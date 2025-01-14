from dataclasses import dataclass
import json
from pathlib import Path

from analysis_scripts import AnalysisScript
from figure_tools import LonLatMap, zonal_mean_vertical_and_column_integrated_map, \
                         ZonalMeanMap
import intake


@dataclass
class Metadata:
    """Helper class that stores the metadata needed by the plugin."""
    frequency: str = "mon"
    realm: str = "atmos_month_aer"

    @staticmethod
    def variables():
        """Helper function to make maintaining this script easier if the
           catalog variable ids change.

        Returns:
            Dictionary mapping the names used in this script to the catalog
            variable ids.
        """
        return {
            "black_carbon": "blk_crb",
            "black_carbon_column": "blk_crb_col",
            "large_dust": "lg_dust",
            "large_dust_column": "lg_dust_col",
            "small_dust": "sm_dust",
            "small_dust_column": "sm_dust_col",
            "organic_carbon": "org_crb",
            "organic_carbon_column": "org_crb_col",
            "large_seasalt": "lg_ssalt",
            "large_seasalt_column": "lg_ssalt_col",
            "small_seasalt": "sm_ssalt",
            "small_seasalt_column": "sm_ssalt_col",
            "seasalt": "salt",
            "seasalt_column": "salt_col",
            "sulfate": "sulfate",
            "sulfate_column": "sulfate_col",
        }


class AerosolAnalysisScript(AnalysisScript):
    """Aerosol analysis script.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        self.metadata = Metadata()
        self.description = "Calculates aerosol mass metrics."
        self.title = "Aerosol Masses"

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
                "pfull": {"standard_name": "air_pressure"},
                "time": {"standard_name": "time"}
            },
            "varlist": {
                "blk_crb": {
                    "standard_name": "black_carbon_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "blk_crb_col": {
                    "standard_name": "column_integrated_black_carbon_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lg_dust": {
                    "standard_name": "large_dust_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "lg_dust_col": {
                    "standard_name": "column_integrated_large_dust_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lg_ssalt": {
                    "standard_name": "large_seasalt_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "lg_ssalt_col": {
                    "standard_name": "column_integrated_large_ssalt_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "org_crb": {
                    "standard_name": "organic_carbon_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "org_crb_col": {
                    "standard_name": "column_integrated_organic_carbon_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "salt": {
                    "standard_name": "seasalt_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "salt_col": {
                    "standard_name": "column_integrated_seasalt_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "sm_dust": {
                    "standard_name": "small_dust_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "sm_dust_col": {
                    "standard_name": "column_integrated_small_dust_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "sm_ssalt": {
                    "standard_name": "small_seasalt_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "sm_ssalt_col": {
                    "standard_name": "column_integrated_small_ssalt_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "sulfate": {
                    "standard_name": "sulfate_mass",
                    "units": "kg m-3",
                    "dimensions": ["time", "pfull", "lat", "lon"]
                },
                "sulfate_col": {
                    "standard_name": "column_integrated_sulfate_mass",
                    "units": "kg m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
            },
        })

    def run_analysis(self, catalog, png_dir, config=None, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a catalog.
            png_dir: Path to the directory where the figures will be made.
            reference_catalog: Path to a catalog of reference data.
            config: Dictionary of catalog metadata.  Will overwrite the
                    data defined in the Metadata helper class if they both
                    contain the same keys.

        Returns:
            A list of paths to the figures that were created.

        Raises:
            ValueError if the catalog cannot be filtered correctly.
        """

        # Connect to the catalog and find the necessary datasets.
        catalog = intake.open_esm_datastore(catalog)

        maps = {}
        for name, variable in self.metadata.variables().items():
            print(f"Working on variable {name}")
            # Filter the catalog down to a single dataset for each variable.
            query_params = {"variable_id": variable}
            query_params.update(vars(self.metadata))
            if config:
                query_params.update(config)
            datasets = catalog.search(**query_params).to_dataset_dict(progressbar=False)
            if len(list(datasets.values())) != 1:
                print(variable, datasets)
                raise ValueError("could not filter the catalog down to a single dataset.")
            dataset = list(datasets.values())[0]

            if name.endswith("column"):
                # Lon-lat maps.
                maps[name] = LonLatMap.from_xarray_dataset(dataset, variable, year=1980,
                                                           time_method="annual mean")
            else:
                maps[name] = ZonalMeanMap.from_xarray_dataset(dataset, variable, year=1980,
                                                              time_method="annual mean",
                                                              invert_y_axis=True)

        figure_paths = []
        for name in self.metadata.variables().keys():
            if name.endswith("column"): continue
            figure = zonal_mean_vertical_and_column_integrated_map(
                maps[name],
                maps[f"{name}_column"],
                f"{name.replace('_', ' ')} Mass",
            )
            figure.save(Path(png_dir) / f"{name}.png")
            figure_paths.append(Path(png_dir)/ f"{name}.png")
        return figure_paths
