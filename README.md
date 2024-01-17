# analysis-scripts
A framework for analyzing GFDL model output

### Motivation
The goal of this project is to provide a simple API to guide the development of
scripts that produce figures and tables from GFDL model output.  This work will be used
by a simple web application to provide users an easy interface to interact with model
output data.

### Requirements
The only software packages that are required are `intake` and `intake-esm`.

### How to use this framework.
Custom analysis scripts classes can be created that inherit the `AnalysisScript` base
class, then override its `requires` and `run_analysis` methods. For example:

```python3
from analysis_scripts import AnalysisScript, Metric, Output

class NewAnalysis(AnalysisScript):
    """A new analysis script that inherits from the abstract base class

    Attributes:
       catalog: intake_esm Catalog object.
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self, catalog_path, title, description):
        self.catalog = intake.open_esm_datastore(catalog_path)
        self.description = description
        self.title = title

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run

        Returns:
            A list of Metric objects.
        """
        return [Metric("olr", "yearly"),]

    def run_analysis(self, *args, **kwargs):
        """Runs the analysis and generates all plots and associated datasets.

        Returns:
            A list of Output objects.
        """
        # Finds the necessary data in the catalog.
        dataset = self.catalog.to_dataset_dict(...

        # Creates the plot and saves it as a png file.
        plt.plot(..
        plt.savefig(png_file)
        return [Output(dataset, png_file),]
```
