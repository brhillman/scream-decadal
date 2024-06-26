#!/usr/bin/env python3

import plac
import ngl
import numpy
import xarray
import os
from e3smplot.utils import nice_cntr_levels
from e3smplot.e3sm_utils import get_data, get_area_weights, area_average
import dask

def plot_map(wks, x, y, data, **kwargs):

    # Set up plot resources
    res = ngl.Resources()
    res.cnFillOn = True
    res.cnLinesOn = False
    res.cnFillPalette = 'MPL_viridis'

    # Add cyclic point if we need to
    if len(data.shape) == 2 and x.max() < 360:
        data, x = ngl.add_cyclic(data, x)

    # If passed 2d coordinate arrays assume they represent cell vertices, 
    # otherwise assume cell centers
    if len(x.shape) == 2:
        res.cnFillMode = 'CellFill'
        res.sfXCellBounds = x
        res.sfYCellBounds = y
    else:
        res.cnFillMode = 'RasterFill'
        res.sfXArray = x
        res.sfYArray = y

    # Tweak plot appearance
    res.mpGridAndLimbOn = False
    res.mpPerimOn = False

    # Additional options passed via kwargs
    for key, val in kwargs.items():
        setattr(res, key, val)

    # Make the plot
    plot = ngl.contour_map(wks, data, res)

    return plot


def open_dataset(*datafiles):
    return xarray.open_mfdataset(datafiles, data_vars='minimal', coords='minimal', compat='override')


def get_coords(grid_file):
    with xarray.open_dataset(grid_file) as ds:
        if 'lon' in ds and 'lat' in ds:
            x = ds['lon']
            y = ds['lat']
        elif 'grid_corner_lon' in ds and 'grid_corner_lat' in ds:
            x = ds['grid_corner_lon']
            y = ds['grid_corner_lat']
        else:
            raise RuntimeError('No valid coordinates in grid file.')
    return x, y


def main(varnames, plotname, *datafiles, gridfiles=None,
         time_index=None, lev_index=0, functions=None,
         mapping_root='./maps',
         vmin=None, vmax=None, **kwargs):

    # Setup the canvas
    wks = ngl.open_wks(
        os.path.splitext(plotname)[1][1:],
        os.path.splitext(plotname)[0]
    )

    # Read data
    datasets = [f if isinstance(f, xarray.Dataset) else open_dataset(*f) for f in datafiles]
    #gridfiles = [get_scrip_grid(d, mapping_root) for d in datasets]

    # Select time
    datasets = [ds.mean(dim='time', keep_attrs=True) if
                time_index is None else ds.isel(time=time_index) for ds in datasets]

    # Select data
    data_arrays = [get_data(ds, varname) for ds, varname in zip(datasets,
                                                                varnames)]
    area_arrays = [get_area_weights(ds) for ds in datasets]
    coords = [get_coords(f) for f in gridfiles]

    for (d, (x, y)) in zip(data_arrays, coords):
        print(d.shape, x.shape, y.shape)
    exit()

    # Apply arbitrary transforms to data?
    if functions is not None: data = eval(functions)

    # Get contour levels; the explicit type casting deals with problems calling
    # this standalone code using subprocess.run() with string arguments, where
    # all kwargs are going to be interpreted as strings
    if vmin is not None and vmax is not None:
        if float(vmin) < 0 and float(vmax) > 0:
            *__, clevels = nice_cntr_levels(float(vmin), float(vmax), returnLevels=True, max_steps=13, aboutZero=True)
        else:
            *__, clevels = nice_cntr_levels(float(vmin), float(vmax), returnLevels=True, max_steps=13)
        kwargs['cnLevels'] = clevels #get_contour_levels(data)
        kwargs['cnLevelSelectionMode'] = 'ExplicitLevels'

#   if 'cnLevels' in kwargs.keys():
#       kwargs['cnLevels'] = kwargs['cnLevels'].split(',')

#   if 'mpMinLonF' in kwargs.keys():
#       # subset data for min/max
#       mx = (x > float(kwargs['mpMinLonF'])) & (x < float(kwargs['mpMaxLonF']))
#       my = (y > float(kwargs['mpMinLatF'])) & (y < float(kwargs['mpMaxLatF']))
#       dsub = data.where(mx).where(my)
#       print(f'data.min = {dsub.min().values}; data.max = {dsub.max().values}')
#       kwargs['tiMainString'] = f'min = {dsub.min().values:.02f}; max = {dsub.max().values:.02f}'

#   # Get title string
#   if 'tiMainString' not in kwargs.keys():
#       dmin = data.min().values
#       dmax = data.max().values
#       wgts = get_area_weights(ds_data)
#       davg = area_average(data, wgts)
#       kwargs['tiMainString'] = f'min = {dmin:.2f}; max = {dmax:.2f}; mean = {davg.values:.2f}'
#       kwargs['tiMainFontHeightF'] = 0.02

#   # Make plots
#   if 'lbTitleString' not in kwargs.keys():
#       kwargs['lbTitleString'] = f'{data.long_name} ({data.units})'
    plots = [plot_map(wks, x.values, y.values, data.values,
                      mpGeophysicalLineColor='white',
                      lbOrientation='horizontal', cnLineLabelsOn=False,
                      cnLinesOn=False, **kwargs) for x, y, data in zip(*coords, data_arrays)]
                                                                      

    # Panel the plots together
    ngl.panel(wks, plots, [len(data_arrays), 1])

    # Close things
    ngl.destroy(wks)

    # Trim whitespace
    os.system(f"convert -trim {plotname} {plotname}")

    # Fix permissions
    os.system(f'chmod a+r {plotname}')


if __name__ == '__main__':
    plac.call(main)
