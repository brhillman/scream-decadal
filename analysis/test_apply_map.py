#!/usr/bin/env python3

import xarray, os
from apply_map import apply_map
from matplotlib import pyplot
from plot_map import plot_map
from e3smplot.e3sm_utils import get_data

def main():
    inputfiles = (
            '/global/cfs/cdirs/e3smdata/simulations/scream-decadal/decadal-production-20240305.ne1024pg2_ne1024pg2.F20TR-SCREAMv1.run1/run/output.scream.decadal.monthlyAVG_ne30pg2.AVERAGE.nmonths_x1.1994-10-01-00000.nc',
            '/global/cfs/cdirs/e3smdata/observations/era5/reanalysis-era5-single-levels-monthly-means-1994-10.nc',
        )
    map_files = ['/global/cfs/cdirs/e3sm/bhillma/maps/map_ne30pg2_to_721x1440_fv2fv.nc', None]

    # Open datasets
    print('open datasets')
    datasets = [xarray.open_dataset(f) for f in inputfiles]
    dataarrays = [get_data(ds, vname).mean(dim='time', keep_attrs=True) for ds,
                  vname in zip(datasets, ('T_2m', 't2m'))]
    lons = [get_data(ds, 'longitude') for ds in datasets]
    lats = [get_data(ds, 'latitude') for ds in datasets]

    # Apply maps
    print('apply maps')
    dataarrays, lons, lats = zip(*[apply_map(d, m) if m is not None else (d, x, y) for d, x, y, m in zip(dataarrays, lons, lats, map_files)])

    # Make plot
    print('plot')
    figure, axes = pyplot.subplots(2, 1)
    for d, x, y, ax in zip(dataarrays, lons, lats, axes):
        #pl = plot_map(x, y, d, plot_method='regrid')
        pl = ax.pcolormesh(x, y, d)
    plotdir = '/global/cfs/cdirs/e3sm/www/bhillma/'
    figname = f'{plotdir}/test_apply_map.png'
    figure.savefig(figname, bbox_inches='tight')
    os.system(f'chmod a+r {figname}')
    print('done')

if __name__ == '__main__':
    import plac; plac.call(main)
