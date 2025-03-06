"""
BaderResultsPanel: Renders the Bader Charge results using the BaderResultsModel.
"""
import ipywidgets as ipw
from aiidalab_qe.common.panel import ResultsPanel
from weas_widget import WeasWidget
from .model import BaderResultsModel
from table_widget import TableWidget  # Your custom TableWidget
from aiidalab_qe.common.infobox import InAppGuide


class BaderResultsPanel(ResultsPanel[BaderResultsModel]):
    """Panel (View + Controller) for displaying the Bader charge results."""

    def _render(self):
        """"""
        self._model.fetch_result()
        self.result_table = TableWidget()
        self._populate_table()

        gui_config = {
            "components": {"enabled": True, "atomsControl": True, "buttons": True},
            "buttons": {
                "enabled": True,
                "fullscreen": True,
                "download": True,
                "measurement": True,
            },
        }
        self.structure_view = WeasWidget(guiConfig=gui_config)
        self._setup_structure_view()

        self.result_table.observe(self._on_row_index_change, "selectedRowId")

        self.children = [
            InAppGuide(identifier="bader-charge-results"),
            self._create_layout(),
        ]

    def _populate_table(self):
        columns = [
            {"field": "site_index", "headerName": "Site Index", "editable": False},
            {"field": "element", "headerName": "Element", "editable": False},
            {"field": "bader_charge", "headerName": "Bader Charge", "editable": False},
            {
                "field": "charge_diff",
                "headerName": "Bader charge difference",
                "editable": False,
                "width": 200,
            },
        ]
        data = []

        for i, site in enumerate(self._model.structure.sites):
            charge = self._model.bader_charges[i]
            kind_name = site.kind_name
            if kind_name in self._model.z_valencces:
                z_valence = self._model.z_valencces[kind_name]
                charge_diff = z_valence - charge
            else:
                charge_diff = None
            data.append(
                {
                    "site_index": i,
                    "element": kind_name,
                    "bader_charge": round(charge, 3),
                    "charge_diff": round(charge_diff, 3)
                    if charge_diff is not None
                    else None,
                }
            )

        self.result_table.from_data(
            data,
            columns=columns,
        )

    def _setup_structure_view(self):
        if self._model.structure:
            ase_atoms = self._model.structure.get_ase()
            self.structure_view.from_ase(ase_atoms)
            self.structure_view.avr.model_style = 1
            self.structure_view.avr.color_type = "VESTA"
            self.structure_view.avr.atom_label_type = "Index"

    def _on_row_index_change(self, change):
        if change["new"] is not None:
            row_index = int(change["new"])
            # The first row is the header, so we do +1 offset.
            site_idx = self.result_table.data[row_index]["site_index"]
            self.structure_view.avr.selected_atoms_indices = [site_idx]

    def _create_layout(self):
        structure_help = ipw.HTML(
            """
            <div style='margin: 10px 0;'>
                <h4 style='margin-bottom: 5px; color: #3178C6;'>Structure</h4>
            </div>
            """,
            layout=ipw.Layout(margin="0 0 20px 0"),
        )

        table_help = ipw.HTML(
            """
            <div style='margin: 10px 0;'>
                <h4 style='margin-bottom: 5px; color: #3178C6;'>Result</h4>
                <p style='margin: 5px 0; font-size: 14px;'>
                    Click on the row to highlight the specific atom for which the Bader charge is being calculated.
                </p>
            </div>
            """,
            layout=ipw.Layout(margin="0 0 20px 0"),
        )

        return ipw.HBox(
            children=[
                ipw.VBox([table_help, self.result_table]),
                ipw.VBox([structure_help, self.structure_view]),
            ],
            layout=ipw.Layout(justify_content="space-between", margin="10px"),
        )
