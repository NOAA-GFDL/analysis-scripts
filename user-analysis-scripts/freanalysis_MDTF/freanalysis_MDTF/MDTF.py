from analysis_scripts import AnalysisScript
from freanalysis_MDTF import hello
import os
import json

class MDTFAnalysisScript(AnalysisScript):
    """Custom Analysis script for some task.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        """Instantiates an object.  The user should provide a description and title."""
        self.description = "Wrapper to access the analysis framework and collection of process-oriented diagnostics for weather and climate simulations "
        self.title = "MDTF-diagnostics"

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string describing the metadata.
        """
        return json.dumps({
            "settings": {
                "activity_id": "he dataset convention",
            },
            "dimensions": {
                # These are just examples, you can put more/different ones.
                "lat": {"standard_name": "latitude"},
                "lon": {"standard_name": "longitude"},
                "time": {"standard_name": "time"}
            },
            "varlist": {
            }
        })

    def run_analysis(self, catalog, png_dir, config_file, config=None, reference_catalog=None):
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
        hello.hello()
        print(config_file)
        os.system(f'mdtf_framework.py -f {config_file}')
        return ["figure1.png", "figure2.png",]
