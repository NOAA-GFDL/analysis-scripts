# analysis-scripts
This repository is home to a new a framework for analyzing GFDL model output.

### Motivation
The goal of this project is to provide a simple API to guide the development of
scripts that produce figures and tables from GFDL model output.  This work will be used
by a simple web application to provide users an easy interface to interact with model
output data.

### How this repository is structured
This repository is split into two parts, which each contain several python
packages. The `core` subdirectory contains packages that allow an automated
workflow to discover and run any number of user created analysis packages that conform
to an API, and utility packages to facilitate plotting and provide common functions that
are shared between analysis packages.  The `user-analysis-scripts` subdirectory is where
user created analysis packages can be added.  These are expected to conform to an
API so that they may be automatically detected at runtime by the framework (similar to
how plugins work).  Please see the READMEs in the subdirectories and the packages they
contain for more detailed information.


### Creating an automated workflow
The `core` subdirectory contains the `analysis_scripts` python package, which provides
and API and some functions that allow users to set up custom workflows for model output
analysis.  This package can be installed using either `pip` or `conda`:

```bash
$ pip install --upgrade pip  # This is optional.
$ cd core/analysis_scripts
$ pip install .
```

The idea is that users can create custom analysis packages whose names start with
 "freananlysis_" and contain a class that inherits from the provided `AnalysisScript` class.
These custom classes can then override the constructor and provided `requires` and
`run_analysis` methods.  As an example, let's make a new python package
"freanalysis_something".  First, let's create a directory tree:

```bash
freanalysis_something
├── freanalysis_something
│   └── __init__.py
├── pyproject.toml
├── README.md
└── tests
    └── test_freanalysis_something.py
```

In `freanalysis_something/freanalysis_something/__init__.py`, let's add the following:

```python3
from analysis_scripts import AnalysisScript


class NewAnalysisScript(AnalysisScript):
    """Custom Analysis script for some task.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        """Instantiates an object.  The user should provide a description and title."""
        self.description = "This analysis does something cool."
        self.title = "Brief, but descriptive name for the analysis."

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string describing the metadata.
        """
        return json.dumps({
            "settings": {
                "activity_id": "some activity",
                "institution_id": "where was this developed?",
                "source_id": "<fill this>",
                "experiment_id": "what experiment is this analysis for",
                "frequency": "what kind of data is expected (monthly, daily, etc.)?",
                "modeling_realm": "what modeling realm?",
                "table_id": "<fill this>",
                "member_id": "<fill this>",
                "grid_label": "<fill this>",
                "temporal_subset": "<fill this>",
                "chunk_freq": "<fill this>",
                "platform": "<fill this>",
                "cell_methods": "<fill this>"
            },
            "dimensions": {
                # These are just examples, you can put more/different ones.
                "lat": {"standard_name": "latitude"},
                "lon": {"standard_name": "longitude"},
                "time": {"standard_name": "time"}
            },
            "varlist": {
                "some_variable": {
                    "standard_name": "some standard name",
                    "units": "some units",
                    "dimensions": ["time", "lat", "lon"]
                }, 
            }
        })

    def run_analysis(self, catalog, png_dir, config=None, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a model output catalog.
            png_dir: Directory to store output png figures in.
            config: Dictionary of configuration options.
            reference_catalog: Path to a catalog of reference data.

        Returns:
            A list of png figures.
        """
        # Do some stuff to create the figures.
        return ["figure1.png", "figure2.png",]
```

Next, in `freanalysis_something/pyproject.toml`, we can put the following:

```toml
[build-system]
requires = [
    "setuptools >= 40.9.0",
]
build-backend = "setuptools.build_meta"

[project]
name = "freanalysis_something"
version = "0.1"
dependencies = [
    "intake",
    "intake-esm",
    # More python package dependencies if needed
]
requires-python = ">= 3.6"
authors = [
    {name = "Your name"},
]
maintainers = [
    {name = "Your name", email = "Your email address"},
]
description = "Some description"
readme = "README.md"
classifiers = [
    "Programming Language :: Python"
]
```

Congrats!  The `freanalysis_something` package is now compatible with this framework.
In order to use it, a workflow would first have to install it:

```bash
$ cd freanalysis_something
$ pip install .
```

Once installed, the provided workflow functions should be able to automatically discover
and run the package.  For example, a simple workflow script could look like this:

```python3
from analysis_scripts import available_plugins, plugin_requirements, run_plugin


# Create a data catalog.
# Some code to create a data "catalog.json" ...

# Show the installed plugins.
print(available_plugins())

# Run the radiative fluxes plugin.
name = "freanalysis_something"  # Name of the custom analysis script you want to run.
print(plugin_requirements(name))
figures = run_plugin(name, "catalog.json", "pngs")
```
