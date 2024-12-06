from math import ceil

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from numpy import linspace, max, min, unravel_index

from .lon_lat_map import LonLatMap
from .zonal_mean_map import ZonalMeanMap


class Figure(object):
    def __init__(self, num_rows=1, num_columns=1, size=(16, 12), title=None):
        """Creates a figure for the input number of plots.

        Args:
            num_rows: Number of rows of plots.
            num_columns: Number of columns of plots.
        """
        self.figure = plt.figure(figsize=size, layout="compressed")
        if title is not None:
            self.figure.suptitle(title.title())
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.plot = [[None for y in range(num_columns)] for x in range(num_rows)]

    def add_map(self, map_, title, position=1, colorbar_range=None, colormap="coolwarm",
                normalize_colors=False, colorbar_center=0, num_levels=51, extend=None):
        """Adds a map to the figure.

        Args:
            map_: LonLatMap or ZonalMeanMap object.
            total: String title for the plot.
            position: Integer position index for the plot in the figure.
            colorbar_range: List of integers describing the colorbar limits.
        """
        # Create the plotting axes.
        optional_args = {}
        if isinstance(map_, LonLatMap):
            optional_args["projection"] = map_.projection
        plot = self.figure.add_subplot(self.num_rows, self.num_columns,
                                       position, **optional_args)

        # Set the colorbar properties.
        if colorbar_range == None:
            levels = num_levels
        else:
            # There seems to be some strange behavior if the number of level is too
            # big for a given range.
            levels = linspace(colorbar_range[0], colorbar_range[-1], num_levels, endpoint=True)
            if extend == None:
                data_max = max(map_.data)
                data_min = min(map_.data)
                if data_max > colorbar_range[1] and data_min < colorbar_range[0]:
                    extend = "both"
                elif data_max > colorbar_range[1]:
                    extend = "max"
                elif data_min < colorbar_range[0]:
                    extend = "min"
        if normalize_colors:
            norm = colors.CenteredNorm(vcenter=colorbar_center)
        else:
            norm = None

        # Make the map.
        optional_args = {"levels": levels, "cmap": colormap, "norm": norm, "extend": extend}
        if isinstance(map_, LonLatMap):
            optional_args["transform"] = ccrs.PlateCarree()
        cs = plot.contourf(map_.x_data, map_.y_data, map_.data, **optional_args)

        # Set the metadata.
        self.figure.colorbar(cs, ax=plot, label=map_.data_label)
        if isinstance(map_, LonLatMap):
            plot.coastlines()
            grid = plot.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
            grid.bottom_labels = False
            grid.top_labels = False
        if isinstance(map_, ZonalMeanMap) and map_.invert_y_axis:
            plot.invert_yaxis()
        plot.set_title(title.replace("_", " ").title())
        plot.set_xlabel(map_.x_label)
        plot.set_ylabel(map_.y_label)

        # Add date information if necessary.
        if hasattr(map_, "timestamp") and map_.timestamp != None:
            plot.text(0.85, 1, map_.timestamp, transform=plot.transAxes)

        # Store the plot in the figure object.
        x, y = self._plot_position_to_indices(position)
        self.plot[x][y] = plot

    def add_line_plot(self, line_plot, title, position=1):
        """Adds a line plot to the figure.

        Args:
            map_: LonLatMap or ZonalMeanMap object.
            total: String title for the plot.
            position: Integer position index for the plot in the figure.
        """
        plot = self.figure.add_subplot(self.num_rows, self.num_columns, position)
        plot.plot(line_plot.x_data, line_plot.data)
#       if isinstance(line_plot, GlobalMeanVerticalPlot) and line_plot.invert_y_axis:
#           plot.invert_yaxis()
        plot.set_title(title)
        plot.set_xlabel(line_plot.x_label)
        plot.set_ylabel(line_plot.y_label)

        # Store the plot in the figure object.
        x, y = self._plot_position_to_indices(position)
        self.plot[x][y] = plot

    def display(self):
        """Shows the figure in a new window."""
        plt.show()

    def save(self, path):
        plt.savefig(path)
        plt.clf()

    def _plot_position_to_indices(self, position):
        """Converts from a plot position to its x and y indices.

        Args:
            position: Plot position (from 1 to num_rows*num_columns).

        Returns:
            The x and y indices for the plot.
        """
        return unravel_index(position - 1, (self.num_rows, self.num_columns))
