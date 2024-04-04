#!/usr/bin/env python3

din_loc_root = '/lustre/orion/cli115/world-shared/e3sm/inputdata'
grid_root = f'{din_loc_root}/share/meshes/homme'
scrip_grids = {
    'ne30pg2'  : f'{grid_root}/ne30pg2_scrip_20200209.nc',
    'ne120pg2' : f'{grid_root}/ne120pg2_scrip_20221012.nc',
    'ne256pg2' : f'{grid_root}/ne256pg2_scrip_20221011.nc',
    'ne1024pg2': f'{grid_root}/ne1024pg2_scrip_20221011.nc',
}

def get_scrip_grid(ds, grid_name):
    if grid_name in scrip_grids.keys():
        return scrip_grids[grid_name]
    else:
        raise RuntimeError(f'{grid_name} not found in dict of known grid files')
