from dataclasses import dataclass
import json
from pathlib import Path

from analysis_scripts import AnalysisScript
from figure_tools import AnomalyTimeSeries, GlobalMeanTimeSeries, LonLatMap, \
                         observation_vs_model_maps, radiation_decomposition, \
                         timeseries_and_anomalies
import intake
import intake_esm
from xarray import open_dataset


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
            "rlds": "lwdn_sfc",
            "rldsaf": "lwdn_sfc_ad",
            "rldscs": "lwdn_sfc_clr",
            "rldscsaf": "lwdn_sfc_ad_clr",
            "rlus": "lwup_sfc",
            "rlusaf": "lwup_sfc_ad",
            "rluscs": "lwup_sfc_clr",
            "rluscsaf": "lwup_sfc_ad_clr",
            "rlut": "olr",
            "rlutaf": "lwtoa_ad",
            "rlutcs": "olr_clr",
            "rlutcsaf": "lwtoa_ad_clr",
            "rsds": "swdn_sfc",
            "rsdsaf": "swdn_sfc_ad",
            "rsdscs": "swdn_sfc_clr",
            "rsdscsaf": "swdn_sfc_ad_clr",
            "rsus": "swup_sfc",
            "rsusaf": "swup_sfc_ad",
            "rsuscs": "swup_sfc_clr",
            "rsuscsaf": "swup_sfc_ad_clr",
            "rsut": "swup_toa",
            "rsutaf": "swup_toa_ad",
            "rsutcs": "swup_toa_clr",
            "rsutcsaf": "swup_toa_ad_clr",
            "rsdt": "swdn_toa",
        }


class RadiationAnalysisScript(AnalysisScript):
    """Abstract base class for analysis scripts.  User-defined analysis scripts
       should inhert from this class and override the requires and run_analysis methods.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        self.metadata = Metadata()
        self.description = "Calculates radiative flux metrics."
        self.title = "Radiative Fluxes"

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
                "lwup_sfc": {
                    "standard_name": "surface_outgoing_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwup_sfc_ad": {
                    "standard_name": "surface_outgoing_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwup_sfc_clr": {
                    "standard_name": "surface_outgoing_clear_sky_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwup_sfc_ad_clr": {
                    "standard_name": "surface_outgoing_clear_sky_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwdn_sfc": {
                    "standard_name": "surface_incoming_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwdn_sfc_ad": {
                    "standard_name": "surface_incoming_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwdn_sfc_clr": {
                    "standard_name": "surface_incoming_clear_sky_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwdn_sfc_ad_clr": {
                    "standard_name": "surface_incoming_clear_sky_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "olr": {
                    "standard_name": "toa_outgoing_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwtoa_ad": {
                    "standard_name": "toa_outgoing_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "olr_clr": {
                    "standard_name": "toa_outgoing_clear_sky_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "lwtoa_ad_clr": {
                    "standard_name": "toa_outgoing_clear_sky_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_sfc": {
                    "standard_name": "surface_outgoing_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_sfc_ad": {
                    "standard_name": "surface_outgoing_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_sfc_clr": {
                    "standard_name": "surface_outgoing_clear_sky_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_sfc_ad_clr": {
                    "standard_name": "surface_outgoing_clear_sky_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swdn_sfc": {
                    "standard_name": "surface_incoming_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swdn_sfc_ad": {
                    "standard_name": "surface_incoming_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swdn_sfc_clr": {
                    "standard_name": "surface_incoming_clear_sky_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swdn_sfc_ad_clr": {
                    "standard_name": "surface_incoming_clear_sky_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_toa": {
                    "standard_name": "toa_outgoing_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_toa_ad": {
                    "standard_name": "toa_outgoing_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_toa_clr": {
                    "standard_name": "toa_outgoing_clear_sky_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swup_toa_ad_clr": {
                    "standard_name": "toa_outgoing_clear_sky_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "swdn_toa": {
                    "standard_name": "toa_downwelling_shortwave_flux",
                    "units": "W m-2",
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

        anomalies = {}
        maps = {}
        timeseries = {}
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

            if name == "rlut":
                anomalies[name] = AnomalyTimeSeries.from_xarray_dataset(
                    datasets[self.metadata.catalog_key(variable)],
                    variable,
                )
                timeseries[name] = GlobalMeanTimeSeries.from_xarray_dataset(
                    datasets[self.metadata.catalog_key(variable)],
                    variable,
                )

        figure_paths = []

        # OLR anomally timeseries.
        figure = timeseries_and_anomalies(timeseries["rlut"], anomalies["rlut"],
                                          "OLR Global Mean & Anomalies")
        figure.save(Path(png_dir) / "olr-anomalies.png")
        figure_paths.append(Path(png_dir) / "olr-anomalies.png")

        # OLR.
        figure = radiation_decomposition(maps["rlutcsaf"], maps["rlutaf"],
                                         maps["rlutcs"], maps["rlut"], "OLR")
        figure.save(Path(png_dir) / "olr.png")
        figure_paths.append(Path(png_dir) / "olr.png")

        # SW TOTA.
        figure = radiation_decomposition(maps["rsutcsaf"], maps["rsutaf"],
                                         maps["rsutcs"], maps["rsut"],
                                         "Shortwave Outgoing Toa")
        figure.save(Path(png_dir) / "sw-up-toa.png")
        figure_paths.append(Path(png_dir) / "sw-up-toa.png")

        # Surface radiation budget.
        surface_budget = []
        for suffix in ["csaf", "af", "cs", ""]:
            surface_budget.append(maps[f"rlds{suffix}"] + maps[f"rsds{suffix}"] -
                                  maps[f"rlus{suffix}"] - maps[f"rsus{suffix}"])
        figure = radiation_decomposition(*surface_budget, "Surface Radiation Budget")
        figure.save(Path(png_dir) / "surface-radiation-budget.png")
        figure_paths.append(Path(png_dir) / "surface-radiation-budget.png")

        # TOA radiation budget.
        toa_budget = []
        for suffix in ["csaf", "af", "cs", ""]:
            toa_budget.append(maps[f"rsdt"] - maps[f"rlut{suffix}"] - maps[f"rsut{suffix}"])
        figure = radiation_decomposition(*toa_budget, "TOA Radiation Budget")
        figure.save(Path(png_dir) / "toa-radiation-budget.png")
        figure_paths.append(Path(png_dir) / "toa-radiation-budget.png")
        return figure_paths
