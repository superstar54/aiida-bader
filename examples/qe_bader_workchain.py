from aiida import load_profile
from aiida.orm import Dict, KpointsData, StructureData, load_code, load_group, load_node
from ase.build import molecule
from aiida.plugins import WorkflowFactory
from aiida.engine import submit

QeBaderWorkChain = WorkflowFactory("bader.qe")


load_profile()
# ===============================================================================
# load the codes
pw_code = load_code("pw-7.2@localhost")
pp_code = load_code("pp-7.2@localhost")
bader_code = load_code("bader@localhost")


# create input structure node
h2o = molecule("H2O")
h2o.center(vacuum=3.0)
h2o.pbc = True
structure = StructureData(ase=h2o)


overrides = {
    "pp_valence": {
        "parameters": Dict(
            dict={
                "INPUTPP": {"plot_num": 21},
                "PLOT": {"iflag": 3},
            }
        ),
        "metadata": {
            "options": {
                "resources": {
                    "num_machines": 1,
                    "num_mpiprocs_per_machine": 2,
                },
                "max_wallclock_seconds": 3600,
            }
        },
    },
    "pp_all": {
        "parameters": Dict(
            dict={
                "INPUTPP": {"plot_num": 0},
                "PLOT": {"iflag": 3},
            }
        ),
        "metadata": {
            "options": {
                "resources": {
                    "num_machines": 1,
                    "num_mpiprocs_per_machine": 2,
                },
                "max_wallclock_seconds": 3600,
            }
        },
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

builder = QeBaderWorkChain.get_builder_from_protocol(
    pw_code,
    pp_code,
    bader_code,
    structure,
    protocol="fast",
    overrides=overrides,
    options=None,
)

submit(builder)
