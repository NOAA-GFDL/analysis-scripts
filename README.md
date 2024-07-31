# analysis-scripts
A framework for analyzing GFDL model output

### Motivation
The goal of this project is to provide a simple API to guide the development of
scripts that produce figures and tables from GFDL model output.  This work will be used
by a simple web application to provide users an easy interface to interact with model
output data.

### Requirements
The code in this repository is broken up into components:

- analysis-scripts - A very simple package that just defines an abstract base class that
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

### For Workflow Developers

#### Running an analysis plugin
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

### For Analysis Script Developers

### How to use this framework.
The idea behind ths framework is to treat each analysis script as a plugin, which can
be discovered dynamically by the workflow.  Each analysis script is expected to be
its own fully developed python package, which has a name that starts with
`freanalysis_`.  At runtime, the workflow will search through all of its installed
python packages, looking specifically for packages whose names begin with
`freanalysis_`.  It will then search each of these found `freanalysis_` packages
for a class that inherits from the `AnalysisScript` base class provided by the
`analysis_scripts` package, and attempt to construct one of these objects.

### Creating A New Analysis Script For This Framework.
A python package is a directory that contains an `__init__.py` file.  In this example,
we will make a new analysis script called `freanalysis_readme_example`.  To do this,
let's setup up a directory:

```bash
freanalysis_readme_example
  -- README.md  # Explain what this analysis script does.
  -- pyproject.toml  # Tell python how to build/install this analysis script.
  -- freanalysis_readme_example  # This directory is the actual python package.
     -- __init__.py  # This file makes its parent directory a python package.
```

Once we have this directory tree, we can fill in the necessary files.


##### README.


##### pyproject.toml


##### Defining the analysis script class
Custom analysis scripts classes can be created that inherit the `AnalysisScript` base
class provided by the `analysis_scripts` package.  Override its contructor,
`requires`, and `run_analysis` methods. For example:

```python3
from analysis_scripts import AnalysisScript


class NewAnalysisScript(AnalysisScript):
    """Analysis script for some task.

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
                "activity_id": "<fill this>",
                "institution_id": "<fill this>",
                "source_id": "<fill this>",
                "experiment_id": "<fill this>",
                "frequency": "<fill this>",
                "modeling_realm": "<fill this>",
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
                "<fill this>": {
                    "standard_name": "<a standard name>",
                    "units": "<some units>",
                    "dimensions": ["time", "lat", "lon"]
                }, 
            }
        })

    def run_analysis(self, catalog, png_dir, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a model output catalog.
            png_dir: Directory to store output png figures in.
            reference_catalog: Path to a catalog of reference data.

        Returns:
            A list of png figures.
        """
        Do some stuff to create the figures.
        return ["figure1.png", "figure2.png",]
```

