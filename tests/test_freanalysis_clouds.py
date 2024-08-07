from ftplib import FTP
from os import chdir, environ
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

from freanalysis.plugins import list_plugins, plugin_requirements, run_plugin
from scripts import gen_intake_gfdl


def download_test_data(stem):
    """Downloads test datasets from a FTP server.

    Args:
        stem: Directory to create the directory tree inside.

    Returns:
        Path to the directory that will be used as the root of the data catalog.
    """
    # Create local directory tree with the appropriate directory structure.
    catalog_root = Path(stem) / "archive" / "oar.gfdl.mdtf" / "MDTF-examples" / \
                   "mdtf-time-slice-example" / "gfdl.ncrc5-deploy-prod-openmp" / "pp"
    data_directory = catalog_root / "atmos" / "ts" / "monthly" / "1yr"
    data_directory.mkdir(parents=True, exist_ok=True)

    # Download the datasets from the FTP server.
    path = "1/oar.gfdl.mdtf/MDTF-examples/GFDL-CM4/data/atmos/ts/monthly/1yr"
    with FTP("nomads.gfdl.noaa.gov") as ftp:
        ftp.login()
        ftp.cwd(path)
        for variable in ["high_cld_amt", "mid_cld_amt", "low_cld_amt"]:
            name = f"atmos.198001-198012.{variable}.nc"
            ftp.retrbinary(f"RETR {name}", open(data_directory / name, "wb").write)
    return catalog_root.resolve()


def create_data_catalog(path, output="data-catalog"):
    """Creates a data catalog from a directory tree.

    Args:
        path: Path to the catalog root.
        output: Name of the data catalog that will be created.

    Returns:
        Paths to the data catalog json and csv files.
    """
    yaml_path = Path(__file__).resolve().parent / "mdtf_timeslice_catalog.yaml"

    # Hack to stop click from exiting.
    command = ["python3", "-m", "scripts.gen_intake_gfdl", str(path), output,
               "--config", str(yaml_path)]
    run(command, check=True)
    return Path(f"{output}.json").resolve(), Path(f"{output}.csv").resolve()


def plugin(json, pngs_directory="pngs"):
    """Run the plugin to create the figure.

    Args:
        json: Path to the catalog json file.
        pngs_directory: Directory to store the output in.
    """
    name = "freanalysis_clouds"
    reqs = plugin_requirements(name)
    Path(pngs_directory).mkdir(parents=True, exist_ok=True)
    run_plugin(name, json, pngs_directory)


def test_freanalysis_clouds():
    with TemporaryDirectory() as tmp:
        chdir(Path(tmp))
        path = download_test_data(stem=tmp)
        json, csv = create_data_catalog(path)
        plugin(json)
