# -*- coding: utf-8 -*-
"""QeBaderWorkTree of the AiiDA bader plugin"""

from aiida_worktree import build_node, WorkTree


def QeBaderWorkTree():
    # register node
    pw_node = build_node(
        {"path": "aiida_quantumespresso.workflows.pw.base.PwBaseWorkChain"}
    )
    pp_node = build_node(
        {"path": "aiida_quantumespresso.calculations.pp.PpCalculation"}
    )
    bader_node = build_node({"path": "aiida_bader.calculations.BaderCalculation"})
    # create worktree
    wt = WorkTree("charge-density")
    pw_node = wt.nodes.new(pw_node, name="pw_base")
    pp_node = wt.nodes.new(pp_node, name="pp")
    bader_node = wt.nodes.new(bader_node, name="bader")
    wt.links.new(pw_node.outputs["remote_folder"], pp_node.inputs["parent_folder"])
    wt.links.new(
        pp_node.outputs["remote_folder"], bader_node.inputs["charge_density_folder"]
    )
    # export worktree
    return wt
