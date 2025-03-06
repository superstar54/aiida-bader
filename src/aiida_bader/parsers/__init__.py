# -*- coding: utf-8 -*-
"""AiiDA bader plugin parser"""
from __future__ import absolute_import

import os

from aiida.common import NotExistent, OutputParsingError
from aiida.engine import ExitCode
from aiida.parsers.parser import Parser
from aiida.orm import ArrayData
import numpy as np


class BaderParser(Parser):
    """
    Parser class for parsing output of bader charge analysis.
    """

    # pylint: disable=protected-access
    def parse(self, **kwargs):
        """Parse output structure and charge."""

        # Check that the retrieved folder is there
        try:
            out_folder = self.retrieved
        except NotExistent:
            self.logger.error("No retrieved folder found")
            return self.exit_codes.ERROR_NO_RETRIEVED_FOLDER

        # Check what is inside the folder
        list_of_files = (
            out_folder.base.repository.list_object_names()
        )  # pylint: disable=protected-access

        output_file = self.node.process_class._DEFAULT_OUTPUT_FILE

        # We need at least the output file name as defined in calcs.py
        if output_file not in list_of_files:
            return self.exit_codes.ERROR_NO_OUTPUT_FILE

        finished = False
        with out_folder.open(output_file) as file:
            for line in file.readlines():
                if "NUMBER OF ELECTRONS" in line:
                    finished = True

        if not finished:
            raise OutputParsingError("Calculation did not finish correctly")

        # Create CifData object from the following the file path returned by xyz2cif
        with out_folder.open(output_file) as f:
            lines = f.readlines()
            charges = [float(line.split()[4]) for line in lines[2:-4]]
        array = ArrayData()
        array.set_array("charge", np.array(charges))
        self.out("bader_charge", array)

        return ExitCode(0)
