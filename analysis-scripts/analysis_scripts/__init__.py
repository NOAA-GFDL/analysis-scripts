import json
from argparse import ArgumentParser
from os import getenv
from pathlib import Path

from requests import get, post
from yaml import safe_load

from freanalysis.plugins import run_plugin


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

    def get_request(url):
        """Sends a get request to the input url.

        Args:
            url: String url to send the get request to.

        Returns:
            Dictionary of response body data.

        Raises:
            ValueError if the response does not return status 200.
        """
        response = get(url)
        if response.status_code != 200:
            print(response.text)
            return ValueError("get from {url} failed.")
        return response.json()


    def post_request(url, data):
        """Post an http request to dora.

        Args:
            url: String url to post the http request to.
            data: Dictionary of data that will be passed as json in the body of the request.

        Returns:
            String text from the http response.

        Raises:
            ValueError if the response does not return status 200.
        """
        response = post(url, json=data, auth=(getenv("DORA_TOKEN"), None))
        if response.status_code != 200:
            print(response.text)
            raise ValueError(f"post to {url} with {data} failed.")
        return response.text


    def parse_experiment_yaml(path):
        """Parse the experiment yaml and return a dictionary of the data needed to add the
        experiment to dora.

        Args:
            path: Path to the experiment yaml.

        Returns:
            Dictionary of data needed to add the experiment to dora.

        Raises:
            ValueError if the experiment owner cannot be determined.
        """
        with open(path) as file_:
            yaml_ = safe_load(file_)

            # Determine the username - is this a hack?
            history_path_parts = Path(yaml_["directories"]["history_dir"]).parts
            user = history_path_parts[2]
            if user == "$USER":
                user = getenv(user[1:])
            if not user:
                raise ValueError(f"Could not identify user {user}.")

            # Expand the paths.
            pp_path = yaml_["directories"]["pp_dir"].replace("$USER", user)
            database_path = pp_path.replace("archive", "home").replace("pp", "db") # Nasty hack.
            analysis_path = yaml_["directories"]["analysis_dir"].replace("$USER", user)

            # Get the model type from the history directory path - is there a better way?
            model_type = history_path_parts[3].upper() # Nasty hack.

            # Get the starting and ending years and total length of the experiment.
            start = int(yaml_["postprocess"]["settings"]["pp_start"])
            stop = int(yaml_["postprocess"]["settings"]["pp_stop"])
            length = stop - start + 1
    
            return {
                "expLength": length,
                "expName": yaml_["name"],
                "expType": yaml_["name"].split("_")[-1].upper(), # Nasty hack.
                "expYear": start,
                "modelType": model_type,
                "owner": user,
                "pathAnalysis": analysis_path,
                "pathDB": database_path,
                "pathPP": pp_path,
                "pathXML": path,
                "userName": user,
            }


    def get_dora_experiment_id(path):
        """Gets the experiment id using a http request after parsing the experiment yaml.

        Args:
            path: Path to the experiment yaml.
    
        Returns:
            Integer dora experiment id.

        Raises:
            ValueError if the unique experiment (identified by the pp directory path)
            cannot be found.
        """
        data = parse_experiment_yaml(path)
    #   url = f"https://dora.gfdl.noaa.gov/api/search?search={data['owner']}"
        url = f"http://127.0.0.1:5000/api/search?search={data['owner']}"
        response = get_request(url)
        for experiment in response.values():
            if experiment["pathPP"] == data["pathPP"]:
                return int(experiment["id"])
        raise ValueError("could not find experiment with pp directory - {data['pathPP']}")


    def add_experiment_to_dora():
        """Adds the experiment to dora using a http request."""
        parser = ArgumentParser()
        parser.add_argument("experiment_yaml", help="Path to the experiment yaml.")
        args = parser.parse_args()

        # Parse the experiment yaml to get the data needed to add the experiment to dora.
        data = parse_experiment_yaml(args.experiment_yaml)

        # Add the experiment to dora.
    #   url = "https://dora.gfdl.noaa.gov/api/add-experiment"
        url = "http://127.0.0.1:5000/api/add-experiment"
        post_request(url, data)


    def run_analysis():
        """Runs the analysis script and writes the paths to the created figures to a yaml file."""
        parser = ArgumentParser()
        parser.add_argument("name", help="Name of the analysis script.")
        parser.add_argument("catalog", help="Path to the data catalog.")
        parser.add_argument("output_directory", help="Path to the output directory.")
        parser.add_argument("output_yaml", help="Path to the output yaml.")
        parser.add_argument("-c", "--config", help="Path to the configuration yaml.")
        args = parser.parse_args()

        # Create the directory for the figures.
        Path(args.output_directory).mkdir(parents=True, exist_ok=True)

        # Parse the configuration out of the yaml file.
        if args.config:
            with open(args.config) as file_:
                config_yaml = safe_load(file_)
                try:
                    configuration = config_yaml["analysis"][args.name]
                except KeyError:
                    configuration = None
        else:
            configuration = None

        # Run the analysis.
        figure_paths = run_plugin(
            args.name,
            args.catalog,
            args.output_directory,
            config=configuration,
        )

        # Write out the figure paths to a file.
        with open(args.output_yaml, "w") as output:
            output.write("figure_paths:\n")
            for path in figure_paths:
                output.write("  -{Path(path).resolve()}\n")


    def publish_analysis_figures():
        """Uploads the analysis figures to dora."""
        parser = ArgumentParser()
        parser.add_argument("name", help="Name of the analysis script.")
        parser.add_argument("experiment_yaml", help="Path to the experiment yaml file.")
        parser.add_argument("figures_yaml", help="Path to the yaml that contains the figure paths.")
        args = parser.parse_args()

        # Check to make sure that the experiment was added to dora and get it id.
        dora_id = get_dora_experiment_id(args.experiment_yaml)

        # Parse out the list of paths from the input yaml file and upload them.
        url = "https://dora.gfdl.noaa.gov/api/add-png"
        data = {"id": dora_id, "name": args.name}
        with open(args.figures_yaml) as file_:
            paths = safe_load(file_)["figure_paths"]
            for path in paths:
                data["path"] = path
                post_request(url, data)


#if __name__ == "__main__":
#   add_experiment_to_dora()
#    print(get_dora_experiment_id("../../../c96L65_am5f7b12r1_amip.yaml"))
