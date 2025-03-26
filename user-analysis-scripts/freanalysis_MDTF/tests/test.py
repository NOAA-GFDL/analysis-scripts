from analysis_scripts import available_plugins, plugin_requirements, run_plugin

# show the installed plugins
print(available_plugins())

# run the 'example' MDTF POD
name = "freanalysis_MDTF"  # name of the custom analysis script you want to run
catalog_path = '/local/home/Jacob.Mims/djptest/mdtf/catalog.json' # absolute path to catalog .json file
out_dir = '/local/home/Jacob.Mims/analysistest/' # absolute path to dir that you would like the MDTF to run and output
config={
    'pods': ['example'], # list of pods you'd like to run
    'startyr': '1990', # year to start analysis
    'endyr': '1995' # year to end analysis
}
figures = run_plugin(name, catalog_path, out_dir, config=config)
print(figures)
