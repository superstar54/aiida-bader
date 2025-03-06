from aiida_quantumespresso.common.types import ElectronicType, SpinType
from aiida import orm
from aiidalab_qe.utils import set_component_resources
from aiida_bader.workchains.qe_bader import QeBaderWorkChain
from aiida_bader.utils import load_pseudos


def check_codes(pw_code, pp_code, bader_code):
    """Check that the codes are installed on the same computer."""
    if (
        not any(
            [
                pw_code is None,
                pp_code is None,
                bader_code is None,
            ]
        )
        and len(
            set(
                (
                    pw_code.computer.pk,
                    pp_code.computer.pk,
                    bader_code.computer.pk,
                )
            )
        )
        != 1
    ):
        raise ValueError(
            "All selected codes must be installed on the same computer. This is because the "
            "Bader calculations rely on large files that are not retrieved by AiiDA."
        )


def update_resources(builder, codes):
    set_component_resources(builder.scf.pw, codes.get("pw"))
    set_component_resources(builder.pp_valence, codes.get("pp"))
    set_component_resources(builder.pp_all, codes.get("pp"))


def get_builder(codes, structure, parameters, **kwargs):
    from copy import deepcopy

    pw_code = codes.get("pw")["code"]
    pp_code = codes.get("pp")["code"]
    bader_code = codes.get("bader")["code"]
    check_codes(pw_code, pp_code, bader_code)
    protocol = parameters["workchain"]["protocol"]

    bader_parameters = parameters.get("bader", {})
    pseudo_group = bader_parameters.pop("pseudo_group")
    pseudos = load_pseudos(structure, pseudo_group)

    scf_overrides = deepcopy(parameters["advanced"])
    scf_overrides["pw"]["pseudos"] = pseudos

    overrides = {
        "scf": scf_overrides,
        "pp_valence": {
            "parameters": orm.Dict(
                {
                    "INPUTPP": {"plot_num": 0},
                    "PLOT": {"iflag": 3},
                }
            ),
        },
        "pp_all": {
            "parameters": orm.Dict(
                {
                    "INPUTPP": {"plot_num": 21},
                    "PLOT": {"iflag": 3},
                }
            ),
        },
        "bader": {
            "metadata": {
                "options": {
                    "withmpi": False,
                    "resources": {
                        "num_machines": 1,
                        "num_mpiprocs_per_machine": 1,
                    },
                    "max_wallclock_seconds": 3600,
                }
            },
        },
    }
    if pp_code is not None and bader_code is not None:
        builder = QeBaderWorkChain.get_builder_from_protocol(
            pw_code=pw_code,
            pp_code=pp_code,
            bader_code=bader_code,
            structure=structure,
            protocol=protocol,
            electronic_type=ElectronicType(parameters["workchain"]["electronic_type"]),
            spin_type=SpinType(parameters["workchain"]["spin_type"]),
            initial_magnetic_moments=parameters["advanced"]["initial_magnetic_moments"],
            overrides=overrides,
            **kwargs,
        )
    else:
        raise ValueError("The pp_code and bader_code are required.")
    # update resources
    update_resources(builder, codes)
    return builder


def update_inputs(inputs, ctx):
    """Update the inputs using context."""
    inputs.structure = ctx.current_structure


workchain_and_builder = {
    "workchain": QeBaderWorkChain,
    "exclude": ("clean_workdir", "structure", "relax"),
    "get_builder": get_builder,
    "update_inputs": update_inputs,
}
