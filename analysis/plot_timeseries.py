#!/usr/bin/env python3

import xarray, os
from e3smplot.e3sm_utils import get_data, area_average
from matplotlib import pyplot


def plot_timeseries(data, **kwargs):
    ax = pyplot.gca()
    if len(data.shape) == 1:
        pl = ax.plot(data.indexes['time'].to_datetimeindex(), data, **kwargs)
        ax.set_ylabel(f'{data.long_name} ({data.units})')
        ax.set_xlabel('Time')
    else:
        pl = ax.contourf(data['time'].to_datetimeindex(), data.lev, data.transpose(), **kwargs)
        ax.set_ylabel(f'Vertical level')
        ax.set_xlabel('Time')
        cb = pyplot.colorbar(
            pl, orientation='horizontal',
            label=ax.set_ylabel(f'{data.long_name} ({data.units})')
        )
    pyplot.xticks(rotation=45)
    return pl


def main(vname, figname, *inputfiles, **kwargs):
    # Open dataset
    ds = xarray.open_mfdataset(inputfiles)

    # Select data
    d = get_data(ds, vname)
    a = get_data(ds, 'area')

    # Compute area-weighted global mean
    dmean = area_average(d, a, dims=('ncol',))

    # Make figure
    fig, ax = pyplot.subplots(1, 1)
    pl = plot_timeseries(dmean, **kwargs)
    
    # Save figure
    os.makedirs(os.path.dirname(figname), exist_ok=True)
    fig.savefig(figname, bbox_inches='tight')

    # Clean up
    pyplot.close(fig)
    ds.close()


if __name__ == '__main__':
    import plac; plac.call(main)
