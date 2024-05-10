#!/usr/bin/env python3

import xarray
from glob import glob
import sys, os
from matplotlib import pyplot
#from plot_map_pyngl import main as plot_map
#from e3smplot.mpl.compare_maps import main as compare_maps
from compare_maps import main as compare_maps
from e3smplot.mpl.plot_maps import main as plot_maps
from e3smplot.e3sm_utils import get_data, get_grid_name
from e3smplot.e3sm_utils import get_scrip_grid, get_mapping_file
from cartopy import crs

case = 'run3-adios'
rundirs = {
        'run1': '/global/cfs/cdirs/e3smdata/simulations/scream-decadal/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run',
        'run3-adios': '/global/cfs/cdirs/e3smdata/simulations/scream-decadal/decadal-production-20240405.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run3-adios/run',
    }
rundir = rundirs[case]
obsdir = '/global/cfs/cdirs/e3smdata/observations/'
mapping_root = '/global/cfs/cdirs/e3sm/bhillma/maps'

var_pairs = (
        #('T_2m', 't2m'),
        #('U_at_model_bot', 'u10'),
        #('SeaLevelPressure', 'msl'),
        #('ps', 'sp'),
        #('V_at_model_bot', 'v10'),
        #('SW_flux_up_at_model_top', 'toa_sw_all_clim'),
        #('SW_clrsky_flux_up_at_model_top', 'toa_sw_clr_t_clim'),
        ('LW_flux_up_at_model_top', 'toa_lw_all_clim'),
        ('LW_clrsky_flux_up_at_model_top', 'toa_lw_clr_t_clim'),
    )

era5_vars = (
        't2m', 'u10', 'msl', 'sp', 'v10'
    )
ceres_vars = (
        'toa_sw_all_clim', 'toa_sw_clr_t_clim',
        'toa_lw_all_clim', 'toa_lw_clr_t_clim',
    )
# Find output streams
print('Find output streams'); sys.stdout.flush()
#output_streams = [os.path.basename(f).replace('.1994-10-01-00000.nc', '') for f in glob(f'{rundir}/output.scream.decadal.*.1994-10-01-00000.nc')]
#output_stream = 'output.scream.decadal.1dailyMAX_ne1024pg2.MAX.ndays_x1' #'output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1'
#'output.scream.decadal.6hourlyINST_ne1024pg2.INSTANT.nhours_x6', 'output.scream.decadal.15minINST_ARM.INSTANT.nmins_x15', 'output.scream.decadal.1hourlyINST_ne1024pg2.INSTANT.nhours_x1', 'output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1', 'output.scream.decadal.3hourlyAVG_ne30pg2.AVERAGE.nhours_x3', 'output.scream.decadal.1dailyMIN_ne1024pg2.MIN.ndays_x1', 'output.scream.decadal.6hourlyINST_ne30pg2.INSTANT.nhours_x6', 'output.scream.decadal.6hourlyAVG_ne30pg2.AVERAGE.nhours_x6', 'decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1.elm.h1', 'output.scream.decadal.3hourlyINST_ne30pg2.INSTANT.nhours_x3', 'output.scream.decadal.1hourlyINST_ARM.INSTANT.nhours_x1', 'output.scream.decadal.1dailyMAX_ne1024pg2.MAX.ndays_x1', 'output.scream.decadal.1dailyAVG_ne1024pg2.AVERAGE.ndays_x1'
output_streams = ('output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1',)
print(output_streams)
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
    with xarray.open_mfdataset(files, use_cftime=True, data_vars='minimal', coords='minimal', compat='override') as ds:
        fields = [v for v in ds.variables.keys() if ds[v].dims == ('time', 'ncol')]

    # Get grid file
    print('Find model grid file'); sys.stdout.flush()
    modgrid = get_scrip_grid(files[0], mapping_root)

    # Plot all those fields
    plotdir = f'/global/cfs/cdirs/e3sm/www/bhillma/scream/decadal-amip/{case}/figures'
    for (v, vobs) in var_pairs: #fields:
        if v not in fields: continue
        print(f'  {v}'); sys.stdout.flush()

        # Get obs file
        if vobs in era5_vars:
            obs_name = 'era5'
            obsfiles = xarray.open_mfdataset(sorted(glob(f'{obsdir}/era5/reanalysis-era5-single-levels-monthly-means-1994-10.nc')))
            t_indices = (None, None)  # Means
        elif vobs in ceres_vars:
            obs_name = 'ceres-ebaf'
            obsfiles = xarray.open_mfdataset(sorted(glob(f'{obsdir}/ceres-ebaf/climo/CERES_EBAF_Ed4.2_Subset_CLIM01-CLIM12.nc'))).rename({'ctime': 'time'})
            t_indices = (0, 9)  # October

        # Get obs grid
        print('Find obs grid file'); sys.stdout.flush()
        obsgrid = get_scrip_grid(obsfiles, mapping_root)

        # Get map from model to obs
        print('Get map file'); sys.stdout.flush()
        mapfile = get_mapping_file(files[0], obsfiles, mapping_root, method='fv2fv') 

        # Make plots
        figname = f'{plotdir}/maps/{v}.map.{output_stream}_vs_{obs_name}.png'
        os.makedirs(os.path.dirname(figname), exist_ok=True)
        compare_maps((v, vobs), figname, files, obsfiles,
                     mapfiles=(mapfile, None), t_indices=t_indices, labels=(case, obs_name))
                                                      
        #plot_maps((v, vobs), figname, files, obsfiles)
        os.system(f'chmod a+r {figname}') 
        os.system(f'chmod a+rx {os.path.dirname(figname)}') 
