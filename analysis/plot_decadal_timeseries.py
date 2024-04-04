#!/usr/bin/env python3

import xarray
from glob import glob
import sys, os
from matplotlib import pyplot
from plot_timeseries import main as plot_timeseries
from e3smplot.e3sm_utils import get_data
from cartopy import crs

rundir = '/lustre/orion/cli115/proj-shared/brhillman/e3sm_scratch/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run'

# Find output streams
output_streams = [os.path.basename(f).replace('.1994-10-01-00000.nc', '') for f in glob(f'{rundir}/*.1994-10-01-00000.nc')]
#output_stream = 'output.scream.decadal.1dailyMAX_ne1024pg2.MAX.ndays_x1' #'output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1'
for output_stream in output_streams:
    print(f'{output_stream}...'); sys.stdout.flush()

    # Find files
    files = sorted(glob(f'{rundir}/{output_stream}.????-??-??-?????.nc'))

    # Get list of fields to plot; we will plot all the 2D fields
    with xarray.open_mfdataset(files, data_vars='minimal', coords='minimal', compat='override') as ds:
        fields = [v for v in ds.variables.keys() if ds[v].dims == ('time', 'ncol')]

    # Plot all those fields
    for v in fields:
        print(f'  {v}'); sys.stdout.flush()
        figname = f'figures/timeseries/{v}.timeseries.{output_stream}.png'
        plot_timeseries(v, figname, *files)
