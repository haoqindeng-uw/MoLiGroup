import matplotlib.pyplot as plt

a = 1 + 2

b = 2 + 3
c = a + b

import numpy as np
plt.figure(1)
# fig, ax = plt.subplots()


x = np.linspace(0, 2*np.pi, 100)
y = np.sin(3*x)
plt.plot(x, y)