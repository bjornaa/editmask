# Check the output from make_coast

import numpy as np
import matplotlib.pyplot as plt

coast_file = "coast.dat"

Xc, Yc = np.loadtxt(coast_file, unpack=True)

plt.plot(Xc, Yc)
plt.axis("image")
plt.show()
