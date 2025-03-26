import os

def grab_plots(out_dir) -> list:
    plots = []
    for dirpath, _, filenames in os.walk(out_dir):
        for filename in filenames:
            if filename.lower().endswith(('.png')) and filename != 'mdtf_diag_banner.png':
                plot_path = os.path.join(dirpath, filename)
                plots.append(plot_path)
    return plots
