# script to make the MDTF runtime configs for each realm/freq to run requested PODs
import sys
import os
import json
import copy

_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

def generate_configs(config: dict, out_dir, catalog):
    # load pod information and template config file
    if not config['custom_pod_info_json']:
        pod_info_file = os.path.join(_FILE_PATH, '..', 'data/pod_info.json')
    else:
        pod_info_file = config['custom_pod_info_json']    
    try:
        with open(pod_info_file) as f:
            pod_info = json.load(f)
    except:
        print(f'ERROR: failed to load {pod_info_file}')
    template_file = os.path.join(_FILE_PATH, '..', 'data/template_config.jsonc')
    try:
        with open(template_file) as f:
            template_config = json.load(f)     
    except:
        print(f'ERROR: failed to load {template_file}')

    # add generic information to template
    template_config['DATA_CATALOG'] = catalog
    template_config['WORK_DIR'] = os.path.join(out_dir, "mdtf")
    template_config['case_list']['case_name']['startdate'] = str(config['data_range'][0])
    template_config['case_list']['case_name']['enddate'] = str(config['data_range'][1])

    if config['use_gfdl_mdtf_env']:
        template_config['OBS_DATA_ROOT'] = '/home/oar.gfdl.mdtf/mdtf/inputdata/obs_data/'
        template_config['conda_root'] = '/home/oar.gfdl.mdtf/miniconda3/'
    else:
        template_config['OBS_DATA_ROOT'] = config['obs_data_path']
    
    # get only requested pod info
    config_files = {}
    for p in config['pods']:
        if p in pod_info:
            config_name = f'{p}_config'
            config_realm = pod_info[p]['realm']
            config_files[config_name] = copy.deepcopy(template_config)
            config_files[config_name]['case_list']['case_name']['realm'] = config_realm
            config_files[config_name]['case_list'][config_realm] = config_files[config_name]['case_list'].pop('case_name')
            config_files[config_name]['pod_list'].append(p)
        else:
            print(f'WARNING: {p} is not a supported POD; skipping requested POD')

    # write out config files
    config_dir = os.path.join(out_dir, 'mdtf', 'config')
    os.makedirs(config_dir)
    for c in config_files:
        with open(os.path.join(config_dir, f"{c}.jsonc"), "w") as f:
            f.write(json.dumps(config_files[c], indent=2)) 

    return
