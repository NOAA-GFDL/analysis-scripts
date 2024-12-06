from math import ceil, floor

from numpy import abs, max, min, percentile

from .figure import Figure


def observation_vs_model_maps(reference, model, title):
    figure = Figure(num_rows=2, num_columns=2, title=title, size=(14, 12))

    # Create common color bar for reference and model.
    reference_range = [floor(min(reference.data)), ceil(max(reference.data))]
    model_range = [floor(min(model.data)), ceil(max(model.data))]
    colorbar_range = [None, None]
    colorbar_range[0] = reference_range[0] if reference_range[0] < model_range[0] \
                        else model_range[0]
    colorbar_range[1] = reference_range[1] if reference_range[1] > model_range[1] \
                        else model_range[1]

    # Reference data.
    global_mean = reference.global_mean()
    figure.add_map(reference, f"Observations [Mean: {global_mean:.2f}]", 1,
                   colorbar_range=colorbar_range)

    # Model data.
    global_mean = model.global_mean()
    figure.add_map(model, f"Model [Mean: {global_mean:.2f}]", 2,
                   colorbar_range=colorbar_range)

    # Difference between the reference and model.
    difference = reference - model
    color_range = _symmetric_colorbar_range(difference.data)
    global_mean = difference.global_mean()
    figure.add_map(difference, f"Obs - Model [Mean: {global_mean:.2f}]", 3,
                   colorbar_range=color_range,
                   normalize_colors=True)

    # Use percentiles.
    zoom = int(ceil(percentile(abs(difference.data), 95)))
    figure.add_map(difference, f"Obs - Model [Mean: {global_mean:.2f}]", 4,
                   colorbar_range=[-1*zoom, zoom], num_levels=19,
                   normalize_colors=True)
    return figure


def radiation_decomposition(clean_clear_sky, clean_sky, clear_sky, all_sky, title):
    figure = Figure(num_rows=2, num_columns=2, title=title, size=(16, 10))
    maps = [clean_clear_sky, clean_sky - clean_clear_sky, all_sky - clean_sky, all_sky]
    titles = ["Clean-clear Sky", "Cloud Effects", "Aerosol Effects", "All Sky"]
    for i, (map_, title) in enumerate(zip(maps, titles)):
        global_mean = map_.global_mean()
        updated_title = f"{title} [Mean: {global_mean:.2f}]"
        if title in ["Cloud Effects", "Aerosol Effects"]:
            figure.add_map(map_, updated_title, i + 1,
                           colorbar_range=_symmetric_colorbar_range(map_.data),
                           normalize_colors=True)
        else:
            figure.add_map(map_, updated_title, i + 1,
                           normalize_colors=True, colorbar_center=global_mean)
    return figure


def timeseries_and_anomalies(timeseries, map_, title):
    figure = Figure(num_rows=1, num_columns=2, title=title, size=(16, 10))
    figure.add_line_plot(timeseries, "Timeseries", 1)
    figure.add_map(map_, "Zonal Mean Anomalies", 2,
                   colorbar_range=_symmetric_colorbar_range(map_.data),
                   normalize_colors=True)
    return figure


def zonal_mean_vertical_and_column_integrated_map(zonal_mean, lon_lat, title):
    figure = Figure(num_rows=1, num_columns=2, title=title, size=(16, 10))
    figure.add_map(zonal_mean, "Zonal Mean Vertical Profile", 1)
    figure.add_map(lon_lat, "Column-integrated", 2)
    return figure


def _symmetric_colorbar_range(data):
    colorbar_range = [int(floor(min(data))), int(ceil(max(data)))]
    if abs(colorbar_range[0]) > abs(colorbar_range[1]):
        colorbar_range[1] = -1*colorbar_range[0]
    else:
        colorbar_range[0] = -1*colorbar_range[1]
    return colorbar_range
