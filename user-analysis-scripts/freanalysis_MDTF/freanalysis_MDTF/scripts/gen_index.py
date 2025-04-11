# script to create a simple index.html for automated mdtf runs
import sys
import os
import json
import shutil

_FILE_PATH = os.path.dirname(os.path.realpath(__file__))

def generate_index(config: dict, out_dir):
    # load pod information
    if not config['custom_pod_info_json']:
        pod_info_file = os.path.join(_FILE_PATH, '..', 'data/pod_info.json')
    else:
        pod_info_file = config['custom_pod_info_json'] 
    try:
        with open(pod_info_file) as f:
            pod_info = json.load(f)
    except:
        print(f'ERROR: failed to load {pod_info_file}')

    # copy over required files for the html
    files = ['index.html', 'mdtf_diag_banner.png']
    for f in files:
        shutil.copy(os.path.join(_FILE_PATH, f), out_dir)    

    index_file = open(f'{out_dir}/index.html', 'a')

    pod_htmls = {}
    pods = [p for p in pod_info]
    mdtf_outputs = [os.path.join(out_dir, d) for d in os.listdir(out_dir) if 'MDTF_output' in d]

    for d in mdtf_outputs:
        list_d = os.listdir(d)
        for p in pods:
            if p in list_d:
                pod_dir = os.path.join(d, p)
                file_path = os.path.join(pod_dir, f'{p}.html')
                if os.path.exists(file_path):
                    print(p)
                    index_file.write(f'<a href="{file_path}"> {p} </a> <br>')
            
    index_file.close()

    return
