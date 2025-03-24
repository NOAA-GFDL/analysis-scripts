from analysis_scripts import available_plugins, plugin_requirements, run_plugin


# Create a data catalog.
# Some code to create a data "catalog.json" ...

# Show the installed plugins
print(available_plugins())

# Run the 'example' MDTF POD
name = "freanalysis_MDTF"  # Name of the custom analysis script you want to run.
config_file = '/local/home/Jacob.Mims/djptest/mdtf/config/atmos_cmip_day_config.jsonc'
figures = run_plugin(name, "catalog.json", "pngs", config_file)
