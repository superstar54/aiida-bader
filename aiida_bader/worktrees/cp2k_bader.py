# -*- coding: utf-8 -*-
"""Cp2kBaderWorkTree of the AiiDA bader plugin"""

from aiida_worktree import build_node, WorkTree


def Cp2kBaderWorkTree():
    # register node
    cp2k_node = build_node({"path": "aiida_cp2k.workchains.base.Cp2kBaseWorkChain"})
    bader_node = build_node({"path": "aiida_bader.calculations.BaderCalculation"})
    # create worktree
    wt = WorkTree("charge-density")
    cp2k_node = wt.nodes.new(cp2k_node, name="cp2k_base")
    bader_node = wt.nodes.new(bader_node, name="bader")
    wt.links.new(
        cp2k_node.outputs["remote_folder"], bader_node.inputs["charge_density_folder"]
    )
    return wt
