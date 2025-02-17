# -*- coding: utf-8 -*-
"""QeBaderWorkChain workchain of the AiiDA bader plugin"""

from __future__ import absolute_import

from aiida.common import AttributeDict
from aiida.engine import ToContext, WorkChain
from aiida.plugins import CalculationFactory, WorkflowFactory
from aiida_quantumespresso.common.types import ElectronicType, RestartType, SpinType
from aiida import orm
from aiida_quantumespresso.workflows.protocols.utils import ProtocolMixin
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_bader.calculations import BaderCalculation

PpCalculation = CalculationFactory("quantumespresso.pp")  # pylint: disable=invalid-name


class QeBaderWorkChain(ProtocolMixin, WorkChain):
    """A workchain that computes bader charges using QE and Bader code."""

    @classmethod
    def define(cls, spec):
        """Define workflow specification."""
        super(QeBaderWorkChain, cls).define(spec)

        spec.input(
            "structure", valid_type=orm.StructureData, help="The input structure."
        )
        spec.expose_inputs(
            PwBaseWorkChain,
            namespace="scf",
            exclude=("clean_workdir", "pw.structure", "pw.parent_folder"),
            namespace_options={
                "help": "Inputs for the `PwBaseWorkChain` of the `scf` calculation.",
                "required": False,
                "populate_defaults": False,
            },
        )
        spec.expose_inputs(
            PpCalculation, namespace="pp_valence", exclude=["parent_folder"]
        )
        spec.expose_inputs(PpCalculation, namespace="pp_all", exclude=["parent_folder"])
        spec.expose_inputs(
            BaderCalculation,
            namespace="bader",
            exclude=["charge_density_folder", "reference_charge_density_folder"],
        )

        spec.outline(
            cls.run_pw,
            cls.run_pp,
            cls.run_bader,
            cls.return_results,
        )

        spec.expose_outputs(PwBaseWorkChain, namespace="scf")
        spec.expose_outputs(PpCalculation, namespace="pp_valence")
        spec.expose_outputs(PpCalculation, namespace="pp_all")
        spec.expose_outputs(BaderCalculation, namespace="bader")

        spec.exit_code(903, "ERROR_PARSING_PW_OUTPUT", "Error while parsing PW output")
        spec.exit_code(
            904,
            "ERROR_PARSING_PP_VALENCE_OUTPUT",
            "Error while parsing PP_VALENCE output",
        )
        spec.exit_code(
            905, "ERROR_PARSING_PP_ALL_OUTPUT", "Error while parsing PP_ALL output"
        )
        spec.exit_code(
            906, "ERROR_PARSING_BADER_OUTPUT", "Error while parsing bader output"
        )

    @classmethod
    def get_protocol_filepath(cls):
        """Return ``pathlib.Path`` to the ``.yaml`` file that defines the protocols."""
        from importlib_resources import files

        from . import protocols

        return files(protocols) / "bader.yaml"

    @classmethod
    def get_builder_from_protocol(
        cls,
        pw_code,
        pp_code,
        bader_code,
        structure,
        protocol=None,
        overrides=None,
        options=None,
        **kwargs,
    ):
        """Return a builder prepopulated with inputs selected according to the chosen protocol.

        :param code: the ``Code`` instance configured for the ``quantumespresso.pw`` plugin.
        :param structure: the ``StructureData`` instance to use.
        :param protocol: protocol to use, if not specified, the default will be used.
        :param overrides: optional dictionary of inputs to override the defaults of the protocol.
        """
        from aiida_quantumespresso.workflows.protocols.utils import recursive_merge

        inputs = cls.get_protocol_inputs(protocol, overrides)

        if isinstance(pw_code, str):
            pw_code = orm.load_code(pw_code)
        if isinstance(bader_code, str):
            bader_code = orm.load_code(bader_code)

        scf = PwBaseWorkChain.get_builder_from_protocol(
            pw_code,
            structure,
            protocol,
            overrides=inputs.get("scf", None),
            options=options,
            **kwargs,
        )
        scf["pw"].pop("structure", None)

        metadata_pp_valence = inputs.get("pp_valence", {}).get(
            "metadata", {"options": {}}
        )
        metadata_pp_all = inputs.get("pp_all", {}).get("metadata", {"options": {}})
        metadata_bader = inputs.get("bader", {}).get("metadata", {"options": {}})

        if options:
            metadata_pp_valence["options"] = recursive_merge(
                metadata_pp_valence["options"], options
            )
            metadata_pp_all["options"] = recursive_merge(
                metadata_pp_all["options"], options
            )
            metadata_bader["options"] = recursive_merge(
                metadata_bader["options"], options
            )

        builder = cls.get_builder()
        builder.structure = structure
        builder.scf = scf
        builder.pp_valence.code = pp_code  # pylint: disable=no-member
        builder.pp_valence.parameters = orm.Dict(
            inputs.get("pp_valence", {}).get("parameters")
        )  # pylint: disable=no-member
        builder.pp_valence.metadata = metadata_pp_valence  # pylint: disable=no-member
        #
        builder.pp_all.code = pp_code  # pylint: disable=no-member
        builder.pp_all.parameters = orm.Dict(
            inputs.get("pp_all", {}).get("parameters")
        )  # pylint: disable=no-member
        builder.pp_all.metadata = metadata_pp_all  # pylint: disable=no-member
        builder.bader.code = bader_code  # pylint: disable=no-member
        builder.bader.parameters = orm.Dict(
            inputs.get("bader", {}).get("parameters")
        )  # pylint: disable=no-member
        builder.bader.metadata = metadata_bader  # pylint: disable=no-member

        return builder

    def run_pw(self):
        """Run PW."""
        scf_inputs = AttributeDict(self.exposed_inputs(PwBaseWorkChain, "scf"))
        scf_inputs.pw.structure = self.inputs.structure
        scf_inputs["metadata"]["label"] = "pw_scf"
        scf_inputs["metadata"]["call_link_label"] = "call_pw_scf"
        running = self.submit(PwBaseWorkChain, **scf_inputs)
        self.report("Running PwBaseWorkChain.")
        return ToContext(pw_calc=running)

    def run_pp(self):
        """Run PP to generate the charge-density."""
        # TODO extract number of core electrons from the pw pseudopotential

        try:
            pp_valence_inputs = AttributeDict(
                self.exposed_inputs(PpCalculation, "pp_valence")
            )
            pp_valence_inputs["parent_folder"] = self.ctx.pw_calc.outputs.remote_folder
            pp_all_inputs = AttributeDict(self.exposed_inputs(PpCalculation, "pp_all"))
            pp_all_inputs["parent_folder"] = self.ctx.pw_calc.outputs.remote_folder
        except Exception as exc:  # pylint: disable=broad-except
            self.report(f'Encountered exception "{str(exc)}" while parsing PW output')
            return self.exit_codes.ERROR_PARSING_PW_OUTPUT  # pylint: disable=no-member

        pp_valence_inputs["metadata"]["call_link_label"] = "call_pp_valence_calc"
        pp_all_inputs["metadata"]["call_link_label"] = "call_pp_all_calc"

        # Create the calculation process and launch it
        pp_valence_running = self.submit(PpCalculation, **pp_valence_inputs)
        pp_all_running = self.submit(PpCalculation, **pp_all_inputs)
        self.report(
            f"Running PpCalculation<{pp_valence_running.pk}> to compute the valence charge-density"
        )
        self.report(
            f"Running PpCalculation<{pp_all_running.pk}> to compute the all-electron charge-density"
        )
        return ToContext(pp_valence_calc=pp_valence_running, pp_all_calc=pp_all_running)

    def run_bader(self):
        """Parse the PP ouputs cube file, and submit bader calculation."""
        try:
            bader_inputs = AttributeDict(self.exposed_inputs(BaderCalculation, "bader"))
            bader_inputs[
                "charge_density_folder"
            ] = self.ctx.pp_valence_calc.outputs.remote_folder
            bader_inputs[
                "reference_charge_density_folder"
            ] = self.ctx.pp_all_calc.outputs.remote_folder
        except Exception as exc:  # pylint: disable=broad-except
            self.report(f'Encountered exception "{str(exc)}" while parsing PP output')
            return self.exit_codes.ERROR_PARSING_PP_OUTPUT  # pylint: disable=no-member

        bader_inputs["metadata"]["call_link_label"] = "call_bader_calc"

        # Create the calculation process and launch it
        running = self.submit(BaderCalculation, **bader_inputs)
        self.report(
            f"Running BaderCalculation<{running.pk}> to compute point charges from the charge-density"
        )
        return ToContext(bader_calc=running)

    def return_results(self):
        """Return exposed outputs and print the pk of the ArrayData w/bader"""
        try:
            self.out_many(
                self.exposed_outputs(self.ctx.pw_calc, PwBaseWorkChain, namespace="scf")
            )
            self.out_many(
                self.exposed_outputs(
                    self.ctx.pp_valence_calc, PpCalculation, namespace="pp_valence"
                )
            )
            self.out_many(
                self.exposed_outputs(
                    self.ctx.pp_all_calc, PpCalculation, namespace="pp_all"
                )
            )
            self.out_many(
                self.exposed_outputs(
                    self.ctx.bader_calc, BaderCalculation, namespace="bader"
                )
            )
            self.report(
                f"bader charges computed: ArrayData<{self.outputs['bader']['bader_charge'].pk}>"
            )
        except KeyError:
            return (
                self.exit_codes.ERROR_PARSING_BADER_OUTPUT
            )  # pylint: disable=no-member

        return 0
