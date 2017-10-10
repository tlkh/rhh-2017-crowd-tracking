import numpy as np
import numpy.random
import matplotlib.pyplot as plt

'''# Generate some test data
x = np.random.randn(8873)
y = np.random.randn(8873)'''

with open('log.txt', 'rt') as points:
    x,y = [], []
    for row in points:
        row = row.split(", ", 2)
        x.append(int(row[0]))
        y.append(-(int(row[1])))

plt.scatter(x,y)
plt.show()
