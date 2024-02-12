from dataclasses import dataclass
import json
from pathlib import Path

from analysis_scripts import AnalysisScript
from figure_tools import Figure, LonLatMap
import intake
import intake_esm


@dataclass
class Metadata:
    activity_id: str = "dev"
    institution_id: str = ""
    source_id: str = ""
    experiment_id: str = "c96L65_am5f4b4r1-newrad_amip"
    frequency: str = "monthly"
    modeling_realm: str = "atmos"
    table_id: str = ""
    member_id: str = "na"
    grid_label: str = ""
    temporal_subset: str = ""
    chunk_freq: str = ""
    platform: str = ""
    cell_methods: str = ""

    def catalog_search_args(self, name):
        return {
            "experiment_id": self.experiment_id,
            "frequency": self.frequency,
            "member_id": self.member_id,
            "modeling_realm": self.modeling_realm,
            "variable_id": name,
        }

    def catalog_key(self, name) -> str:
        return ".".join([
            self.experiment_id,
            self.frequency,
            self.member_id,
            self.modeling_realm,
            name,
        ])

    def variables(self):
        return {
            "high_cloud_fraction": "high_cld_amt",
            "low_cloud_fraction": "low_cld_amt",
            "middle_cloud_fraction": "mid_cld_amt",
        }


class AerosolAnalysisScript(AnalysisScript):
    """Aerosol analysis script.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        self.metadata = Metadata()
        self.description = "Calculates cloud metrics."
        self.title = "Cloud Fractions"

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string containing the metadata.
        """
        columns = Metadata.__annotations__.keys()
        settings = {x: getattr(self.metadata, x) for x in columns}
        return json.dumps({
            "settings": settings,
            "dimensions": {
                "lat": {"standard_name": "latitude"},
                "lon": {"standard_name": "longitude"},
                "time": {"standard_name": "time"}
            },
            "varlist": {
                "high_cld_amt": {
                    "standard_name": "high_cloud_fraction",
                    "units": "%",
                    "dimensions": ["time", "lat", "lon"]
                },
                "low_cld_amt": {
                    "standard_name": "low_cloud_fraction",
                    "units": "%",
                    "dimensions": ["time", "lat", "lon"]
                },
                "mid_cld_amt": {
                    "standard_name": "middle_cloud_fraction",
                    "units": "%",
                    "dimensions": ["time", "lat", "lon"]
                },
            },
        })

    def run_analysis(self, catalog, png_dir, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a catalog.
            png_dir: Path to the directory where the figures will be made.
            reference_catalog: Path to a catalog of reference data.

        Returns:
            A list of paths to the figures that were created.
        """

        # Connect to the catalog and find the necessary datasets.
        catalog = intake.open_esm_datastore(catalog)

        maps = {}
        for name, variable in self.metadata.variables().items():
            # Get the dataset out of the catalog.
            args = self.metadata.catalog_search_args(variable)

            datasets = catalog.search(
                **self.metadata.catalog_search_args(variable)
            ).to_dataset_dict(progressbar=False)

            # Lon-lat maps.
            maps[name] = LonLatMap.from_xarray_dataset(
                datasets[self.metadata.catalog_key(variable)],
                variable,
                time_method="annual mean",
                year=2010,
            )

        figure = Figure(num_rows=3, num_columns=1, title="Cloud Fraction", size=(16, 10))
        figure.add_map(maps["high_cloud_fraction"], "High Clouds", 1, colorbar_range= [0, 100])
        figure.add_map(maps["middle_cloud_fraction"], "Middle Clouds", 2, colorbar_range=[0, 100])
        figure.add_map(maps["low_cloud_fraction"], "Low Clouds", 3, colorbar_range=[0, 100])
        figure.save(Path(png_dir) / "cloud-fraction.png")
        return [Path(png_dir) / "cloud-fraction.png",]
