from numpy import array, array_equal, mean, ndarray

from .time_subsets import TimeSubset


class ZonalMeanMap(object):
    def __init__(self, data, latitude, y_axis_data, units=None, y_label=None,
                 invert_y_axis=False, timestamp=None):
        self.data = data[...]
        self.x_data = latitude[...]
        self.y_data = y_axis_data[...]
        self.invert_y_axis = invert_y_axis
        self.x_label = "Latitude"
        self.y_label = y_label
        self.data_label = units
        self.timestamp = timestamp

    def __add__(self, arg):
        self._compatible(arg)
        return ZonalMeanMap(self.data + arg.data, self.x_data, self.y_data,
                            units=self.data_label, y_label=self.y_label,
                            invert_y_axis=self.invert_y_axis, timestamp=self.timestamp)

    def __sub__(self, arg):
        self._compatible(arg)
        return ZonalMeanMap(self.data - arg.data, self.x_data, self.y_data,
                            units=self.data_label, y_label=self.y_label,
                            invert_y_axis=self.invert_y_axis, timestamp=self.timestamp)

    @classmethod
    def from_xarray_dataset(cls, dataset, variable, time_method=None, time_index=None,
                            year=None, y_axis=None, y_label=None, invert_y_axis=False):
        """Instantiates a ZonalMeanMap object from an xarray dataset."""
        v = dataset.data_vars[variable]
        data = array(v.data[...])
        axis_attrs = _dimension_order(dataset, v)
        latitude = array(dataset.coords[v.dims[-2]].data[...])
        y_dim = array(dataset.coords[v.dims[-3]].data[...])
        y_dim_units = y_label or dataset.coords[v.dims[-3]].attrs["units"]

        if axis_attrs[0] == "t":
            time = array(dataset.coords[v.dims[0]].data[...])
            if time_method == "instantaneous":
                if time_method == None:
                    raise ValueError("time_index is required when time_method='instantaneous.'")
                data = data[time_index, ...]
                timestamp = str(time[time_index])
            elif time_method == "annual mean":
                if year == None:
                    raise ValueError("year is required when time_method='annual mean'.")
                time = TimeSubset(time)
                data = time.annual_mean(data, year)
                timestamp = str(year)
            else:
                raise ValueError("time_method must be either 'instantaneous' or 'annual mean'.")
        else:
            timestamp = None

        return cls(mean(data, -1), latitude, y_dim, v.attrs["units"], y_dim_units,
                   invert_y_axis, timestamp)

    def _compatible(self, arg):
        """Raises a ValueError if two objects are not compatible."""
        for attr in ["x_data", "y_data", "invert_y_axis", "y_label", "data_label"]:
            if isinstance(getattr(self, attr), ndarray):
                equal = array_equal(getattr(self, attr), getattr(arg, attr))
            else:
                equal = getattr(self, attr) == getattr(arg, attr)
            if not equal:
                raise ValueError(f"The same {attr} is required for both objects.")


def _dimension_order(dataset, variable):
    """Raises a ValueError if the variable's dimensions are not in an expected order.

    Returns:
        A list of the dimension axis attribute strings.
    """
    axis_attrs = [dataset.coords[x].attrs["axis"].lower()
                  if "axis" in dataset.coords[x].attrs else None
                  for x in variable.dims]
    allowed = [x + ["y", "x"] for x in [["z",], [None,], ["t", "z"], ["t", None]]]
    for config in allowed:
        if axis_attrs == config:
            return axis_attrs
    raise ValueError(f"variable contains unexpected axes ordering {axis_attrs}.")
