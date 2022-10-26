editmask
========

A
This is a set of `python` scripts for making ane editing the land mask for a model grid. 

The `grid` is a curvilinear rectangular grid defined in a grid file. `Grid
coordinates` is a linear coordinate system for the grid with coordinates X=i,
Y=j for the center of the (i,j)-th grid cells with $(0, 0)$ in the lower left
corner.

A `land mask` is a 2D array over the grid with values one at sea and zero over
land.

A `coast file` is a text file with two columns for X and Y grid coordinates. The
coast polygons are separated by lines with two NaNs. A coast file can be made by
the script ``make_coast.py``. This is set up for a polar stereographic map
projection defined by parameters `xp, yp, dx, ylon`. It can easily be modied for
other grids where the geographical mapping can be defined by a `proj4string`. The
script ``plot_coast.py`` can be used to check that the coast line looks all
right. 

Given the coast file, an initial land mask can be made by the script
``initmask.py``. It simply marks all grid cells where the center is on land as
land cells. It takes a `netcdf` grid file as input. The grid file must define
dimensions in the X and Y directions. It overwrites any existing land mask in
the file so it is recommended to work on a copy of the grid file.

The script `editmask.py` provides an interactive editor for the land mask. The
input is a grid file with an initial land mask and a coast line file. The basic
use is to manually adjust the land mask to intricate fjord geometry. The input
Both land and sea are shown with  yellow–green and blue check board patterns
together with the coast line in `matplotlib`. Ordinary matplotlib controls can
be used to zoom and pan the image. Clicking on a grid cell toggles between land
and sea. Critical cells, sea cells without neighbour in X or Y direction is
marked as red. Semi-critical cells, sea cells that are not included in a 2x2
block of sea cells are marked as orange.

Using the subgrid limiters i0, i1 in X-direction and j0, j1 in Y-direction it is
possible to work sequentially on subgrids to speed up the response from the
system, if needed.