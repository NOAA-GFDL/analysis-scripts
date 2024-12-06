import json


class AnalysisScript(object):
    """Abstract base class for analysis scripts.  User-defined analysis scripts
       should inhert from this class and override the requires and run_analysis methods.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        """Instantiates an object.  The user should provide a description and title."""
        raise NotImplementedError("you must override this function.")
        self.description = None
        self.title = None

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string describing the metadata.
        """
        raise NotImplementedError("you must override this function.")
        return json.dumps("{json of metadata MDTF format.}")

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
        raise NotImplementedError("you must override this function.")
        return ["figure1.png", "figure2.png",]
