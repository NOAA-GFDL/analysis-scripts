# analysis-scripts
A framework for analyzing GFDL model output

### Motivation
The goal of this project is to provide a simple API to guide the development of
scripts that produce figures and tables from GFDL model output.  This work will be used
by a simple web application to provide users an easy interface to interact with model
output data.

### Requirements
The code in this repository is broken up into components:

- analysis-scripts - A very simple package that just defines an abstract base clases that
                     all user-created plugins should inherit from.
- figure_tools - An optional package that contains some helper functions and classes
                 for making common plots.
- freanalysis - A package that is designed to be used by whatever workflow is responsible
                for running the analysis.
- freanalysis_aerosol - A plugin that creates aerosl mass figures.
- freanalysis_clouds - A plugin that creates cloud amount figures.
- freanalysis_radiation - A plugin that creates radiative flux figures.

### How to install everything
For now I'd recommend creating a virtual enviroment, and then installing each of the
packages listed above:

```bash
$ python3 -m venv env
$ source env/bin/activate
$ pip install --upgrade pip
$ cd analysis-scripts; pip install .; cd ..
$ cd figure_tools; pip install .; cd ..
$ cd freanalysis; pip install .; cd ..
$ cd freanalysis_aerosol; pip install .; cd ..
$ cd freanalysis_clouds; pip install .; cd ..
$ cd freanalysis_radiation; pip install .; cd ..
```

# Running an analysis plugin
In order to run a plugin, you must first create a data catalog and can then perform
the analysis:

```python3
from freanalysis.create_catalog import create_catalog
from freanalysis.plugins import list_plugins, plugin_requirements, run_plugin


# Create a data catalog.
create_catalog(pp_dir, "catalog.json")

# Show the installed plugins.
list_plugins()

# Run the radiative fluxes plugin.
name = "freanalysis_radiation"
reqs = plugin_requirements(name)
print(reqs)
run_plugin(name, "catalog.json", "pngs")
```
