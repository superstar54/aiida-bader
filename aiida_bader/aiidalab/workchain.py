from aiida.plugins import WorkflowFactory
from aiida_quantumespresso.common.types import ElectronicType, SpinType
from aiida import orm

QeBaderWorkChain = WorkflowFactory("bader.qe")


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


def get_builder(codes, structure, parameters, **kwargs):
    from copy import deepcopy

    pw_code = codes.get("pw")
    pp_code = codes.get("pp")
    bader_code = codes.get("bader")
    check_codes(pw_code, pp_code, bader_code)
    protocol = parameters["workchain"]["protocol"]

    scf_overrides = deepcopy(parameters["advanced"])

    overrides = {
        "scf": scf_overrides,
        "pp": {
            "parameters": orm.Dict(
                {
                    "INPUTPP": {"plot_num": 21},
                    "PLOT": {"iflag": 3},
                }
            ),
            "metadata": {
                "options": {
                    "resources": {
                        "num_machines": 1,
                        "num_mpiprocs_per_machine": 1,
                    },
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
    return builder


workchain_and_builder = {
    "workchain": QeBaderWorkChain,
    "exclude": ("clean_workdir", "structure", "relax"),
    "get_builder": get_builder,
}
