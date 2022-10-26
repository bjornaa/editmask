"""Interactive editor for adapting a land mask to a coast line.

Input is a netcdf grid file with a land mask and
a nan-separated text file with a coast line in the
grid coordinate system.
Warns about critical grid cells.
The land mask is modified in place (work on a copy).

Idea from editmask.m in matlab.tar.gz, available from the
ROMS site, https://www.myroms.org/index.php?page=Processing.

"""
# ------------------------------
# Bjørn Ådlandsvik <bjorn@hi.no>
# Institute of Marine Research
# 2022-10-25
# ------------------------------


import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

# ---------------
# User settings
# ---------------

# Grid file copy
grid_file = "norkyst_800m_grid_copy.nc"
# Variable name for the mask, = 0 at land, = 1 at sea
mask_var = "mask_rho"  # ROMS

# Text file with coast line in grid coordinates
# Polygons are separated by Nan
coast_file = "coast.dat"

# Sub-domain to consider
# Use None for whole axis
i0, i1 = 0, None
j0, j1 = 0, None


# -------------
# Functions
# -------------

# Click handler
def click(event):
    """Handles left mouse clicks"""
    tb = plt.get_current_fig_manager().toolbar
    if event.button == 1 and event.inaxes and tb.mode == "":
        x, y = event.xdata, event.ydata
        i = int(round(x))
        j = int(round(y))
        print("grid cell: ", i, j)

        if M[j - j0, i - i0] > 0.5:  # Click in sea cell
            M[j - j0, i - i0] = 0.0
        else:  # Click in land cell
            M[j - j0, i - i0] = 1.0

        # Update the figure
        foreground()


# --------------------------

# Key handler
def key(event):
    print(event.key)
    if event.key == "m":
        savemask()
        print("Saving land mask")

    elif event.key == "q":
        print("Quit")
        f.close()
        import sys

        sys.exit(0)


# ---------------------------------

# (Re)draw foreground
def foreground():
    M2 = display_mask(M)
    h.set_array(M2.ravel())
    plt.draw()


# ---------------------------------


def savemask():
    f.variables[mask_var][j0:j1, i0:i1] = M
    f.sync()


# ---------------------------------


def display_mask(M):
    """Make an array for correct display with pcolormesh"""
    jmax, imax = M.shape
    # Extend M with a one cell frame of zeros
    B0 = np.zeros((jmax + 2, imax + 2))
    B0[1:-1, 1:-1] = M
    MS = B0[:-2, 1:-1]
    MN = B0[2:, 1:-1]
    MW = B0[1:-1, :-2]
    ME = B0[1:-1, 2:]
    MNW = B0[2:, :-2]
    MNE = B0[2:, 2:]
    MSE = B0[:-2, 2:]
    MSW = B0[:-2, :-2]

    # Q = 0 if no pair of neighbour grid cells are both at sea
    # Q2 = 0 if grid cell is not in 2x2 sea block
    Q = MS * MW + MW * MN + MN * ME + ME * MS
    Q2 = MSW * MS * MW + MNW * MN * MW + MNE * MN * ME + MSE * MS * ME

    # M2 = 0,1 on land, 2, 3 at sea
    # Both with checkboard pattern
    M2 = 2 * M + A
    # Set semi-critical sea sells (Q != 0, Q2==0) to 4 (orange)
    M2[(M > 0) & (Q > 0) & (Q2 == 0)] = 4
    # Set critical sea cells (Q==0) to 5 (i.e. red)
    M2[(M > 0) & (Q == 0)] = 5

    return M2


# ---------------
# File handling
# ---------------

f = Dataset(grid_file, mode="a")
M = f.variables[mask_var][j0:j1, i0:i1]
jmax, imax = M.shape

# Fill in missing right or upper limit
if i1 is None:
    i1 = i0 + imax
if j1 is None:
    j1 = j0 + jmax

# Grid coordinates of cell boundaries
X = -0.5 + i0 + np.arange(imax + 1)
Y = -0.5 + j0 + np.arange(jmax + 1)

# Read coast line
Xc, Yc = np.loadtxt(coast_file, unpack=True)

# Check-board pattern of 0 and 1
A = np.fromfunction(lambda i, j: (i + j) % 2, (jmax, imax))

M2 = display_mask(M)
print("editmask: # critical cells = ", np.sum(M2 == 5))
print("editmask: # semi-critical cells = ", np.sum(M2 == 4))

# Uncomment to list the critical locations
# print(np.argwhere(M2 >= 5.0))

# Make a dedicated colour map
mycolormap = plt.matplotlib.colors.ListedColormap(
    [
        (0.4, 1.0, 0.4),  # light green
        (0.8, 1.0, 0.2),  # yellow
        (0.2, 0.2, 1.0),  # blue
        (0.4, 0.4, 1.0),  # light blue
        (1.0, 0.5, 0.0),  # orange
        (1.0, 0.0, 0.0),  # clear red
    ]
)


# -------------
# Plot
# -------------

# Plot coast line
plt.plot(Xc, Yc, color="black", lw=2)

# The line above have sometimes given annoying extra lines.
# If this happens, break up the coast line in separate polygons by:
# (I,) = np.nonzero(np.isnan(Xc))
# I = np.concatenate(([0], I))
# for i, j in zip(I[:-1], I[1:]):
#     plt.plot(Xc[i:j], Yc[i:j], color="black", lw=2)

# Land mask
h = plt.pcolormesh(X, Y, M2, cmap=mycolormap)
plt.clim(-0.5, 5.5)
# plt.colorbar()

plt.title("m: Save mask,  o: Toggle zoom,  p: Pan,  q: Quit")
plt.axis("image")
plt.axis([i0 - 0.5, i1 - 0.5, j0 - 0.5, j1 - 0.5])

# Interactive call-back functions
plt.connect("button_press_event", click)
plt.connect("key_press_event", key)

plt.show()

f.close()
