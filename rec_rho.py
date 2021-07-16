#!/usr/bin/env python3
# -*- coding: utf-8 -

import os

import basf2 as b2
import modularAnalysis as ma

from variables import variables
import variables.utils as vu
import variables.collections as vc

path_files = {
    'sgn' : '/home/people/jmedrala/data_rho'
}
sample = 'sgn'


input_files = sorted([os.path.join(path_files[sample], i)
                      for i in os.listdir(path_files[sample])])[:2]
output_file = f'data_rho/tree_{sample}_KA.root'


# If we are using data, we need to specify the proper global tag
#b2.reset_database()
#b2.use_database_chain()
#b2.use_central_database("data_reprocessing_prompt_bucket4b")


mypath = b2.create_path()
ma.inputMdstList("default", input_files, path=mypath)

# ma.printDataStore(path=mypath)

# reconstruct basic particles
from stdCharged import stdK, stdPi, stdMu, stdE
stdK("loose", path=mypath)
stdPi("loose", path=mypath)
stdMu("loose", path=mypath)
stdE("loose", path=mypath)
from stdPi0s import stdPi0s
stdPi0s("loose", path=mypath)

#Reconstruct the rho+
rhocuts = '0.7 < M < 0.9'
ma.reconstructDecay('rho+:pipi -> pi+:loose pi0:loose', cut=rhocuts,
                    dmID=1, path=mypath)

# Reconstruct the D0
D0cuts = '1.8 < M < 1.9'
ma.reconstructDecay('D0:Kpi -> K+:loose pi-:loose', cut=D0cuts,
                    dmID=1, path=mypath)
                 
# Reconstruct the D*+
Dstcuts = '1.99 < M < 2.05'
ma.reconstructDecay('D*-:D0pi -> D0:Kpi pi+:loose', Dstcuts,
                    dmID=1, path=mypath)

# Reconstruct B
Bcuts = '4.9 < M < 5.7'
ma.reconstructDecay('B0:Dstarrho -> D*-:D0pi rho+:pipi', cut=Bcuts,
                    dmID=1, path=mypath)

# Apply a decay-tree fit
import vertex as vx
vx.vertexTree('B0:Dstarrho', conf_level=0, updateAllDaughters=True,
              ipConstraint=True, path=mypath)

# Define aliases for the vertex results
variables.addAlias('B_vtxChi2','extraInfo(chiSquared)')
variables.addAlias('B_vtxNDF','extraInfo(ndf)')

ma.rankByHighest(particleList='B0:Dstarrho', variable='B_vtxChi2',
                 outputVariable='B_rank', path=mypath)
variables.addAlias('B_rank', 'extraInfo(B_rank)')

# Do MC matching for the B
ma.matchMCTruth('B0:Dstarrho', path=mypath)

# Event Shape variables
ma.buildEventShape(path=mypath)


# NTuple

vars_basic = (vc.kinematics + vc.inv_mass + vc.mc_truth +
              ['d0', 'd0Err', 'z0', 'z0Err'])

variables.addAlias('dmID', 'extraInfo(decayModeID)')

vars_Dst = vars_basic + vc.vertex + vc.mc_vertex + ['dM', 'dmID']

vars_rho = vars_basic + vc.vertex + vc.mc_vertex + ['dM']

vars_B = (vars_basic + vc.vertex + vc.mc_vertex + vc.deltae_mbc +
          ['dM'])

vars_fs_particles = vars_basic + vc.pid + vc.track

list_variables = vc.event_shape + ['B_rank', 'B_vtxChi2', 'B_vtxNDF']

list_variables += vu.create_aliases_for_selected(vars_B,
                                             '^B0 ==> D*-  rho+',
                                             prefix = ['B'])

list_variables += vu.create_aliases_for_selected(vars_Dst,
                                             'B0 ==> ^D*- rho+',
                                             prefix = ['Dst'])

list_variables += vu.create_aliases_for_selected(vars_rho,
                                             'B0 ==> D*- ^rho+',
                                             prefix = ['rho'])

list_variables += vu.create_aliases_for_selected(vars_fs_particles,
                                                 'B0 ==> [D*- ==> ^D0 ^pi+] [rho+ ==> ^pi+ ^pi0]',
                                                 prefix = ['D0', 'pi1', 'pi2', 'pi3'])


ma.variablesToNtuple('B0:Dstarrho', treename='tree', filename=output_file,
                     path=mypath, variables=sorted(list_variables))


b2.process(mypath)
print(b2.statistics)
