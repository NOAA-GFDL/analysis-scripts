from analysis_scripts import AnalysisScript
import freanalysis_MDTF
from freanalysis_MDTF.scripts import gen_config, gen_index, grab_plots
import MDTF_diagnostics
MDTF_PACKAGE_PATH = MDTF_diagnostics.__path__[0]
import os
import shutil
import json
import subprocess

_PACKAGE_PATH = freanalysis_MDTF.__path__[0]

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

    # TODO: I'm not entirely sure what to put here in the case of the MDTF.
    # The MDTF will check for vars on it's own, so I'm not sure the what the best option will be!
    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string describing the metadata.
        """
        return json.dumps({
            "settings": {
                "activity_id": "the dataset convention",
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

    def run_analysis(self, catalog: str, out_dir, config=None, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a model output catalog
            out_dir: Directory to run and store the MDTF and output in (this replaces png_dir from the base class) 
            reference_catalog: Path to a catalog of reference data. (OPTIONAL)

        Returns:
            A list of png figures.
        """
        # overwrite out_dir if dir exists
        output_dir = os.path.join(out_dir, 'mdtf')
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        # generate runtime_config files for each realm and freq combination
        gen_config.generate_configs(config, out_dir, catalog)
       
        # decide which env to use
        if config['use_gfdl_mdtf_env']:
            cmd = [
                '/home/oar.gfdl.mdtf/mdtf/MDTF-diagnostics',
                '-f'
            ] 
        else:
            cmd = [
                'python',
                mdtf_script_path,
                '-f'
            ]
        # run each config file
        mdtf_script_path = os.path.join(MDTF_PACKAGE_PATH, "mdtf_framework.py")
        for f in os.listdir(os.path.join(output_dir, 'config')):
            # decide which env to use
            if config['use_gfdl_mdtf_env']:
                cmd = [
                    '/home/oar.gfdl.mdtf/mdtf/MDTF-diagnostics/mdtf',
                    '-f',
                    os.path.join(output_dir, 'config', f)
                ]
            else:
                cmd = [
                    'python',
                    mdtf_script_path,
                    '-f',
                    os.path.join(output_dir, 'config', f)
                ]
            subprocess.run(cmd)

        gen_index.generate_index(config, output_dir)    

        return grab_plots.grab_plots(output_dir)
