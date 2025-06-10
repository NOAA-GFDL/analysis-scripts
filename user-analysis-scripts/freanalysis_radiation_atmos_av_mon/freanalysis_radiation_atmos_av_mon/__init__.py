from dataclasses import dataclass
import json
from pathlib import Path

from analysis_scripts import AnalysisScript
from figure_tools import AnomalyTimeSeries, GlobalMeanTimeSeries, LonLatMap, \
                         observation_vs_model_maps, radiation_decomposition, \
                         timeseries_and_anomalies, chuck_radiation
import intake
import intake_esm
import pdb

@dataclass
class Metadata:
    """Helper class that stores the metadata needed by the plugin."""

    def variables(self):
        """Helper function to make maintaining this script easier if the
           catalog variable ids change.

        Returns:
            Dictionary mapping the names used in this script to the catalog
            variable ids.
        """
        return {
            "rlds": "rlds",
            "rldsaf": "rldsaf",
            "rldscs": "rldscs",
            "rldscsaf": "rldscsaf",
            "rlus": "rlus",
            "rlusaf": "rlusaf",
            "rluscs": "rluscs",
            "rluscsaf": "rluscsaf",
            "rlut": "olr",
            "rlutaf": "rlutaf",
            "rlutcs": "rlutcs",
            "rlutcsaf": "rlutcsaf",
            "rsds": "rsds",
            "rsdsaf": "rsdsaf",
            "rsdscs": "rsdscs",
            "rsdscsaf": "rsdscsaf",
            "rsus": "rsus",
            "rsusaf": "rsusaf",
            "rsuscs": "rsuscs",
            "rsuscsaf": "rsuscsaf",
            "rsut": "rsut",
            "rsutaf": "rsutaf",
            "rsutcs": "rsutcs",
            "rsutcsaf": "rsutcsaf",
            "rsdt": "rsdt",
        }

    def reference_variables(self):
        pass


class RadiationVsCeresAnalysisScript(AnalysisScript):
    """Radiative flux comparison to CERES analysis script.

    Attributes:
       description: Longer form description for the analysis.
       metadata: MetaData object to helper filter the data catalog.
       title: Title that describes the analysis.
    """
    def __init__(self):
        self.metadata = Metadata()
        self.description = "Compare the radiative flux to CERES."
        self.title = "Radiative Fluxes Vs. CERES"

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
                "rlus": {
                    "standard_name": "surface_outgoing_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rlusaf": {
                    "standard_name": "surface_outgoing_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rluscs": {
                    "standard_name": "surface_outgoing_clear_sky_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rluscsaf": {
                    "standard_name": "surface_outgoing_clear_sky_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rlds": {
                    "standard_name": "surface_incoming_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rldsaf": {
                    "standard_name": "surface_incoming_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rldscs": {
                    "standard_name": "surface_incoming_clear_sky_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rldscsaf": {
                    "standard_name": "surface_incoming_clear_sky_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rlut": {
                    "standard_name": "toa_outgoing_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rlutaf": {
                    "standard_name": "toa_outgoing_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rlutcs": {
                    "standard_name": "toa_outgoing_clear_sky_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rlutcsaf": {
                    "standard_name": "toa_outgoing_clear_sky_aerosol_free_longwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsus": {
                    "standard_name": "surface_outgoing_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsusaf": {
                    "standard_name": "surface_outgoing_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsuscs": {
                    "standard_name": "surface_outgoing_clear_sky_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsuscsaf": {
                    "standard_name": "surface_outgoing_clear_sky_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsds": {
                    "standard_name": "surface_incoming_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsdsaf": {
                    "standard_name": "surface_incoming_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsdscs": {
                    "standard_name": "surface_incoming_clear_sky_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsdscsaf": {
                    "standard_name": "surface_incoming_clear_sky_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsut": {
                    "standard_name": "toa_outgoing_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsutaf": {
                    "standard_name": "toa_outgoing_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsutcs": {
                    "standard_name": "toa_outgoing_clear_sky_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsutcsaf": {
                    "standard_name": "toa_outgoing_clear_sky_aerosol_free_shortwave_flux",
                    "units": "W m-2",
                    "dimensions": ["time", "lat", "lon"]
                },
                "rsdt": {
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
            reference_catalog: Path to a catalog of reference data.
            config: Dictonary of catalog metadata.  Will overwrite the
                    data defined in the Metadata helper class if they both
                    contain the same keys.

        Returns:
            A list of paths to the figures that were created.

        Raises:
            ValueError if the catalog cannot be filtered correctly.
        """
        # Seasonal climatology.
        figure_paths = []
        for season in [[12, 2], [3, 5], [6, 8], [9, 11]]:
            figure = self.plot_vs_obs(catalog, reference_catalog, "monthly", "rlut",
                                      "toa_lw_all_mon", png_dir, season,
                                      config={"realm": "atmos_cmip"})
            figure_paths.append(figure)

        # Annual mean climatology.
        figure = self.plot_vs_obs(catalog, reference_catalog, "monthly", "rlut",
                                  "toa_lw_all_mon", png_dir, config={"realm": "atmos_cmip"})
        figure_paths.append(figure)
        return figure_paths

    def plot_vs_obs(self, catalog, reference_catalog, frequency,
                    variable, reference_variable, png_dir,
                    month_range=None, config=None):
        # Connect to the catalog and filter to find the necessary datasets.
        model_catalog = intake.open_esm_datastore(catalog)
        query_params = {"variable_id": variable, "frequency": frequency}
        query_params.update(vars(self.metadata))
        if config:
            query_params.update(config)

        #pdb.set_trace()
        search_results = model_catalog.search(**query_params)
        print("model search results returned")
        datasets = search_results.to_dataset_dict(progressbar=False)
        if len(list(datasets.values())) != 1:
            print(query_params, list(datasets.values()))
            raise ValueError("could not filter the catalog down to a single dataset.")
        dataset = list(datasets.values())[0]
        print("Model dataset created")

        # Model Lon-lat maps.
        model_map = LonLatMap.from_xarray_dataset(dataset, variable, time_index=0,
                                                  time_method="instantaneous")
        print("Model map created")

        # Connect to the reference catalog and get the reference datasets.
        obs_catalog = intake.open_esm_datastore(reference_catalog)
        query_params = {
            "experiment_id": "ceres_ebaf_ed4.1",
            "variable_id": reference_variable,
        }
        search_results = obs_catalog.search(**query_params)
        print("obs search results returned")
        datasets = search_results.to_dataset_dict(progressbar=False)
        if len(list(datasets.values())) != 1:
            raise ValueError("could not filter the catalog down to a single dataset.")
        dataset = list(datasets.values())[0]
        print("Obs dataset created")

        if month_range == None:
            period = "annual"
            title = f"Annual {variable}"
        else:
            period = "seasonal"
            initials = {1: "j", 2: "f", 3: "m", 4: "a", 5: "m", 6: "j",
                        7: "j", 8: "a", 9: "s", 10: "o", 11: "n", 12: "d"}
            if month_range[1] - month_range[0] < 0:
                # We have crossed to the next year.
                months = [initials[x] for x in range(month_range[0], 13)]
                months += [initials[x] for x in range(1, month_range[1] + 1)]
            else:
                months = [initials[x] for x in range(month_range[0], month_range[1] + 1)]
            season = "".join(months)
            title = f"{season} {variable}"
        obs_map = LonLatMap.from_xarray_dataset(
            dataset, reference_variable, f"{period} climatology",
            year_range=[2003, 2018], month_range=month_range,
        )
        print("obs map created")
        obs_map.regrid_to_map(model_map)
        print("obs map regridded")

        figure = chuck_radiation(model_map, obs_map, f"{title}")
        print("chuck radiation")
        #breakpoint()
        output = Path(png_dir) / f"{title.lower().replace(' ', '-')}.png"
        print("path determined")
        figure.save(output)
        print("figure saved")
        return output


if __name__ == "__main__":
    RadiationAnalysisScript().run_analysis("model_catalog.json", ".",
                                           "obs_catalog.json")
