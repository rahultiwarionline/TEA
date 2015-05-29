#! /usr/bin/env python

# ******************************* START LICENSE *******************************
# Thermal Equilibrium Abundances (TEA), a code to calculate gaseous molecular
# abundances under thermochemical equilibrium conditions.
# 
# This project was completed with the support of the NASA Earth and
# Space Science Fellowship Program, grant NNX12AL83H, held by Jasmina
# Blecic, Principal Investigator Joseph Harrington. Project developers
# included graduate student Jasmina Blecic and undergraduate M. Oliver
# Bowman.
# 
# Copyright (C) 2014 University of Central Florida.  All rights reserved.
# 
# This is a test version only, and may not be redistributed to any third
# party.  Please refer such requests to us.  This program is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.
# 
# Our intent is to release this software under an open-source,
# reproducible-research license, once the code is mature and the first
# research paper describing the code has been accepted for publication
# in a peer-reviewed journal.  We are committed to development in the
# open, and have posted this code on github.com so that others can test
# it and give us feedback.  However, until its first publication and
# first stable release, we do not permit others to redistribute the code
# in either original or modified form, nor to publish work based in
# whole or in part on the output of this code.  By downloading, running,
# or modifying this code, you agree to these conditions.  We do
# encourage sharing any modifications with us and discussing them
# openly.
# 
# We welcome your feedback, but do not guarantee support.  Please send
# feedback or inquiries to both:
# 
# Jasmina Blecic <jasmina@physics.ucf.edu>
# Joseph Harrington <jh@physics.ucf.edu>
# 
# or alternatively,
# 
# Jasmina Blecic and Joseph Harrington
# UCF PSB 441
# 4111 Libra Drive
# Orlando, FL 32816-2385
# USA
# 
# Thank you for testing TEA!
# ******************************* END LICENSE *******************************

from readconf import *

# Setup for time/speed testing
if times:
    import time
    start = time.time()

import ntpath
import os
import shutil
import subprocess
import numpy as np
import sys
import balance
import iterate
import makeheader as mh

# =============================================================================
# This program runs TEA over an input file that contains only one T-P.
# The code retrieves the input file and the current directory name given by the 
# user. It sets locations of all necessary modules and directories that 
# will be used. Then, it executes the modules in the following order:
# makeheader.py, balance,py, and iterate.py. The final results with the input
# and the configuration files are saved in the results/ directory. The config
# file, abundances file, and input file used for this run will be placed in
# inputs/ directory.
#
# This module prints on screen the code progress: the current T-P line from
# the pre-atm file, the current iteration number, and informs the user that
# minimization is done.
# Example:
#  100
# Maximum iteration reached, ending minimization.
#
# The program is executed with in-shell inputs:
# runsingle.py <SINGLETP_INPUT_FILE_PATH> <DIRECTORY_NAME>
# Example: ../TEA/tea/runsingle.py ../TEA/doc/examples/singleTP/inputs/singleTP_Example.txt Single_Example
# =============================================================================
    
# Time / speed testing
if times:
    end = time.time()
    elapsed = end - start
    print("runsingle.py imports:  " + str(elapsed))

# Print license
print("\n\
================= Thermal Equilibrium Abundances (TEA) =================\n\
A code to calculate gaseous molecular abundances under thermochemical \n\
equilibrium conditions. \n\
Copyright (C) 2014 University of Central Florida.  All rights reserved. \n\
Test version, not for redistribution.  \n\
For feedback, contact: \n\
Jasmina Blecic <jasmina@physics.ucf.edu>        \n\
Joseph Harrington <jh@physics.ucf.edu>          \n\
========================================================================\n")

# Correct location_TEA name
if location_TEA[-1] != '/':
    location_TEA += '/'

if location_out[-1] != '/':
    location_out += '/'

# Retrieve user inputs file
infile = raw_input("Enter Input ATM File Location> ")

# If input file does not exist break
try:
    f = open(infile)
except:
    raise IOError ("\n\nSingle T-P input file does not exist.\n")

# Retrieve current output directory name given by user 
desc    = raw_input("What would you like the result directory to be named?> ")


# Check if output directory exists and inform user
if os.path.exists(location_out + desc):
    raw_input("  Output directory " + str(location_out + desc) + "/ already exists.\n"
              "  Press enter to continue and overwrite existing files,\n"
              "  or quit and choose another output name.\n")

# Set up locations of necessary scripts and directories of files
inputs_dir     = location_out + desc + "/inputs/"
thermo_dir     = location_TEA + "lib/gdata"
loc_balance    = location_TEA + "tea/balance.py"
loc_iterate    = location_TEA + "tea/iterate.py"
loc_headerfile = location_out + desc + "/headers/" + "header_" + desc + ".txt"
loc_outputs    = location_out + desc + "/outputs/"
loc_transient  = location_out + desc + "/outputs/" + "transient/"

# Create inputs directory
if not os.path.exists(inputs_dir): os.makedirs(inputs_dir)

# Check if config file exists in current working directory
TEA_config = 'TEA.cfg'
try:
    f = open(TEA_config)
except IOError:
    print("\nConfig file is missing. Place TEA.cfg in the working directory.\n")

# Inform user if TEA.cfg file already exists in inputs/ directory
if os.path.isfile(inputs_dir + TEA_config):
    print("  " + str(TEA_config) + " overwritten in inputs/ directory.")
# Copy TEA.cfg file to current inputs directory
shutil.copy2(TEA_config, inputs_dir + TEA_config)

# Inform user if abundances file already exists in inputs/ directory
head, abun_filename = ntpath.split(abun_file)
if os.path.isfile(inputs_dir + abun_filename):
    print("  " + str(abun_filename) + " overwritten in inputs/ directory.")
# Copy abundances file to inputs/ directory
shutil.copy2(abun_file, inputs_dir + abun_filename)

# Inform user if single T-P input file already exists in inputs/ directory
if os.path.isfile(inputs_dir + infile.split("/")[-1]):
    print("  " + str(infile.split("/")[-1]) + " overwritten in inputs/ directory.\n")
# Copy single T-P input file to inputs directory
shutil.copy2(infile, inputs_dir + infile.split("/")[-1])

# Times / speed check for pre-loop runtime
if times:
    new = time.time()
    elapsed = new - end
    print("pre-loop:           " + str(elapsed))

# Detect operating system for sub-process support
if os.name == 'nt': inshell = True    # Windows
else:               inshell = False   # OSx / Linux

# Execute main TEA loop
mh.make_singleheader(infile, desc, thermo_dir)
balanceFunction(loc_headerfile, desc, doprint)
iterator(loc_headerfile, desc, doprint)

# Save or delete headers file
if save_headers == False:
    shutil.rmtree(location_out + desc + "/headers/")

# Save or delete lagrange.py and lambdacorr.py outputs
if save_outputs:
    # Save directory for each T-P and its output files
    if not os.path.exists(loc_outputs): os.makedirs(loc_outputs)
    old_name = loc_transient
    new_name = loc_outputs + desc + "_singleTP_output" + loc_outputs[-1::]
    if os.path.exists(new_name):
        for file in os.listdir(new_name):
            os.remove(new_name + file)
        shutil.rmtree(new_name)
    os.rename(old_name, new_name)
else:
    shutil.rmtree(loc_outputs)

# Print on-screen
print("\n  Species abundances calculated.\n  Created results file.")

# Time / speed testing
if times:
    end = time.time()
    elapsed = end - start
    print("Overall run time:   " + str(elapsed) + " seconds")

