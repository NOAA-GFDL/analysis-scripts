# freanalysis
Package that can run GFDL model analysis plugins.

### Motivation
This crates a simple way for FRE to discover and run user generated analysis packages
to create figures to analyze the GFDL models.

### Requirements
The software packages that are required are:

- analysis-scripts

### How to use
Users can create their own python packages that start with the name `freanalysis_`.
This package will search for installed packages that start with this name, and
then try to use them:

```python3
from freanalysis import available_plugins, list_plugins, plugin_requirements, run_plugin


# Get a list of all available plugins:
plugins = available_plugins()


# Print out a list of all available plugins:
list_plugins()


# Get the metadata for each plugin.  This can be used to create/verify against a data
# catalog (i.e., if you want to check if a plugin is compatable with a catalog).
for name in plugins:
    metadata = plugin_requirements(name)


# Run the plugins.  You need to pass in a path to a data catalog, and a directory where
# you want the figures to be created.
for name in plugins:
    figures = run_plugin(name, catalog, png_dir, reference_catalog=None)
```
