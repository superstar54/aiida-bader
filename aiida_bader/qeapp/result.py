import ipywidgets as ipw
from aiidalab_qe.common.panel import ResultPanel
from weas_widget import WeasWidget
from .widget import TableWidget


class Result(ResultPanel):
    title = "Bader Charge"
    workchain_labels = ["bader"]

    def __init__(self, node=None, **kwargs):
        super().__init__(node=node, **kwargs)
        self.summary_view = ipw.HTML()
        self.result_table = TableWidget()
        guiConfig = {
            "enabled": True,
            "components": {"atomsControl": True, "buttons": True},
            "buttons": {
                "fullscreen": True,
                "download": True,
                "measurement": True,
            },
        }
        self.structure_view = WeasWidget(guiConfig=guiConfig)
        self.result_table.observe(self._process_row_index, "row_index")
        self.structure_view_ready = False

    def _process_row_index(self, change):
        if change["new"] is not None:
            selected_atoms_indices = [self.result_table.data[change["new"] + 1][0]]
            self.structure_view.avr.selected_atoms_indices = selected_atoms_indices
            # trigger the resize event to update the view
            if not self.structure_view_ready:
                self.structure_view._widget.send_js_task(
                    {"name": "tjs.onWindowResize", "kwargs": {}}
                )
                self.structure_view._widget.send_js_task(
                    {
                        "name": "tjs.updateCameraAndControls",
                        "kwargs": {"direction": [0, -100, 0]},
                    }
                )
                self.structure_view_ready = True

    def _update_view(self):
        self.structure = self.node.inputs.bader.structure
        bader_charge = self.outputs.bader.bader.bader_charge.get_array("charge")
        self._update_structure(self.structure)
        self._generate_table(self.structure, bader_charge)
        table_help = ipw.HTML(
            """
            <div style='margin: 10px 0;'>
                <h4 style='margin-bottom: 5px; color: #3178C6;'>Result</h4>
            </div>
            """,
            layout=ipw.Layout(margin="0 0 20px 0"),  # Adjust the margin as needed
        )
        structure_help = ipw.HTML(
            """
            <div style='margin: 10px 0;'>
                <h4 style='margin-bottom: 5px; color: #3178C6;'>Structure</h4>
                <p style='margin: 5px 0; font-size: 14px;'>
                    Click on the row above to highlight the specific atom for which the Bader charge is being calculated.
                </p>
            </div>
            """,
            layout=ipw.Layout(margin="0 0 20px 0"),  # Adjust the margin as needed
        )
        self.children = [
            ipw.VBox(
                children=[
                    ipw.VBox([table_help, self.result_table]),
                    ipw.VBox([structure_help, self.structure_view]),
                ],
                layout=ipw.Layout(justify_content="space-between", margin="10px"),
            ),
        ]

    def _update_structure(self, structure):
        atoms = structure.get_ase()
        self.structure_view.from_ase(atoms)
        self.structure_view.avr.model_style = 1
        self.structure_view.avr.color_type = "VESTA"
        self.structure_view.avr.atom_label_type = "Index"

    def _generate_table(self, structure, bader_charge):
        # get index and element form AiiDA StructureData
        site_index = [site.kind_name for site in structure.sites]

        # Start of the HTML string for the table
        data = [["Site Index", "Element", "Bader Charge"]]
        # Add rows to the table based on the bader_charge
        for i in range(len(site_index)):
            charge = round(bader_charge[i], 2)
            data.append([i, site_index[i], charge])
        self.result_table.data = data
