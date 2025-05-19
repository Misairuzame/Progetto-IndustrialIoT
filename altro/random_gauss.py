import random

import matplotlib.pyplot as plt

plt.hist([random.gauss(1.0, 0.02) for _ in range(10000)], bins=100)
plt.show()
