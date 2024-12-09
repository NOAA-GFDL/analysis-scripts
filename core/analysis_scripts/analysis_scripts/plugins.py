import importlib
import inspect
import pkgutil
import sys

from .base_class import AnalysisScript


class _PathAdjuster(object):
    """Helper class to adjust where python tries to import modules from."""
    def __init__(self, path):
        """Initialize the object.

        Args:
            path: Path to look in for python modules and packages.
        """
        self.path = path
        self.old_sys_path = sys.path

    def __enter__(self):
        """Adjusts the sys path so the modules and packages can be imported."""
        if self.path not in sys.path:
            sys.path.insert(0, self.path)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Undoes the sys path adjustment."""
        if sys.path != self.old_sys_path:
            sys.path = self.old_sys_path


# Dictionary of found plugins.
discovered_plugins = {}


def find_plugins(path=None):
    """Find all installed python modules with names that start with 'freanalysis_'.

    Args:
        path: Custom directory where modules and packages are installed.
    """
    if path:
        path = [path,]
    for finder, name, ispkg in pkgutil.iter_modules(path):
        if name.startswith("freanalysis_"):
            if path:
                with _PathAdjuster(path[0]):
                    discovered_plugins[name] = importlib.import_module(name)
            else:
                discovered_plugins[name] = importlib.import_module(name)


# Update plugin dictionary.
find_plugins()


class UnknownPluginError(BaseException):
    """Custom exception for when an invalid plugin name is used."""
    pass


def _plugin_object(name):
    """Searches for a class that inherits from AnalysisScript in the plugin module.

    Args:
        name: Name of the plugin.

    Returns:
        The object that inherits from AnalysisScript.

    Raises:
        KeyError if the input name does not match any installed plugins.
        ValueError if no object that inhertis from AnalysisScript is found in the
            plugin module.
    """
    # Loop through all attributes in the plugin package with the input name.
    try:
        plugin_module = discovered_plugins[name]
    except KeyError:
        raise UnknownPluginError(f"could not find analysis script plugin {name}.")

    for attribute in vars(plugin_module).values():
       # Try to find a class that inherits from the AnalysisScript class.
       if inspect.isclass(attribute) and AnalysisScript in attribute.__bases__:
           # Instantiate an object of this class.
           return attribute()
    raise ValueError(f"could not find compatible object in {name}.") 


def available_plugins():
    """Returns a list of plugin names."""
    return sorted(list(discovered_plugins.keys()))


def list_plugins():
    """Prints a list of plugin names."""
    names = available_plugins()
    if names:
        print("\n".join(["Available plugins:", "-"*32] + names))
    else:
        print("Warning: no plugins found.")


def plugin_requirements(name):
    """Returns a JSON string detailing the plugin's requirement metadata.

    Args:
        name: Name of the plugin.

    Returns:
        JSON string of metadata.
    """
    return _plugin_object(name).requires()


def run_plugin(name, catalog, png_dir, config=None, reference_catalog=None):
    """Runs the plugin's analysis.

    Args:
        name: Name of the plugin.
        catalog: Path to the data catalog.
        png_dir: Directory where the output figures will be stored.
        config: Dictionary of configuration values.
        catalog: Path to the catalog of reference data.

    Returns:
        A list of png figure files that were created by the analysis.
    """
    return _plugin_object(name).run_analysis(catalog, png_dir, config, reference_catalog)
