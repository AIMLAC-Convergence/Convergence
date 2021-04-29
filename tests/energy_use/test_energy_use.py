# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 08:00:49 2021

@author: c1616132
"""
import pytest

from Energy_use import total_energy_sum, temp_cost

@pytest.mark.parametrize("T,expect",[
    ([1,1,-7,1,2,16,2,3,3,4,5,6,6,5,4,3,3,2,2,2,1,1,1,1],[636.0])
    ])
def test_temp_cost(T,expect):
    output = temp_cost(T)
    
    assert output == expect
    

@pytest.mark.parametrize("weekday2,date2,date3,f,total_energy,expect",[
    (1,4,15,None,4800,5691.0)
    ])
def test_total_energy_sum(weekday2,date2,date3,f,total_energy,expect):
    output = total_energy_sum(weekday2,date2,date3,f,total_energy)
    
    assert output == expect
