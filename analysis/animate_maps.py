#!/usr/bin/env python3

import plac, os, imageio, sys, numpy, functools
from matplotlib import pyplot
from matplotlib.tri import Triangulation
from cartopy import crs
from cartopy.util import add_cyclic_point
from xarray import open_mfdataset
from time import perf_counter
from scipy.interpolate import griddata
from e3smplot.e3sm_utils import get_data
from plot_map import plot_map


def open_files(*inputfiles):
    print('Found %i files'%len(inputfiles))
    return open_mfdataset(inputfiles, data_vars='minimal', coords='minimal', compat='override')


def memoize(func):
    cache = dict()    
    @functools.wraps(func)
    def memoized_func(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return memoized_func


@memoize
def get_triangulation(lon, lat):
    return Triangulation(lon, lat)


def fix_longitudes(lon):
    lon.assign_coords(lon=numpy.where(lon > 180, lon - 360, lon))
    return lon


def plot_frame(dataset, variable_name, frame_name,
               projection=crs.PlateCarree(),
               **kwargs):

    # Select data
    data = get_data(dataset, variable_name).squeeze()
    lon = get_data(dataset, 'lon').squeeze()
    lat = get_data(dataset, 'lat').squeeze()

    # Reduce data
    if 'lev' in data.dims: raise RuntimeError('Weird dimensions')

    # Fix coordinates
    #lon = fix_longitudes(lon)

    # Plot
    figure, axes = pyplot.subplots(1, 1, subplot_kw=dict(projection=projection), figsize=(10, 8))
    pl, cb = plot_map(lon, lat, data, **kwargs)
    axes.set_title('time = %04i-%02i-%02i %02i:%02i:%02i'%(
        data['time.year'], data['time.month'], data['time.day'],
        data['time.hour'], data['time.minute'], data['time.second']
    ))

    # Save figure
    figure.savefig(frame_name, dpi=100)
    pyplot.close()


# Get a time-varying longitude to be used to rotate map center to mimic earth
# rotation in animations
def rotate_longitude(itime, samples_per_day, start_lon=360):
    central_longitude = (start_lon - itime * 360 / samples_per_day) % 360
    if central_longitude > 180: central_longitude = central_longitude - 360
    return central_longitude
   

def plot_frames(
        dataset, variable_name, 
        rotate=False, samples_per_day=48, 
        **kwargs):

    # Get data range so that all frames will be consistent
    if 'vmin' not in kwargs.keys(): kwargs['vmin'] = get_data(dataset, variable_name).min().values
    if 'vmax' not in kwargs.keys(): kwargs['vmax'] = get_data(dataset, variable_name).max().values

    # Loop over time series and make a plot for each
    frames = []
    print('Looping over %i time indices'%len(dataset.time)); sys.stdout.flush()
    for i in range(len(dataset.time)):
        frame_name = 'tmp_frames/%s.%i.png'%(variable_name, i)
        os.makedirs(os.path.dirname(frame_name), exist_ok=True)
        if os.path.exists(frame_name): 
            frames.append(frame_name)
            update_progress(i+1, len(dataset.time))
            continue
        if rotate == "True":
            central_longitude = rotate_longitude(i, samples_per_day)
            plot_frame(
                dataset.isel(time=i), variable_name, frame_name, 
                projection=crs.Orthographic(central_longitude=central_longitude, central_latitude=20),
                **kwargs
            )
        else:
            plot_frame(
                dataset.isel(time=i), variable_name, frame_name, 
                projection=crs.PlateCarree(central_longitude=180),
                **kwargs
            )
        frames.append(frame_name)
        update_progress(i+1, len(dataset.time))

    # Return list of frames
    return frames


def animate_frames(outputfile, frames, **kwargs):
    print('Stitching %i frames together...'%(len(frames)), end='')
    sys.stdout.flush()
    images = [imageio.imread(frame) for frame in frames]
    imageio.mimsave(outputfile, images, **kwargs)
    print('Done.'); sys.stdout.flush()


def remove_frames(frames):
    for frame in frames: os.remove(frame)


# update_progress() : Displays or updates a console progress bar
def update_progress(iteration, num_iterations, bar_length=10):

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
    text = "\rPercent: [%s] %i of %i (%.2f%%)%s"%( 
        "#"*block + "-"*(bar_length-block), 
        iteration, num_iterations,
        progress*100, status
    )
    sys.stdout.write(text)
    sys.stdout.flush()


def main(variable_name, outputfile, *inputfiles, **kwargs):

    # Open files
    dataset = open_files(*inputfiles)

    # Pull out keyward args
    animate_kw = {}
    for key in ('time_per_frame',):
        if key in kwargs.keys():
            animate_kw[key] = kwargs.pop(key)

    # Plot frames
    frames = plot_frames(dataset, variable_name, **kwargs)

    # Stitch together frames into single animation
    animate_frames(outputfile, frames, **animate_kw)

    # Clean up
    remove_frames(frames)


if __name__ == '__main__':
    plac.call(main)
