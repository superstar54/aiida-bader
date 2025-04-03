import pathlib

file_path = pathlib.Path(__file__).parent
structure_examples = {
    "title": "Bader charge",
    "structures": [
        ("PtO", file_path / "PtO.cif"),
        ("PtO₂", file_path / "PtO2.cif"),
    ],
}
