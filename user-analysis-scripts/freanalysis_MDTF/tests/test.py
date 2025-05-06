from analysis_scripts import available_plugins, plugin_requirements, run_plugin

# show the installed plugins
print(available_plugins())

# run the 'example' MDTF POD
name = "freanalysis_MDTF"  # name of the custom analysis script you want to run
catalog_path = "/work/c2b/freanalysis_MDTF/catalog.json" # absolute path to catalog .json file
out_dir = "/work/c2b/freanalysis_MDTF_output" # absolute path to dir that you would like the MDTF to run and output
config={
    'pods': ['Wheeler_Kiladis'], # list of pods you'd like to run
    'startyr': '1990', # year to start analysis
    'endyr': '1995', # year to end analysis
    'custom_pod_info_json': "",
    'data_range': [1990, 1995],
    'use_gfdl_mdtf_env': True
}
figures = run_plugin(name, catalog_path, out_dir, config=config)
print(figures)
