from numpy import array, mean, transpose

from .time_subsets import TimeSubset


class AnomalyTimeSeries(object):
    def __init__(self, data, time_data, latitude, units):
        self.data = data[...]
        self.x_data = time_data[...]
        self.y_data = latitude[...]
        self.x_label = "Time"
        self.y_label = "Latitude"
        self.data_label = units

    @classmethod
    def from_xarray_dataset(cls, dataset, variable):
        """Instantiates an AnomalyTimeSeries object from an xarray dataset."""
        v = dataset.data_vars[variable]
        axis_attrs = _dimension_order(dataset, v)

        time = TimeSubset(array(dataset.coords[v.dims[0]].data))
        latitude = array(dataset.coords[v.dims[-2]].data)
        data = mean(array(v.data), axis=-1) # Average over longitude.

        time, data = time.annual_means(data)
        average = mean(data, axis=0) # Average over longitude and time.
        anomaly = data
        for i in range(time.size):
            anomaly[i, :] -=  average[:]
        anomaly = transpose(anomaly)

        return cls(anomaly, time, latitude, v.attrs["units"])


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
