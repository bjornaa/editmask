"""Make a coast line from GSHHS in grid coordinates
   
Uses pyproj, shapely and cartopy

"""

# ----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute if Marine Research
# 2022-10-24
# ----------------------------------


from itertools import chain
import numpy as np
from netCDF4 import Dataset
import pyproj
from shapely import geometry
import cartopy.io.shapereader as shapereader

# Choose between c, l, i, h, f resolutions
# Crude to Fine
GSHHS_resolution = "f"

# Grid file and parameters
grid_file = "norkyst_800m_grid.nc"
xp, yp, dx, ylon = 3991, 2230, 800, 70  # Norkyst-800m
ellps = "WGS84"  # WGS84 or sphere

# Output coast file name
outfile = "coast.dat"

# Read the grid file
with Dataset(grid_file) as ncid:
    lon = ncid.variables["lon_rho"][:, :]
    lat = ncid.variables["lat_rho"][:, :]

jmax, imax = lon.shape

eps = 0.2  # Make the extent slightly larger
lonmin = lon.min() - eps
lonmax = lon.max() + eps
latmin = lat.min() - eps
latmax = lat.max() + eps

# Grid projection
proj4string = f"+proj=stere +ellps={ellps} +lat_0=90.0 +lat_ts=60.0 +x_0={xp*dx} +y_0={yp*dx} +lon_0={ylon}"
# gproj = pyproj.Proj(proj4string)
grid_projection = pyproj.Proj(
    proj="stere", ellps=ellps, lat_0=90, lat_ts=60, x_0=xp * dx, y_0=yp * dx, lon_0=ylon
)

# Global coastline from GSHHS as shapely collection generator
path = shapereader.gshhs(scale=GSHHS_resolution)
coast_ll = shapereader.Reader(path).geometries()

# Restrict the coastline to the regional lon-lat domain
geobox = geometry.box(lonmin, latmin, lonmax, latmax)
coast_ll = (geobox.intersection(p) for p in coast_ll if geobox.intersects(p))
# Filter out isolated points
coast_ll = filter(
    lambda p: isinstance(p, geometry.MultiPolygon) or isinstance(p, geometry.Polygon),
    coast_ll,
)
# The filtered intersection can consist of both polygons, multipolygons
# First make a generator expression of multipolygons = lists of polygons
# and thereafter flatten it into one large MultiPolygon
coast_ll = (
    pol.geoms if isinstance(pol, geometry.MultiPolygon) else [pol] for pol in coast_ll
)
coast_ll = geometry.MultiPolygon(chain(*coast_ll)).geoms

# Transform the coastline to grid coordinates
coast = []
for polygon in coast_ll:
    x, y = polygon.boundary.xy
    x, y = grid_projection(x, y)
    x, y = np.array(x) / dx, np.array(y) / dx
    coast.append(geometry.Polygon(zip(x, y)))
print("f")
coast = geometry.MultiPolygon(coast).geoms

# Restrict the coast line to the model domain
gridbox = geometry.box(-0.5, -0.5, imax - 0.5, jmax - 0.5)
coast = (gridbox.intersection(pol) for pol in coast if gridbox.intersects(pol))
# Filter out isolated points
coast = filter(
    lambda pol: isinstance(pol, geometry.MultiPolygon)
    or isinstance(pol, geometry.Polygon),
    coast,
)
coast = (pol if isinstance(pol, geometry.MultiPolygon) else [pol] for pol in coast)
coast = geometry.MultiPolygon(chain(*coast)).geoms

# Save the coast to file
# Text with NaN between the polygons

with open(outfile, mode="w") as f:
    for polygon in coast:
        for xy in polygon.boundary.coords:
            f.write(f"{xy[0]:7.2f}  {xy[1]:7.2f}\n")
        f.write("    NaN    NaN\n")
