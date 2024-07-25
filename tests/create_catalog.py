from catalogbuilder.scripts import gen_intake_gfdl
import sys

def create_catalog(yaml, output="data-catalog"):
    """Creates a data catalog from a config file

    Args:
        yaml: YAML config file (e.g. mdtf_timeslice_catalog.yaml)
        output: (prefix)Name of the data catalog that will be created.

    Returns:
        Paths to the data catalog json and csv files.
    """
    yaml_path = Path(__file__).resolve().parent / "mdtf_timeslice_catalog.yaml"
    return Path(f"{output}.json").resolve(), Path(f"{output}.csv").resolve()
  
    sys.argv = ['input_path','--config', yaml_path]
    print(sys.argv)
    gen_intake_gfdl.main()
    return Path(f"{output}.json").resolve(), Path(f"{output}.csv").resolve()
