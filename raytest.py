#!/home/a1r/env/bin/python

from freanalysis.plugins import list_plugins, plugin_requirements, run_plugin
name = "freanalysis_clouds"
reqs = plugin_requirements(name)
print(reqs)
catalog = "/home/a1r/cat/canopy/am5f7b11r0/c96L65_am5f7b11r0_amipnew.json" #"/home/a1r/cat/canopy/am5f7b11r0/c96L65_am5f7b11r0_amipn0513.json" 
run_plugin(name, catalog, "pngs")
