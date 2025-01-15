import cartopy.crs as ccrs
from cartopy.util import add_cyclic
from numpy import array, array_equal, cos, mean, ndarray, pi, sum
from xarray import DataArray

from .time_subsets import TimeSubset


class LonLatMap(object):
    """Longitude-latitude data map.

    Attributes:
        coastlines: Flag that determines if coastlines are drawn on the map.
        data: numpy array of data values.
        data_label: String units for the colorbar.
        projection: Cartopy map projection to use.
        x_data: numpy array of data values for the x-axis.
        xlabel: String label for the x-axis ("Longitude")
        x_data: numpy array of data values for the y-axis.
        ylabel: String label for the y-axis ("Latitude")
    """
    def __init__(self, data, longitude, latitude, units=None,
                 projection=ccrs.Mollweide(), coastlines=True, add_cyclic_point=True,
                 timestamp=None):
        if add_cyclic_point:
            self.data, self.x_data, self.y_data = add_cyclic(data[...], longitude[...],
                                                             latitude[...])
        else:
            self.data = data[...]
            self.x_data = longitude[...]
            self.y_data = latitude[...]
        self.projection = projection
        self.coastlines = coastlines
        self.x_label = "Longitude"
        self.y_label = "Latitude"
        self.data_label = units
        self.timestamp = timestamp

    def __add__(self, arg):
        """Allows LonLatMap objects to be added together."""
        self._compatible(arg)
        return LonLatMap(self.data + arg.data, self.x_data, self.y_data,
                         units=self.data_label, projection=self.projection,
                         coastlines=self.coastlines, add_cyclic_point=False,
                         timestamp=self.timestamp)

    def __sub__(self, arg):
        """Allows LonLatMap objects to be subtracted from one another."""
        self._compatible(arg)
        return LonLatMap(self.data - arg.data, self.x_data, self.y_data,
                         units=self.data_label, projection=self.projection,
                         coastlines=self.coastlines, add_cyclic_point=False,
                         timestamp=self.timestamp)

    @classmethod
    def from_xarray_dataset(cls, dataset, variable, time_method=None, time_index=None,
                            year=None, year_range=None, month_range=None):
        """Instantiates a LonLatMap object from an xarray dataset."""
        v = dataset.data_vars[variable]
        data = array(v.data[...])
        axis_attrs = _dimension_order(dataset, v)
        longitude = array(dataset.coords[v.dims[-1]].data[...])
        latitude = array(dataset.coords[v.dims[-2]].data[...])

        if axis_attrs[0] == "t":
            time = array(dataset.coords[v.dims[0]].data[...])
            if time_method == "instantaneous":
                if time_method == None:
                    raise ValueError("time_index is required when time_method='instantaneous.'")
                data = data[time_index, ...]
                timestamp = f"@ {str(time[time_index])}"
            elif time_method == "annual mean":
                if year == None:
                    raise ValueError("year is required when time_method='annual mean'.")
                time = TimeSubset(time)
                data = time.annual_mean(data, year)
                timestamp = r"$\bar{t} = $" + str(year)
            elif "climatology" in time_method:
                if year_range == None or len(year_range) != 2:
                    raise ValueError("year_range is required ([star year, end year]" +
                                     " when time_method is a climatology.")
                if time_method == "annual climatology":
                    time = TimeSubset(time)
                    data = time.annual_climatology(data, year_range)
                    timestamp = f"{year_range[0]} - {year_range[1]} annual climatology"
                elif time_method == "seasonal climatology":
                    if month_range == None or len(month_range) != 2:
                        raise ValueError("month_range is required ([start month, end month])" +
                                         " when time_method='seasonal climatology'.")
                    time = TimeSubset(time)
                    data = time.seasonal_climatology(data, year_range, month_range)
                    timestamp = ""
            else:
                valid_values = ["instantaneous", "annual mean", "annual climatology",
                                "seasonal climatology"]
                raise ValueError(f"time_method must one of :{valid_values}.")
        else:
            timestamp = None

        return cls(data, longitude, latitude, units=v.attrs["units"], timestamp=timestamp)

    def global_mean(self):
        """Performs a global mean over the longitude and latitude dimensions.

        Returns:
            Gobal mean value.
        """

        weights = cos(2.*pi*self.y_data/360.)
        return sum(mean(self.data, axis=-1)*weights, axis=-1)/sum(weights)

    def regrid_to_map(self, map_):
        """Regrid the data to match in the input map.

        Args:
            map_: A LonLatMap to regrid to.
        """
        if not isinstance(map_, LonLatMap):
            raise TypeError("input map must be a LonLatMap.")
        try:
            self._compatible(map_)
            return
        except ValueError:
            da = DataArray(self.data, dims=["y", "x"],
                           coords={"x": self.x_data, "y": self.y_data})
            da2 = DataArray(map_.data, dims=["y", "x"],
                            coords={"x": map_.x_data, "y": map_.y_data})
            self.data = array(da.interp_like(da2, kwargs={"fill_value": "extrapolate"}))
            self.x_data = map_.x_data
            self.y_data = map_.y_data

    def _compatible(self, arg):
        """Raises a ValueError if two objects are not compatible."""
        if not isinstance(arg, LonLatMap):
            raise TypeError("input map must be a LonLatMap.")
        for attr in ["x_data", "y_data", "projection", "data_label"]:
            if isinstance(getattr(self, attr), ndarray):
                equal = array_equal(getattr(self, attr), getattr(arg, attr))
            else:
                equal = getattr(self, attr) == getattr(arg, attr)
            if not equal:
                raise ValueError(f"The same {attr} is required for both objects.")


def _dimension_order(dataset, variable):
    """Raises a ValueError if the variable's dimensoins are not in an expected order.

    Returns:
        A list of the dimension axis attribute strings.
    """
    axis_attrs = [dataset.coords[x].attrs["axis"].lower()
                  if "axis" in dataset.coords[x].attrs else None
                  for x in variable.dims]
    allowed = [x  + ["y", "x"] for x in [["t",], ["z",], [None,], []]]
    for config in allowed:
        if axis_attrs == config:
            return axis_attrs
    raise ValueError(f"variable {variable} contains unexpected axes ordering {axis_attrs}.")
