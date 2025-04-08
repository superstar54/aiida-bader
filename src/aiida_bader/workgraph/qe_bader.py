# -*- coding: utf-8 -*-
"""QeBaderWorkGraph of the AiiDA bader plugin"""
from aiida import orm
from aiida_workgraph import WorkGraph, task


@task.graph_builder(outputs=[{"name": "charge", "from": "bader.charge"}])
def bader_workgraph(
    structure: orm.StructureData = None,
    pw_code: orm.Code = None,
    pp_code: orm.Code = None,
    bader_code: orm.Code = None,
    kpoints_distance: float = 0.2,
    pseudos: dict = None,
    parameters: dict = None,
    metadata_pw: dict = None,
    metadata_pp: dict = None,
    metadata_bader: dict = None,
):
    """Workgraph for Bader charge analysis.
    1. Run the SCF calculation.
    2. Run the PP calculation for valence charge density.
    3. Run the PP calculation for all-electron charge density.
    4. Run the Bader charge analysis.
    """

    from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
    from aiida_quantumespresso.calculations.pp import PpCalculation
    from aiida_bader.calculations import BaderCalculation

    parameters = {} if parameters is None else parameters.get_dict()
    settings = {}
    kpoints = None
    wg = WorkGraph("BaderCharge")
    # -------- scf -----------
    scf_task = wg.add_task(PwBaseWorkChain, name="scf")

    parameters.setdefault("CONTROL", {})
    parameters["CONTROL"]["calculation"] = "scf"
    # isolated systems
    if structure.pbc == (False, False, False):
        parameters.setdefault("SYSTEM", {})
        parameters["SYSTEM"]["assume_isolated"] = "mt"
        settings = {"gamma_only": True}
        kpoints = orm.KpointsData()
        kpoints.set_kpoints_mesh([1, 1, 1])
        kpoints_distance = None
    scf_inputs = {
        "pw": {
            "structure": structure,
            "parameters": orm.Dict(dict=parameters),
            "code": pw_code,
            "pseudos": pseudos,
            "metadata": metadata_pw,
            "settings": orm.Dict(dict=settings),
        },
        "kpoints_distance": kpoints_distance,
        "kpoints": kpoints,
    }
    scf_task.set(scf_inputs)
    # -------- pp valence -----------
    pp_valence = wg.add_task(
        PpCalculation,
        name="pp_valence",
        code=pp_code,
        parent_folder=scf_task.outputs["remote_folder"],
        parameters=orm.Dict(
            {
                "INPUTPP": {"plot_num": 0},
                "PLOT": {"iflag": 3},
            }
        ),
        metadata=metadata_pp,
    )
    # -------- pp all -----------
    pp_all = wg.add_task(
        PpCalculation,
        name="pp_all",
        code=pp_code,
        parent_folder=scf_task.outputs["remote_folder"],
        parameters=orm.Dict(
            {
                "INPUTPP": {"plot_num": 21},
                "PLOT": {"iflag": 3},
            }
        ),
        metadata=metadata_pp,
    )
    # -------- bader -----------
    bader_task = wg.add_task(
        BaderCalculation,
        name="bader",
        code=bader_code,
        charge_density_folder=pp_valence.outputs["remote_folder"],
        reference_charge_density_folder=pp_all.outputs["remote_folder"],
        metadata=metadata_bader,
    )
    return wg
