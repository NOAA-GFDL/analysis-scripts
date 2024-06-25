from os import environ

from freanalysis.plugins import list_plugins, plugin_requirements, run_plugin


name = "freanalysis_clouds"
reqs = plugin_requirements(name)
print(reqs)
catalog = environ["CATALOG_JSON"]
run_plugin(name, catalog, "pngs")
