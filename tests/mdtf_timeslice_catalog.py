#!/usr/bin/env python

from scripts import gen_intake_gfdl
import sys

sys.argv = ['input_path','--config', '/home/runner/work/analysis-scripts-fork/analysis-scripts-fork/tests/mdtf_timeslice_catalog.yaml']
print(sys.argv)
gen_intake_gfdl.main()
