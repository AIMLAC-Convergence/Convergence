# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:22:38 2021

@author: davem
"""
import pytest
import sys
sys.path.insert(0, '../../convergence-modules/energy_production/')
import energy_production as ep
import pandas as pd
import yaml
@pytest.mark.parametrize("DNI, DHI, z, A, intLength, sP",[
    (10.,10.,45., 89.,1800., yaml.load('params.yaml', Loader=yaml.FullLoader) )
    ])
def test_solarEnergy(DNI, DHI, z, A, intLength, sP):
    output = ep.solarEnergy(DNI, DHI, z, A, intLength, sP['params']['solar'])
    assert output == 0
