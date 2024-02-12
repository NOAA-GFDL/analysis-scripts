from numpy import array, datetime64, mean, zeros


class TimeSubset(object):
    def __init__(self, data):
        """Instantiates an object.

        Args:
            data: An xarray DataArray for the time dimension of an xarray Dataset.
        """
        self.data = data

    def annual_mean(self, data, year):
        """Calculates the annual mean of the input date for the input year.

        Args:
            data: Numpy array of data to be averaged.
            year: Integer year to average over.
        """
        start, end = None, None
        for i, point in enumerate(self.data):
            month, y = self._month_and_year(point)
            if y == year:
                if month == 1:
                    start = i
                elif month == 12:
                    end = i + 1
            if None not in [start, end]: break
        else:
            raise ValueError(f"could not find year {year}.")
        return mean(array(data[start:end, ...]), axis=0)

    def annual_means(self, data):
        """Calculates the annual means of the input date for each year.

        Args:
            data: Numpy array of data to be averaged.

        Returns:
            Numpy array of years that were averaged over and a numpy array of the
            average data.
        """
        years = {}
        for i, point in enumerate(self.data):
            month, year = self._month_and_year(point)
            if year not in years:
                years[year] = [None, None]
            if month == 1:
                years[year][0] = i
            elif month == 12:
                years[year][1] = i + 1

        years_data = sorted(years.keys())
        means_data = zeros(tuple([len(years_data),] + list(data.shape[1:])))
        for i, key in enumerate(years_data):
            start, end = years[key]
            means_data[i, ...] = mean(array(data[start:end, ...]), axis=0)
        return array(years_data), means_data

    def _month_and_year(self, time):
        """Returns the integer month and year for the input time point.

        Args:
            Integer month and year values.
        """
        if isinstance(time, datetime64):
            year = time.astype("datetime64[Y]").astype(int) + 1970
            month = time.astype("datetime64[M]").astype(int) % 12 + 1
        else:
            year = time.year
            month = time.month
        return month, year
