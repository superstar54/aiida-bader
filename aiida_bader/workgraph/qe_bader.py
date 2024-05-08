# -*- coding: utf-8 -*-
"""QeBaderWorkGraph of the AiiDA bader plugin"""

from aiida_workgraph import WorkGraph


def QeBaderWorkGraph():
    from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
    from aiida_quantumespresso.calculations.pp import PpCalculation
    from aiida_bader.calculations import BaderCalculation

    wg = WorkGraph("charge-density")
    pw_node = wg.nodes.new(PwBaseWorkChain, name="pw_base")
    pp_node = wg.nodes.new(PpCalculation, name="pp", 
                           parent_folder=pw_node.outputs["remote_folder"])
    wg.nodes.new(BaderCalculation, name="bader",
                                charge_density_folder=pp_node.outputs["remote_folder"])
    return wg
