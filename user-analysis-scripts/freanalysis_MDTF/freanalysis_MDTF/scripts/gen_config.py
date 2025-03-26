# script to make the MDTF runtime configs for each realm/freq to run requested PODs
import sys
import os
import json
import copy

_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

def generate_configs(config: dict, out_dir, catalog):
    
    # load pod information and template config file
    pod_info_file = os.path.join(_FILE_PATH, '..', 'data/pod_info.json')    
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
    template_config['case_list']['case_name']['startdate'] = config['startyr']
    template_config['case_list']['case_name']['enddate'] = config['endyr']

    # get only requested pod info
    config_names = []
    realms = []
    for p in config['pods']:
        if p in pod_info:
            realm = pod_info[p]['realm']
            realms.append(realm)
            freq = pod_info[p]['frequency']
            config_name = f'{realm}_{freq}_config'
            config_names.append(config_name)
        else:
            print(f'WARNING: {p} is not a supported POD; skipping requested POD')
    config_names = set(config_names)
    realms = set(realms)

    # create dict of config files
    config_files = {}
    for c in config_names:
        config_files[c] = copy.deepcopy(template_config)
        for r in realms:
            if r in c:
                config_files[c]['case_list']['case_name']['realm'] = r
                config_files[c]['case_list'][r] = config_files[c]['case_list'].pop('case_name')
    
    # add pods to cooresponding config file
    for p in config['pods']:
        config_file = f"{pod_info[p]['realm']}_{pod_info[p]['frequency']}_config"    
        config_files[config_file]['pod_list'].append(p)

    # write out config files
    config_dir = os.path.join(out_dir, 'mdtf', 'config')
    os.makedirs(config_dir)
    for c in config_files:
        with open(os.path.join(config_dir, f"{c}.jsonc"), "w") as f:
            f.write(json.dumps(config_files[c], indent=2)) 

    return
