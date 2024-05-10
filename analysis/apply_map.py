import numpy
import xarray
import scipy.sparse
import sys

def myprint(*args, **kwargs):
    print(*args, **kwargs); sys.stdout.flush()


def apply_map(da, map_file, template=None, verbose=False):

    # Allow for passing either a mapping file name or a xarray.Dataset
    if isinstance(map_file, xarray.Dataset):
        ds_map = map_file
    else:
        if verbose: myprint('Open map file as xarray.Dataset object')
        ds_map = xarray.open_mfdataset(map_file)

    # Do the remapping
    if verbose: myprint('Create weights as a COO matrix')
    weights = scipy.sparse.coo_matrix((ds_map['S'].values, (ds_map['row'].values-1, ds_map['col'].values-1)))
    if verbose: myprint('Flatten data array')
    if len(da.shape) == 1:
        da_flat = da.data
    elif len(da.shape) == 2:
        da_flat = da.data.reshape([da.shape[0]*da.shape[1]])
    if verbose: myprint('Apply weights via matrix multiply')
    da_regrid = weights.dot(da_flat)

    # Figure out coordinate variables and whether or not we should reshape the
    # output before returning
    if verbose: myprint('Reshape output')
    if isinstance(template, xarray.DataArray):
        da_regrid = xarray.DataArray(
            da_regrid.reshape(template.shape), dims=template.dims, coords=template.coords,
            attrs=da.attrs
        )
        x = da_regrid.lon
        y = da_regrid.lat
    elif len(ds_map.dst_grid_dims) == 2:
        # Get lon and lat coordinates from mapping file
        x = ds_map.xc_b.values.reshape(ds_map.dst_grid_dims.values[::-1])[0,:]
        y = ds_map.yc_b.values.reshape(ds_map.dst_grid_dims.values[::-1])[:,0]

        # Reshape to expected output
        da_regrid = xarray.DataArray(
            da_regrid.reshape(ds_map.dst_grid_dims.values[::-1]),
            dims=('lat', 'lon'),
            coords={'lat': y, 'lon': x},
            attrs=da.attrs,
        )
    else:
        x = ds_map.xc_b
        y = ds_map.yc_b

    # Return remapped array and coordinate variables
    if verbose: myprint('Return remapped data, x, y')
    return da_regrid, x, y


# update_progress() : Displays or updates a console progress bar
def update_progress(iteration, num_iterations, bar_length=10):
    '''
    Display and update a console progress bar
    '''

    # Get progress as a fraction and compute size of "block" filled to visually
    # represent fraction completed.
    progress = 1.0 * iteration / num_iterations
    block = int(round(bar_length * progress))

    # Get status; if status < 1 there will be no newline, so we need to add one
    # explicitly on the last iteration.
    if progress >= 1:
        status = "\r\n"
    else:
        status = ""

    # Display appropriate text to build status bar
    text = "\rProgress: [%s] %i of %i (%.2f%%)%s"%(
        "#"*block + "-"*(bar_length-block),
        iteration, num_iterations,
        progress*100, status
    )
    sys.stdout.write(text)
    sys.stdout.flush()


def interp_along_axis(xout, xin, yin, axis=0, *args, **kwargs):
    """
    Perform 1D interpolation along 1D slices of a ND array.
    """

    # Make sure input arrays are sized appropriately
    assert xin.shape == yin.shape

    # Setup output array
    shape_in  = yin.shape
    shape_out = list(shape_in)
    shape_out[axis] = len(xout)
    yout = numpy.empty(shape_out)

    # Apply function along axis specified by looping over
    # indices across the other axes and applying function
    # to 1d slices; equivalent to, e.g.,
    # for ii in yin.shape[0]:
    #     for jj in yin.shape[1]:
    #        for kk in yin.shape[2]:
    #            yout[ii,jj,kk,:] = numpy.interp(xout, xin[ii,jj,kk,:], yin[ii,jj,kk,:])
    Ni, Nk = yin.shape[:axis], yin.shape[axis+1:]
    for ii in numpy.ndindex(Ni):
        for kk in numpy.ndindex(Nk):
            yout[ii + numpy.s_[...,] + kk] = numpy.interp(
                xout, xin[ii + numpy.s_[:,] + kk], yin[ii + numpy.s_[:,] + kk], *args, **kwargs
            )
    return yout
