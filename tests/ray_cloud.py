#!/usr/bin/env python

from scripts import gen_intake_gfdl
import sys

input_path = "archive/oar.gfdl.mdtf/MDTF-examples/mdtf-time-slice-example/gfdl.ncrc5-deploy-prod-openmp/pp"
output_path = "gfdl_analysis_citest"
sys.argv = ['INPUT_PATH', input_path, output_path]
print(sys.argv)
gen_intake_gfdl.main()
