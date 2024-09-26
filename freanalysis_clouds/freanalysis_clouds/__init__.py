from dataclasses import dataclass
import json
from pathlib import Path

from analysis_scripts import AnalysisScript
from figure_tools import Figure, LonLatMap
import intake


@dataclass
class Metadata:
    """Helper class that stores the metadata needed by the plugin."""
    frequency: str = "monthly"
    realm: str = "atmos"

    @staticmethod
    def variables():
        """Helper function to make maintaining this script easier if the
           catalog variable ids change.

        Returns:
            Dictionary mapping the names used in this script to the catalog
            variable ids.
        """
        return {
            "high_cloud_fraction": "high_cld_amt",
            "low_cloud_fraction": "low_cld_amt",
            "middle_cloud_fraction": "mid_cld_amt",
        }


class CloudAnalysisScript(AnalysisScript):
    """Cloud analysis script.

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

    def run_analysis(self, catalog, png_dir, reference_catalog=None, config={}):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a catalog.
            png_dir: Path to the directory where the figures will be made.
            reference_catalog: Path to a catalog of reference data.
            config: Dictonary of catalog metadata.  Will overwrite the
                    data defined in the Metadata helper class if they both
                    contain the same keys.

        Returns:
            A list of paths to the figures that were created.

        Raises:
            ValueError if the catalog cannot be filtered correctly.
        """

        # Connect to the catalog.
        catalog = intake.open_esm_datastore(catalog)

        maps = {}
        for name, variable in self.metadata.variables().items():
            # Filter the catalog down to a single dataset for each variable.
            query_params = {"variable_id": variable}
            query_params.update(vars(self.metadata))
            query_params.update(config)
            datasets = catalog.search(**query_params).to_dataset_dict(progressbar=False)
            if len(list(datasets.values())) != 1:
                raise ValueError("could not filter the catalog down to a single dataset.", datasets)
            dataset = list(datasets.values())[0]

            # Create Lon-lat maps.
            maps[name] = LonLatMap.from_xarray_dataset(dataset, variable, year=1980,
                                                       time_method="annual mean")

        # Create the figure.
        figure = Figure(num_rows=3, num_columns=1, title="Cloud Fraction", size=(16, 10))
        figure.add_map(maps["high_cloud_fraction"], "High Clouds", 1, colorbar_range= [0, 100])
        figure.add_map(maps["middle_cloud_fraction"], "Middle Clouds", 2, colorbar_range=[0, 100])
        figure.add_map(maps["low_cloud_fraction"], "Low Clouds", 3, colorbar_range=[0, 100])
        output = Path(png_dir) / "cloud-fraction.png"
        figure.save(output)
        return [output,]
