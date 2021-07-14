#!/usr/bin/env python3
# -*- coding: utf-8 -

import basf2 as b2

out_file ='B02D*-pi+.mdst.root'
in_file='test3.dec'

path = b2.create_path()
setter = path.add_module('EventInfoSetter', evtNumList=[50])
b2.print_params(setter)


from ROOT import Belle2
generator = path.add_module("EvtGenInput", userDECFile=in_file)

b2.print_params(generator)


from simulation import add_simulation
add_simulation(path)

from reconstruction import add_reconstruction
add_reconstruction(path)

from reconstruction import add_mdst_output
add_mdst_output(path, filename=out_file)

b2.process(path)
