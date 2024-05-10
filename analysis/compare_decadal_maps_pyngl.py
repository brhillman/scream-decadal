#!/usr/bin/env python3

import xarray
from glob import glob
import sys, os
#from plot_map_pyngl import main as plot_map
from compare_maps_pyngl import main as compare_maps
from plot_maps_pyngl import main as plot_maps
from e3smplot.e3sm_utils import get_data, get_grid_name
from e3smplot.e3sm_utils import get_scrip_grid, get_mapping_file


#rundir = '/lustre/orion/cli115/proj-shared/brhillman/e3sm_scratch/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run'
rundir = '/global/cfs/cdirs/e3smdata/simulations/scream-decadal/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run'
obsdir = '/global/cfs/cdirs/e3smdata/observations/era5'
mapdir = '/global/cfs/cdirs/e3sm/bhillma/maps'

# Find output streams
print('Find output streams'); sys.stdout.flush()
output_streams = [os.path.basename(f).replace('.1994-10-01-00000.nc', '') for f in glob(f'{rundir}/*.1994-10-01-00000.nc')]
#output_stream = 'output.scream.decadal.1dailyMAX_ne1024pg2.MAX.ndays_x1' #'output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1'
#'output.scream.decadal.6hourlyINST_ne1024pg2.INSTANT.nhours_x6', 'output.scream.decadal.15minINST_ARM.INSTANT.nmins_x15', 'output.scream.decadal.1hourlyINST_ne1024pg2.INSTANT.nhours_x1', 'output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1', 'output.scream.decadal.3hourlyAVG_ne30pg2.AVERAGE.nhours_x3', 'output.scream.decadal.1dailyMIN_ne1024pg2.MIN.ndays_x1', 'output.scream.decadal.6hourlyINST_ne30pg2.INSTANT.nhours_x6', 'output.scream.decadal.6hourlyAVG_ne30pg2.AVERAGE.nhours_x6', 'decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1.elm.h1', 'output.scream.decadal.3hourlyINST_ne30pg2.INSTANT.nhours_x3', 'output.scream.decadal.1hourlyINST_ARM.INSTANT.nhours_x1', 'output.scream.decadal.1dailyMAX_ne1024pg2.MAX.ndays_x1', 'output.scream.decadal.1dailyAVG_ne1024pg2.AVERAGE.ndays_x1'
output_streams = ('output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1',)
for output_stream in output_streams:
    print(f'{output_stream}...'); sys.stdout.flush()
    if '_ARM' in output_stream: 
        print('  -- skipping --  ')
        continue

    # Find files
    print('Find files'); sys.stdout.flush()
    files = sorted(glob(f'{rundir}/{output_stream}.????-??-??-?????.nc'))

    # Get list of fields to plot; we will plot all the 2D fields
    print('Find fields in files'); sys.stdout.flush()
    with xarray.open_mfdataset(files, data_vars='minimal', coords='minimal', compat='override') as ds:
        fields = [v for v in ds.variables.keys() if ds[v].dims == ('time', 'ncol')]

    # Get grid file
    print('Find model grid file'); sys.stdout.flush()
    modgrid = get_scrip_grid(files[0], mapdir)

    # Get obs file
    obs_name = 'era5'
    obsfiles = sorted(glob(f'{obsdir}/reanalysis-era5-single-levels-monthly-means-1994-10.nc')) 

    # Get obs grid
    print('Find obs grid file'); sys.stdout.flush()
    obsgrid = get_scrip_grid(obsfiles[0], mapdir)

    # Get map from model to obs
    print('Get map file'); sys.stdout.flush()
    mapfile = get_mapping_file(files[0], obsfiles[0], mapdir, method='fv2fv') 

    # Plot all those fields
    plotdir = '/global/cfs/cdirs/e3sm/www/bhillma/scream/decadal-amip/figures'
    for v in ('T_2m',): #fields:
        if v not in fields: continue
        print(f'  {v}'); sys.stdout.flush()
        figname = f'{plotdir}/maps-pyngl/{v}.map.{output_stream}_vs_{obs_name}.png'
        os.makedirs(os.path.dirname(figname), exist_ok=True)
        #compare_maps(('T_2m', 't2m'), figname, files, obsfiles,
        #             gridfiles=(modgrid, obsgrid), maps=(mapfile, None))
        plot_maps(('T_2m', 't2m'), figname, files, obsfiles, gridfiles=(modgrid, obsgrid))
        os.system(f'chmod a+r {figname}') 
