# -*- coding: utf-8 -*-
"""Cp2kBaderWorkGraph of the AiiDA bader plugin"""

from aiida_workgraph import WorkGraph


def Cp2kBaderWorkGraph():
    from aiida_cp2k.workchains.base import Cp2kBaseWorkChain
    from aiida_bader.calculations import BaderCalculation

    wt = WorkGraph("charge-density")
    cp2k_node = wt.nodes.new(Cp2kBaseWorkChain, name="scf")
    wt.nodes.new(
        BaderCalculation,
        name="bader",
        charge_density_folder=cp2k_node.outputs["remote_folder"],
    )
    return wt
