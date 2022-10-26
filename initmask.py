"""Make an initial land mask based on a coast contour

A cell is masked as land if its center is inside
the coast multipolygon.
The mask is zero on land and one at sea.

The mask overwrites any previous land mask on the file,
so work on a copy of the grid file.

The script may use a couple of minutes, 
depending on the size of the grid.

Use editmask to manually fine adjust the mask to the coast.

"""

# -------------------------------
# Bjørn Ådlandsvik <bjorn@hi.no>
# Institute of Marine research
# 2022-10-26
# -------------------------------

import numpy as np
from matplotlib.path import Path
from netCDF4 import Dataset

# ---------------
# User settings
# ---------------

# Work on a copy of the grid file
grid_file = "norkyst_800m_grid_copy.nc"
# Name of mask variable, X and Y dimensions
mask_var = "mask_rho"   # ROMS
X_dim = "xi_rho"
Y_dim = "eta_rho"

# Coast file in grid coordinates, Nan-separated text format
coast_file = "coast.dat"

# --------------------------------------

# Open a (copy of) the grid file
ncid = Dataset(grid_file, mode="a")
imax = ncid.dimensions[X_dim].size
jmax = ncid.dimensions[Y_dim].size

# Intitalize the mask to sea everywhere
M = np.ones((jmax, imax))

# Load coast contour
Xc, Yc = np.loadtxt(coast_file, unpack=True)
coast_path = Path(np.c_[Xc, Yc])

# Grid coordinates of center of grid cells
II, JJ = np.meshgrid(range(imax), range(jmax))
II = II.reshape((jmax * imax,))
JJ = JJ.reshape((jmax * imax,))

# Find the land points
land = coast_path.contains_points(np.c_[II, JJ])
land = land.reshape((jmax, imax))
M[land] = 0

# Save the mask to the grid file copy
ncid.variables[mask_var][:, :] = M
ncid.close()
