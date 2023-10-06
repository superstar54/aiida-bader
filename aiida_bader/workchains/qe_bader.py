# -*- coding: utf-8 -*-
"""QeBaderWorkChain workchain of the AiiDA bader plugin"""

from __future__ import absolute_import

from aiida.common import AttributeDict
from aiida.engine import ToContext, WorkChain
from aiida.plugins import CalculationFactory, WorkflowFactory


PwBaseWorkChain = WorkflowFactory(
    "quantumespresso.pw.base"
)  # pylint: disable=invalid-name
PpCalculation = CalculationFactory("quantumespresso.pp")  # pylint: disable=invalid-name
BaderCalculation = CalculationFactory("bader")  # pylint: disable=invalid-name


class QeBaderWorkChain(WorkChain):
    """A workchain that computes bader charges using QE and Bader code."""

    @classmethod
    def define(cls, spec):
        """Define workflow specification."""
        super(QeBaderWorkChain, cls).define(spec)

        spec.expose_inputs(PwBaseWorkChain, namespace="pw_base")
        spec.expose_inputs(PpCalculation, namespace="pp", exclude=["parent_folder"])
        spec.expose_inputs(
            BaderCalculation, namespace="bader", exclude=["charge_density_folder"]
        )

        spec.outline(cls.run_pw, cls.run_pp, cls.run_bader, cls.return_results)

        spec.expose_outputs(PwBaseWorkChain, namespace="pw_base")
        spec.expose_outputs(PpCalculation, namespace="pp")
        spec.expose_outputs(BaderCalculation, namespace="bader")

        spec.exit_code(903, "ERROR_PARSING_PW_OUTPUT", "Error while parsing PW output")
        spec.exit_code(904, "ERROR_PARSING_PP_OUTPUT", "Error while parsing PP output")
        spec.exit_code(
            905, "ERROR_PARSING_BADER_OUTPUT", "Error while parsing bader output"
        )

    def run_pw(self):
        """Run PW."""
        pw_base_inputs = AttributeDict(self.exposed_inputs(PwBaseWorkChain, "pw_base"))
        pw_base_inputs["metadata"]["label"] = "pw_scf"
        pw_base_inputs["metadata"]["call_link_label"] = "call_pw_scf"
        running = self.submit(PwBaseWorkChain, **pw_base_inputs)
        self.report("Running PwBaseWorkChain.")
        return ToContext(pw_calc=running)

    def run_pp(self):
        """Run PP to generate the charge-density."""
        # TODO extract number of core electrons from the pw pseudopotential

        try:
            pp_inputs = AttributeDict(self.exposed_inputs(PpCalculation, "pp"))
            pp_inputs["parent_folder"] = self.ctx.pw_calc.outputs.remote_folder
        except Exception as exc:  # pylint: disable=broad-except
            self.report(f'Encountered exception "{str(exc)}" while parsing PW output')
            return self.exit_codes.ERROR_PARSING_PW_OUTPUT  # pylint: disable=no-member

        pp_inputs["metadata"]["call_link_label"] = "call_pp_calc"

        # Create the calculation process and launch it
        running = self.submit(PpCalculation, **pp_inputs)
        self.report(
            f"Running PpCalculation<{running.pk}> to compute the charge-density"
        )
        return ToContext(pp_calc=running)

    def run_bader(self):
        """Parse the PP ouputs cube file, and submit bader calculation."""
        try:
            bader_inputs = AttributeDict(self.exposed_inputs(BaderCalculation, "bader"))
            bader_inputs[
                "charge_density_folder"
            ] = self.ctx.pp_calc.outputs.remote_folder
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
                self.exposed_outputs(
                    self.ctx.pw_calc, PwBaseWorkChain, namespace="pw_base"
                )
            )
            self.out_many(
                self.exposed_outputs(self.ctx.pp_calc, PpCalculation, namespace="pp")
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
