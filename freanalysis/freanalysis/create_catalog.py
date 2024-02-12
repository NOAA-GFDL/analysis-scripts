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
    """Creates a catalog csv file.

    Args:
        pp_dir: Path to the base of a FRE post-process directory tree.
        output_path: Path to the output file.
    """
    with open(output_path, "w") as output:
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
