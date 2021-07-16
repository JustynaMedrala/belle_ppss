#!/bin/bash

source /cvmfs/belle.cern.ch/tools/b2setup release-04-02-09

basf2 generate.py -n 15000
