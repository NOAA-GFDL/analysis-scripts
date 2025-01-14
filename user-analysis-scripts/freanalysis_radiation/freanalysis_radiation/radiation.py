from dataclasses import dataclass
import json
from pathlib import Path

from analysis_scripts import AnalysisScript
from figure_tools import AnomalyTimeSeries, GlobalMeanTimeSeries, LonLatMap, \
                         observation_vs_model_maps, radiation_decomposition, \
                         timeseries_and_anomalies
import intake


@dataclass
class Metadata:
    frequency: str = "mon"
    realm: str = "atmos"

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

    def run_analysis(self, catalog, png_dir, config=None, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a catalog.
            png_dir: Path to the directory where the figures will be made.
            config: Dictionary of catalog metadata.  Will overwrite the data
                    defined in the Metadata helper class if they both contain
                    the same keys.
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
            # Filter the catalog down to a single dataset for each variable.
            query_params = {"variable_id": variable}
            query_params.update(vars(self.metadata))
            if config:
                query_params.update(config)
            datasets = catalog.search(**query_params).to_dataset_dict(
                progressbar=True,
            )
            if len(list(datasets.values())) != 1:
                raise ValueError(f"could not filter the dataset down to just {variable}.")
            dataset = list(datasets.values())[0]

            # Lon-lat maps.
            maps[name] = LonLatMap.from_xarray_dataset(
                dataset,
                variable,
                time_method="annual mean",
                year=1980,
            )

            if name == "rlut":
                anomalies[name] = AnomalyTimeSeries.from_xarray_dataset(
                    dataset,
                    variable,
                )
                timeseries[name] = GlobalMeanTimeSeries.from_xarray_dataset(
                    dataset,
                    variable,
                )

        figure_paths = []

        # OLR anomally timeseries.
        figure = timeseries_and_anomalies(timeseries["rlut"], anomalies["rlut"],
                                          "OLR Global Mean & Anomalies")
        figure_paths.append(Path(png_dir) / "olr-anomalies.png")
        figure.save(figure_paths[-1])

        # OLR.
        figure = radiation_decomposition(maps["rlutcsaf"], maps["rlutaf"],
                                         maps["rlutcs"], maps["rlut"], "OLR")
        figure_paths.append(Path(png_dir) / "olr.png")
        figure.save(figure_paths[-1])

        # SW TOTA.
        figure = radiation_decomposition(maps["rsutcsaf"], maps["rsutaf"],
                                         maps["rsutcs"], maps["rsut"],
                                         "Shortwave Outgoing Toa")
        figure_paths.append(Path(png_dir) / "sw-up-toa.png")
        figure.save(figure_paths[-1])

        # Surface radiation budget.
        surface_budget = []
        for suffix in ["csaf", "af", "cs", ""]:
            surface_budget.append(maps[f"rlds{suffix}"] + maps[f"rsds{suffix}"] -
                                  maps[f"rlus{suffix}"] - maps[f"rsus{suffix}"])
        figure = radiation_decomposition(*surface_budget, "Surface Radiation Budget")
        figure_paths.append(Path(png_dir) / "surface-radiation-budget.png")
        figure.save(figure_paths[-1])

        # TOA radiation budget.
        toa_budget = []
        for suffix in ["csaf", "af", "cs", ""]:
            toa_budget.append(maps[f"rsdt"] - maps[f"rlut{suffix}"] - maps[f"rsut{suffix}"])
        figure = radiation_decomposition(*toa_budget, "TOA Radiation Budget")
        figure_paths.append(Path(png_dir) / "toa-radiation-budget.png")
        figure.save(figure_paths[-1])
        return figure_paths
