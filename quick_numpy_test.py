import numpy as np

my_array = np.array([np.linspace(1,10, num=10),
					 np.linspace(1,10, num=10),
					 np.linspace(1,10, num=10)]
					)



mega_array = np.array([my_array.copy(), my_array.copy()])
print(mega_array)
print(mega_array.shape)

mega_array[:, :2] = 5
print(mega_array)