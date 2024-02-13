from pathlib import Path


# Catalog column names.
columns = [
    "activity_id",
    "institution_id",
    "source_id",
    "experiment_id",
    "frequency",
    "modeling_realm",
    "table_id",
    "member_id",
    "grid_label",
    "variable_id",
    "temporal_subset",
    "chunk_freq",
    "platform",
    "cell_methods",
    "path",
]


def create_catalog(pp_dir, output_path):
    """Creates a catalog json.

    Args:
        pp_dir: Path to the base of a FRE post-process directory tree.
        output_path: Path to the output file.
    """
    parent_dir = Path(output_path).parent
    csv_path = parent_dir / f"{Path(output_path).stem}.csv"
    with open(output_path, "w") as output:
        json_str = {
            "esmcat_version": "0.0.1",
            "attributes": [
                {"column_name": "activity_id", "vocabulary": ""},
                {"column_name": "institution_id", "vocabulary": ""},
                {"column_name": "source_id", "vocabulary": ""},
                {"column_name": "experiment_id", "vocabulary": ""},
                {"column_name": "frequency", "vocabulary": ""},
                {"column_name": "modeling_realm", "vocabulary": ""},
                {"column_name": "table_id", "vocabulary": ""},
                {"column_name": "member_id", "vocabulary": ""},
                {"column_name": "grid_label", "vocabulary": ""},
                {"column_name": "variable_id", "vocabulary": ""},
                {"column_name": "temporal_subset", "vocabulary": ""},
                {"column_name": "chunk_freq", "vocabulary": ""},
                {"column_name": "platform", "vocabulary": ""},
                {"column_name": "cell_methods", "vocabulary": ""},
                {"column_name": "path", "vocabulary": ""}
            ],
            "assets": {"column_name": "path", "format": "netcdf","format_column_name": null},
            "aggregation_control": {
                "variable_column_name": "variable_id",
                "groupby_attrs": [
                    "source_id",
                    "experiment_id",
                    "frequency",
                    "member_id",
                    "modeling_realm",
                    "variable_id",
                    "chunk_freq"
                ],
                "aggregations": [
                    {"type": "union", "attribute_name": "variable_id", "options": {}},
                    {
                        "type": "join_existing",
                        "attribute_name": "temporal_subset",
                        "options": {
                            "dim": "time",
                            "coords": "minimal",
                            "compat": "override"
                        }
                    }
                ]
            },
            "id": "",
            "description": null,
            "title": null,
            "last_updated": "",
            "catalog_file": csv_path
        }

    with open(csv_path, "w") as output:
        output.write(",".join(columns) + "\n")
        path = Path(pp_dir)
        for name in path.iterdir():
            realm = name.stem
            if not name.is_dir() or str(name.stem).startswith("."): continue
            full = name / "ts/monthly/1yr"
            for file_ in full.iterdir():
                attrs = {column: "" for column in columns}
                if not str(file_).endswith(".nc"): continue
                attrs["activity_id"] = "dev"
                attrs["experiment_id"] = "c96L65_am5f4b4r1-newrad_amip"
                attrs["modeling_realm"] = realm
                attrs["frequency"] = "monthly"
                attrs["member_id"] = "na"
                attrs["variable_id"] = str(file_.stem).split(".")[-1]
                attrs["path"] = str(file_)
                output.write(",".join([attrs[column] for column in columns]) + "\n")
