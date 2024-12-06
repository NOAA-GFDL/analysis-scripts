from numpy import array, cos, mean, pi, sum

from .time_subsets import TimeSubset


class GlobalMeanTimeSeries(object):
    def __init__(self, data, time_data, units):
        self.data = data[...]
        self.x_data = time_data[...]
        self.x_label = "Time"
        self.y_label = units

    @classmethod
    def from_xarray_dataset(cls, dataset, variable):
        """Instantiates an AnomalyTimeSeries object from an xarray dataset."""
        v = dataset.data_vars[variable]
        axis_attrs = _dimension_order(dataset, v)

        time = TimeSubset(array(dataset.coords[v.dims[0]].data))
        latitude = array(dataset.coords[v.dims[-2]].data)
        time, data = time.annual_means(v.data)
        data = _global_mean(data, latitude)

        return cls(data, time, v.attrs["units"])


def _dimension_order(dataset, variable):
    """Raises a ValueError if the variable's dimensions are not in an expected order.

    Returns:
        A list of the dimension axis attribute strings.
    """
    axis_attrs = [dataset.coords[x].attrs["axis"].lower()
                  if "axis" in dataset.coords[x].attrs else None
                  for x in variable.dims]
    if axis_attrs == ["t", "y", "x"]:
        return axis_attrs
    raise ValueError(f"variable {variable} contains unexpected axes ordering {axis_attrs}.")


def _global_mean(data, latitude):
    """Performs a global mean over the longitude and latitude dimensions.

    Returns:
        Gobal mean value.
    """
    weights = cos(2.*pi*latitude/360.)
    return sum(mean(data, axis=-1)*weights, axis=-1)/sum(weights)
