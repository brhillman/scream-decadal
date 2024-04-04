#!/usr/bin/env python3
import xarray
from glob import glob

rundir = '/lustre/orion/cli115/proj-shared/brhillman/e3sm_scratch/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run'

# Find files
files = sorted(glob(f'{rundir}/output.scream.*.nc'))

# Remove rhist files from list
files = [f for f in files if 'rhist' not in f]

if False:
    questionable_files = [
            f'{rundir}/output.scream.decadal.15minINST_ARM.INSTANT.nmins_x15.1994-10-10-00000.nc',
            f'{rundir}/output.scream.decadal.15minINST_ARM.INSTANT.nmins_x15.1994-10-11-00000.nc',
            f'{rundir}/output.scream.decadal.15minINST_ARM.INSTANT.nmins_x15.1994-10-11-00900.nc',
    ]
    questionable_files = sorted(glob(f'{rundir}/output.scream.decadal.1hourlyINST_ne1024pg2.INSTANT.nhours_x1.1994-10-*.nc'))
    for f in questionable_files:
        try:
            with xarray.open_dataset(f) as ds:
                print(f'{f}')
                print(f'  size of time axis: {len(ds.time)}')
                print(f'  time range: {ds.time[0].values} -- {ds.time[-1].values}')
        except:
            print(f'-- could not decode {f} --')

for f in files:
    with xarray.open_dataset(f, decode_times=False) as ds:
        if (len(ds.time) == 0): print(f'{f} has zero time')
#        for v in ds.variables.keys():
#            print(f'  {v} min = {ds[v].min().values}; max = {ds[v].max().values}; numnan = {ds[v].isnull().sum().values}')
