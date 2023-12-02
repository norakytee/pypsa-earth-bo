
import pypsa
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess

network = 'networks/elec_s_all_ec_lcopt_Co2L-1H.nc'
n = pypsa.Network(network)

scale_demand_old = {
    2022: 1.039555791,
    2023: 1.037440228,
    2024: 1.030106894,
    2025: 1.029322163,
    2026: 1.051886792,
    2027: 1.044491339,
    2028: 1.044448186,
    2029: 1.044491013,
    2030: 1.044447874,
    2031: 1.044477281,
    2032: 1.044422438,
    2033: 1.040027091,
    2034: 1.039984371,
    2035: 1.040012523,
    'back':0.569269673, # scaling factor for scaling from 2035 to 2021
    'direct' : 1.7566367 # scaling factor from 2021 to 2035
}


scale_demand = {
    2024: 1.058723565,
    2025: 1.060816836,
    2026: 1.033372562,
    2027: 1.027658017,
    2028: 1.032454682,
    2029: 1.030974469,
    2030: 1.030564438,
    2031: 1.029585799,
    2032: 1.029366414,
    2033: 1.048001634,
    2034: 1.041580000,
    2035: 1.041580000,
    2036: 1.041580000,
    2037: 1.041580000,
    'back':0.569269673, # scaling factor for scaling from 2035 to 2021
    'direct' : 1.7566367 # scaling factor from 2021 to 2035
}

scale_cost_sudden = {
    ('OCGT', 2024): 1.0,
    ('OCGT', 2025): 1.0,
    ('OCGT', 2026): 0.24,
    ('OCGT', 2027): 1.0,
    ('OCGT', 2028): 1.0,
    ('OCGT', 2029): 1.0,
    ('OCGT', 2030): 1.0,
    ('OCGT', 2031): 1.0,
    ('OCGT', 2032): 1.0,
    ('OCGT', 2033): 1.0,
    ('OCGT', 2034): 1.0,
    ('OCGT', 2035): 1.0,
    ('OCGT', 2036): 1.0,
    ('OCGT', 2037): 1.0,

    ('CCGT', 2024): 1.0,
    ('CCGT', 2025): 1.0,
    ('CCGT', 2026): 0.27,
    ('CCGT', 2027): 1.0,
    ('CCGT', 2028): 1.0,
    ('CCGT', 2029): 1.0,
    ('CCGT', 2030): 1.0,
    ('CCGT', 2031): 1.0,
    ('CCGT', 2032): 1.0,
    ('CCGT', 2033): 1.0,
    ('CCGT', 2034): 1.0,
    ('CCGT', 2035): 1.0,
    ('CCGT', 2036): 1.0,
    ('CCGT', 2037): 1.0,

    ('oil', 2024): 1.0,
    ('oil', 2025): 1.0,
    ('oil', 2026): 0.29,
    ('oil', 2027): 1.0,
    ('oil', 2028): 1.0,
    ('oil', 2029): 1.0,
    ('oil', 2030): 1.0,
    ('oil', 2031): 1.0,
    ('oil', 2032): 1.0,
    ('oil', 2033): 1.0,
    ('oil', 2034): 1.0,
    ('oil', 2035): 1.0,
    ('oil', 2036): 1.0,
    ('oil', 2037): 1.0,
}

scale_cost_gradual = {
    ('OCGT', 2024): 0.82,
    ('OCGT', 2025): 0.85,
    ('OCGT', 2026): 0.87,
    ('OCGT', 2027): 0.88,
    ('OCGT', 2028): 0.89,
    ('OCGT', 2029): 0.90,
    ('OCGT', 2030): 0.91,
    ('OCGT', 2031): 0.92,
    ('OCGT', 2032): 0.93,
    ('OCGT', 2033): 0.93,
    ('OCGT', 2034): 0.94,
    ('OCGT', 2035): 0.94,
    ('OCGT', 2036): 0.94,
    ('OCGT', 2037): 0.95,

    ('CCGT', 2024): 0.84,
    ('CCGT', 2025): 0.86,
    ('CCGT', 2026): 0.88,
    ('CCGT', 2027): 0.89,
    ('CCGT', 2028): 0.90,
    ('CCGT', 2029): 0.91,
    ('CCGT', 2030): 0.92,
    ('CCGT', 2031): 0.92,
    ('CCGT', 2032): 0.93,
    ('CCGT', 2033): 0.93,
    ('CCGT', 2034): 0.94,
    ('CCGT', 2035): 0.94,
    ('CCGT', 2036): 0.94,
    ('CCGT', 2037): 0.95,

    ('oil', 2024): 0.854,
    ('oil', 2025): 0.873,
    ('oil', 2026): 0.887,
    ('oil', 2027): 0.898,
    ('oil', 2028): 0.908,
    ('oil', 2029): 0.916,
    ('oil', 2030): 0.922,
    ('oil', 2031): 0.928,
    ('oil', 2032): 0.933,
    ('oil', 2033): 0.937,
    ('oil', 2034): 0.941,
    ('oil', 2035): 0.944,
    ('oil', 2036): 0.947,
    ('oil', 2037): 0.950,
}

def read_network_file():
    network = 'networks/elec_s_all_ec_lcopt_Co2L-1H.nc'
    n = pypsa.Network(network)
    return n
   

# Function that implements all yearly changes

def yearly_changes(n,year):
    print(year)
    # ------- DEMAND ---------
    upscaling_factor = scale_demand[year]
    n.loads_t.p_set = n.loads_t.p_set * upscaling_factor


    # ------- EMISSIONS -------
    #n.global_constraints.constant = emission_limit[year]
    #display(n.global_constraints.constant)

    #-------- COSTS ---------
    indexes = {}
    for car in ['OCGT', 'CCGT', 'oil']:
        mask = n.generators['carrier'] == car
        indexes[car] = n.generators.index[mask].tolist()
    for car in indexes:
        n.generators.loc[indexes[car], 'marginal_cost'] = n.generators.loc[indexes[car], 'marginal_cost'] / scale_cost_sudden[(car, year)]

    # ------- GENERATOR EXTENSTION -----
    solved_network = f'{scen_folder}/{scen}_{year-1}.nc'
    m = pypsa.Network(solved_network)
    additional_exp= m.generators.p_nom_opt - m.generators.p_nom
    # replace negative values with 0
    for index, value in additional_exp.items():
        if value < 0:
            additional_exp[index]=0
    # add expansion to previous network
    n.generators.p_nom = n.generators.p_nom.add(additional_exp, fill_value=0)
    n.generators.p_nom_min = n.generators.p_nom_min.add(additional_exp, fill_value=0)
    #display(n.generators.p_nom)


    # ------- STORES ----------
    additional_stores = m.stores.e_nom_opt - m.stores.e_nom
    additional_stores
    n.stores.e_nom = n.stores.e_nom.add(additional_stores, fill_value = 0)
    n.stores.e_nom_min = n.stores.e_nom_min.add(additional_stores, fill_value = 0)
    #display(n.stores.e_nom.sum())


    # ------- LINKS -------
    additional_links = m.links.p_nom_opt - m.links.p_nom
    additional_links
    n.links.p_nom = n.links.p_nom.add(additional_links, fill_value = 0)
    n.links.p_nom_min = n.links.p_nom_min.add(additional_links, fill_value = 0)
    #display(n.links.p_nom.sum())


    # ------- DECOM ---------
    #for index,value in decom[year].items():
    #    n.generators.loc[index, 'p_nom'] = n.generators.loc[index].p_nom - value
    #    n.generators.loc[index, 'p_nom_min'] = n.generators.loc[index].p_nom_min - value

    # -------- EXPANSION ----------
    # for index,value in expansion[year].items():
    #     n.generators.loc[index, 'p_nom_min'] = n.generators.loc[index].p_nom_min + value

    # ------- HYDRO-DECOM-------- # is done seperately, because the  code is different
    #if year == 2032:
    #    n.storage_units.loc['BO 2 hydro','p_nom'] = n.storage_units.loc['BO 2 hydro'].p_nom - 2.55

    # ------- SAVING ----------
    n.export_to_netcdf('networks/elec_s_all_ec_lcopt_Co2L-1H.nc')


# Function that renames the results file and moves it to the scenario folder

def rename_results_file(year):
    current_location = 'results/networks/'
    old_filename = "elec_s_all_ec_lcopt_Co2L-1H.nc"
    new_filename = f"{scen}_{year}.nc"
    new_location = f'{scen_folder}/'

    # Create the full paths for the old and new files
    old_file_path = os.path.join(current_location, old_filename)
    new_file_path = os.path.join(new_location, new_filename)

    # Rename the file
    os.rename(old_file_path, new_file_path)



scen_folder = 'results_cost_sudden'
scen = 'cost_g'

# run for loop over all years
for year in range(2023, 2038):
    n = read_network_file()
    if year == 2023:
        subprocess.run(['snakemake', '-j', '6', 'solve_all_networks', '--unlock'])
        subprocess.run(['snakemake', '-j', '6', 'solve_all_networks'])
        rename_results_file(year)
    else:
        yearly_changes(n, year)
        subprocess.run(['snakemake', '-j', '6', 'solve_all_networks'])
        rename_results_file(year)


     

