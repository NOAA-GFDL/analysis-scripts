from collections import namedtuple

import intake
import intake_esm


Metric = NamedTuple("Metric", ["name", "frequency"])
Output = NamedTuple("Output", ["dataset", "png_path"])


class AnalysisScript(object):
    """Abstract base class for analysis scripts.  User-defined analysis scripts
       should inhert from this class and override the requires and run_analysis methods.

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
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A list of Metric objects.
        """
        raise NotImplementedError("you must override this function.")
        return [Metric(None, None),]

    def run_analysis(self):
        """Runs the analysis and generates all plots and associated datasets.

        Returns:
            A list of Output objects.
        """
        raise NotImplementedError("you must override this function.")
        return [Output(None, None),]
