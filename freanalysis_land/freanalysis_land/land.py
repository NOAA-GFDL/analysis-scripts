import json
from analysis_scripts import AnalysisScript
import intake
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import datetime
import pandas as pd
import re
import xarray as xr


class LandAnalysisScript(AnalysisScript):
    """Abstract base class for analysis scripts.  User-defined analysis scripts
       should inhert from this class and override the requires and run_analysis methods.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        """Instantiates an object.  The user should provide a description and title."""
        self.description = "This is for analysis of land model (stand-alone)"
        self.title = "Soil Carbon"

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string describing the metadata.
        """
        raise NotImplementedError("you must override this function.")
        return json.dumps("{json of metadata MDTF format.}")
    
    def global_map(self,dataset,var,dates,plt_time=None,colormap='viridis',title=''):
        """
        Generate a global map and regional subplots for a specified variable from an xarray dataset.

        This function creates a global map and several regional subplots (North America, South America, Europe, Africa, Asia, and Australia)
        using the specified variable from an xarray dataset. The generated map will be saved as a PNG file.

        Parameters:
        ----------
        dataset : xarray.Dataset
            The input xarray dataset containing the variable to be plotted.
        
        var : str
            The name of the variable in the dataset to be plotted.
        
        dates: list
            The list of dates from the dataframe, converted to period index.

        plt_time : int, optional
            The time index to plot from the variable data. Defaults to the length of `dates` - 1, or last date in dataset.
        
        colormap : str, optional
            The colormap to use for plotting the data. Defaults to 'viridis'.
        
        title : str, optional
            The title for the figure. Defaults to an empty string.

        Returns:
        -------
        fig : matplotlib figure object
            The function returns the plot for saving

        Notes:
        -----
        The function uses Cartopy for map projections and Matplotlib for plotting.
        Ensure Cartopy and Matplotlib are installed in your Python environment.

        The output file is saved with the format '<variable>_global_map.png'.

        Examples:
        --------
        global_map(my_dataset, 'mrso', plt_time=0, colormap='coolwarm', title='Global Temperature Map')
        """
        lon = dataset.lon
        lat = dataset.lat

        if plt_time == None: plt_time=len(dates)-1

        data = dataset[var][plt_time].values
        projection = ccrs.PlateCarree()
        fig = plt.figure(figsize=(8.5, 11))

        # Global map
        ax_global = fig.add_subplot(3, 1, 1, projection=projection)
        ax_global.set_title('Global Map')
        mesh = ax_global.pcolormesh(lon, lat, data, transform=projection, cmap=colormap)
        ax_global.coastlines()

        # List of bounding boxes for different continents (min_lon, max_lon, min_lat, max_lat)
        regions = {
            'North America': [-170, -47, 0, 85],
            'South America': [-90, -30, -60, 15],
            'Europe': [-10, 60, 30, 75],
            'Africa': [-20, 50, -35, 37],
            'Asia': [60, 150, 5, 75],
            'Australia': [110, 180, -50, 0]
        }

        # Create subplots for each region
        for i, (region, bbox) in enumerate(regions.items(), start=1):
            ax = fig.add_subplot(3, 3, i + 3, projection=projection)
            ax.set_extent(bbox, crs=projection)
            ax.set_title(region)
            ax.pcolormesh(lon, lat, data, transform=projection, cmap=colormap)
            ax.coastlines()
            ax.add_feature(cartopy.feature.BORDERS)

        # Add colorbar
        fig.colorbar(mesh, ax=ax_global, orientation='horizontal', pad=0.05, aspect=50)
        plt.suptitle(title)
        plt.tight_layout()

        return fig
        # plt.savefig(var+'_global_map.png')
        # plt.close()

    def timeseries(self, dataset,var,dates_period,var_range=None,minlon = 0,maxlon = 360,minlat = -90,maxlat=90,timerange=None,title=''):
        '''
        Generate a time series plot of the specified variable from a dataset within a given geographic and temporal range.


        Parameters:
        -----------
        dataset : xarray.Dataset
            The dataset containing the variable to be plotted.
        var : str
            The name of the variable to plot from the dataset.
        dates_period : pandas.DatetimeIndex
            The dates for the time series data.
        var_range : tuple of float, optional
            The range of variable values to include in the plot (min, max). If not provided, the default range is (0, inf).
        minlon : float, optional
            The minimum longitude to include in the plot. Default is 0.
        maxlon : float, optional
            The maximum longitude to include in the plot. Default is 360.
        minlat : float, optional
            The minimum latitude to include in the plot. Default is -90.
        maxlat : float, optional
            The maximum latitude to include in the plot. Default is 90.
        timerange : tuple of int, optional
            The range of years to plot (start_year, end_year). If not provided, all available years in the dataset will be plotted.
        title : str, optional
            The title of the plot. Default is an empty string.

        Returns:
        --------
        matplotlib.figure.Figure
            The figure object containing the generated time series plot.
        
        Notes:
        ------
        The function filters the dataset based on the provided variable range, longitude, and latitude bounds. It then 
        calculates the monthly and annual means of the specified variable and plots the seasonal and annual means.
        
        '''
        if var_range != None:
            data_filtered = dataset.where((dataset[var] > var_range[0]) & (dataset[var] <= var_range[1]) &
                                        (dataset.lat >= minlat) & (dataset.lon >= minlon) &
                                        (dataset.lat <= maxlat) & (dataset.lon <= maxlon))
        else:
            data_filtered = dataset.where((dataset[var] > 0) &
                                        (dataset.lat >= minlat) & (dataset.lon >= minlon) &
                                        (dataset.lat <= maxlat) & (dataset.lon <= maxlon))
        data_filtered['time'] = dates_period

        data_df = pd.DataFrame(index = dates_period)
        data_df['monthly_mean'] = data_filtered.resample(time='YE').mean(dim=['lat','lon'],skipna=True)[var].values
        data_df['monthly_shift'] = data_df['monthly_mean'].shift(1)

        if timerange != None:
            ys, ye = (str(timerange[0]),str(timerange[1]))
            plot_df = data_df.loc[f'{ys}-1-1':f'{ye}-1-1']
        else:
            plot_df = data_df

        fig, ax = plt.subplots()
        plot_df.resample('Q').mean()['monthly_shift'].plot(ax=ax,label='Seasonal Mean')
        plot_df.resample('Y').mean()['monthly_mean'].plot(ax=ax,label='Annual Mean')
        plt.legend()
        plt.title(title)
        plt.xlabel('Years')
        return fig

    def run_analysis(self, catalog, png_dir, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a model output catalog.
            png_dir: Directory to store output png figures in.
            reference_catalog: Path to a catalog of reference data.

        Returns:
            A list of png figures.
        """
        print ('WARNING: THESE FIGURES ARE FOR TESTING THE NEW ANALYSIS WORKFLOW ONLY AND SHOULD NOT BE USED IN ANY OFFICIAL MANNER FOR ANALYSIS OF LAND MODEL OUTPUT.')
        col = intake.open_esm_datastore(catalog)
        df = col.df

        # Soil Carbon
        var = 'cSoil'
        print ('Soil Carbon Analysis')
        cat = col.search(variable_id=var,realm='land_cmip')
        other_dict = cat.to_dataset_dict(cdf_kwargs={'chunks':{'time':12},'decode_times':False})
        combined_dataset = xr.concat(list(dict(sorted(other_dict.items())).values()), dim='time')

        # Other data:
        # land_static_file = re.search('land_static:\s([\w.]*)',combined_dataset.associated_files).group(1)
        # STATIC FILES SHOULD BE PART OF THE CATALOG FOR EASY ACCESS

        # Select Data and plot
        dates = [datetime.date(1,1,1) + datetime.timedelta(d) for d in combined_dataset['time'].values] # Needs to be made dynamic
        dates_period = pd.PeriodIndex(dates,freq='D')

        sm_fig = self.global_map(combined_dataset,var,dates,title='Soil Carbon Content (kg/m^2)')
        plt.savefig(png_dir+var+'_global_map.png')
        plt.close()

        ts_fig = self.timeseries(combined_dataset,var,dates_period,title='Global Average Soil Carbon')
        plt.savefig(png_dir+var+'_global_ts.png')
        plt.close()

        # Soil Moisture
        var = 'mrso'
        print ('Soil Moisture Analysis')
        cat = col.search(variable_id=var,realm='land_cmip')
        other_dict = cat.to_dataset_dict(cdf_kwargs={'chunks':{'time':12},'decode_times':False})
        combined_dataset = xr.concat(list(dict(sorted(other_dict.items())).values()), dim='time')

        # Other data:
        # soil_area_file = re.search('soil_area:\s([\w.]*)',combined_dataset.associated_files).group(1)
        # STATIC FILES SHOULD BE PART OF THE CATALOG FOR EASY ACCESS

        # Select Data and plot
        dates = [datetime.date(1,1,1) + datetime.timedelta(d) for d in combined_dataset['time'].values] # Needs to be made dynamic
        dates_period = pd.PeriodIndex(dates,freq='D')

        sm_fig = self.global_map(combined_dataset,var,dates,title='Soil Moisture (kg/m^2)')
        plt.savefig(png_dir+var+'_global_map.png')
        plt.close()
