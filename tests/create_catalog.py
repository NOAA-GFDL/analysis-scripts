from pathlib import Path
from catalogbuilder.scripts import gen_intake_gfdl
import sys

def create_catalog(path, yaml_path, output="/home/runner/work/analysis-scripts-fork/data-catalog"):
    """Creates a data catalog from a config file

    Args:
        path: Location of data
        yaml: YAML config file (e.g. mdtf_timeslice_catalog.yaml)
        output: (prefix)Name of the data catalog that will be created.

    Returns:
        Paths to the data catalog json and csv files.
    """
    print(yaml_path)
    print(path)
    sys.argv = ['str(path)','--config', yaml_path]
    print(sys.argv)
    try:
      gen_intake_gfdl.main()
    except:
      print("Exception occured running gen_intake_gfdl")
    print("test")
    
    return Path(f"{output}.json").resolve(), Path(f"{output}.csv").resolve()
