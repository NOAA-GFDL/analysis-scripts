# figure_tools
Tools to make common analysis figures.

### Motivation
The goal of this project is to provide a simple API to guide the development of
scripts that produce figures from xarry datasets (such as those produced from climate
models).

### Requirements
The only software packages that are required are:

- cartopy
- matplotlib
- numpy
- xarray

### How to install this package
For now I'd recommend creating and installing this package in a virtual enviroment:

```bash
$ python3 -m venv env
$ source env/bin/activate
$ pip install --upgrade pip
$ git clone https://github.com/NOAA-GFDL/analysis-scripts.git
$ cd analysis-scripts/figure_tools
$ pip install .
```

### Creating plots
Longitude-latitude maps, heatmaps, and line plots can be made from the provided
objects.  These objects can be instantiated directly from `xarray` datasets.  For example:

```python3
# Longitude-latitude map.
from figure_tools import Figure, LonLatMap


map = LonLatMap.from_xarray_dataset(<path to dataset>, <variable name>,
                                    time_method="annual mean", year=2010)
figure = Figure(title=<variable name>)
figure.add_map(map_)
figure.save(<path to output png file>)
```
