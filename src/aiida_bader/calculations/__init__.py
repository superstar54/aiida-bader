# -*- coding: utf-8 -*-
"""AiiDA-bader input plugin"""
from __future__ import absolute_import

import os
from collections import OrderedDict

from aiida.common import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import Dict, RemoteData, StructureData, ArrayData, Str


class BaderCalculation(CalcJob):
    """
    AiiDA plugin for the bader code that performs charge analysis.
    """

    _DEFAULT_OUTPUT_FILE = "ACF.dat"

    @classmethod
    def define(cls, spec):
        """
        Init internal parameters at class load time
        """
        # reuse base class function
        super(BaderCalculation, cls).define(spec)
        spec.input(
            "charge_density_filename",
            valid_type=Str,
            default=lambda: Str("aiida.fileout"),
            required=False,
            help="Name of the charge density file",
        )
        spec.input(
            "charge_density_folder",
            valid_type=RemoteData,
            required=True,
            help="Use a remote folder",
        )
        spec.input(
            "reference_charge_density_folder",
            valid_type=RemoteData,
            required=False,
            help="reference_charge",
        )
        spec.input(
            "reference_charge_density_filename",
            valid_type=Str,
            default=lambda: Str("aiida.fileout"),
            required=False,
            help="Name of the charge density file",
        )
        spec.inputs["metadata"]["options"]["parser_name"].default = "bader.bader"
        spec.inputs["metadata"]["options"]["resources"].default = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 1,
        }
        spec.inputs["metadata"]["options"]["withmpi"].default = False

        #  exit codes
        spec.exit_code(
            100,
            "ERROR_NO_RETRIEVED_FOLDER",
            message="The retrieved folder data node could not be accessed.",
        )
        spec.exit_code(
            101,
            "ERROR_NO_OUTPUT_FILE",
            message="The retrieved folder does not contain an output file.",
        )
        spec.output(
            "bader_charge",
            valid_type=ArrayData,
            required=True,
            help="Bader charges",
        )

    def prepare_for_submission(self, folder):
        """Create the input files from the input nodes passed
         to this instance of the `CalcJob`.

        :param folder: an `aiida.common.folders.Folder` to temporarily write files on disk
        :return: `aiida.common.datastructures.CalcInfo` instance
        """

        # Prepare CalcInfo to be returned to aiida
        calcinfo = CalcInfo()
        calcinfo.uuid = self.uuid
        calcinfo.local_copy_list = []
        calcinfo.remote_copy_list = []
        calcinfo.remote_symlink_list = []
        calcinfo.retrieve_list = [
            self._DEFAULT_OUTPUT_FILE,
        ]

        # Charge-density remote folder
        charge_density_folder = self.inputs.charge_density_folder
        comp_uuid = charge_density_folder.computer.uuid
        remote_path = os.path.join(
            charge_density_folder.get_remote_path(),
            self.inputs.charge_density_filename.value,
        )
        copy_infos = [(comp_uuid, remote_path, "charge_density.cube")]
        if self.inputs.reference_charge_density_folder:
            reference_charge_density_folder = (
                self.inputs.reference_charge_density_folder
            )
            comp_uuid = reference_charge_density_folder.computer.uuid
            remote_path = os.path.join(
                reference_charge_density_folder.get_remote_path(),
                self.inputs.reference_charge_density_filename.value,
            )
            copy_infos.append((comp_uuid, remote_path, "reference_charge_density.cube"))
        for copy_info in copy_infos:
            if (
                self.inputs.code.computer.uuid == copy_info[0]
            ):  # if running on the same computer - make a symlink
                calcinfo.remote_symlink_list.append(copy_info)
            else:  # if not - copy the folder
                self.report(
                    f"Warning: Transferring cube file {charge_density_folder.get_remote_path()} from "
                    + f"computer {charge_density_folder.computer.label} to computer {self.inputs.code.computer.label}. "
                    + "This may put strain on your network."
                )
                calcinfo.remote_copy_list.append(copy_info)

        codeinfo = CodeInfo()
        codeinfo.cmdline_params = ["charge_density.cube"]
        if self.inputs.reference_charge_density_folder:
            codeinfo.cmdline_params.extend(["-ref", "reference_charge_density.cube"])
        codeinfo.code_uuid = self.inputs.code.uuid
        calcinfo.codes_info = [codeinfo]

        return calcinfo
