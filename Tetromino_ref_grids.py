import numpy as np
# np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
ref_grids = {
	'fw z': {
		1: np.array([[1,1,0,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]]),
		2: np.array([[0,1,0,0],[1,1,0,0],[1,0,0,0],[0,0,0,0]])
	},
	'bw z': {
		1: np.array([[0,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]]),
		2: np.array([[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]])
	},
	'fw l': {
		1: np.array([[1,0,0,0],[1,0,0,0],[1,1,0,0],[0,0,0,0]]),
		2: np.array([[1,1,1,0],[1,0,0,0],[0,0,0,0],[0,0,0,0]]),
		3: np.array([[1,1,0,0],[0,1,0,0],[0,1,0,0],[0,0,0,0]]),
		4: np.array([[0,0,1,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]])
	},
	'bw l': {
		1: np.array([[0,1,0,0],[0,1,0,0],[1,1,0,0],[0,0,0,0]]),
		2: np.array([[1,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]),
		3: np.array([[1,1,0,0],[1,0,0,0],[1,0,0,0],[0,0,0,0]]),
		4: np.array([[1,1,1,0],[0,0,1,0],[0,0,0,0],[0,0,0,0]])
	},
	't': {
		1: np.array([[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]]),
		2: np.array([[1,0,0,0],[1,1,0,0],[1,0,0,0],[0,0,0,0]]),
		3: np.array([[1,1,1,0],[0,1,0,0],[0,0,0,0],[0,0,0,0]]),
		4: np.array([[0,1,0,0],[1,1,0,0],[0,1,0,0],[0,0,0,0]])
	},
	'sq': {
		1: np.array([[1,1,0,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]])
	},
	'long': {
		1: np.array([[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]]),
		2: np.array([[1,1,1,1],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
	}
}
minimised_grids = {
	'fw z': {
		1: np.array([[1,1,0],[0,1,1]]),
		2: np.array([[0,1],[1,1],[1,0]])
	},
	'bw z': {
		1: np.array([[0,1,1],[1,1,0]]),
		2: np.array([[1,0],[1,1],[0,1]])
	},
	'fw l': {
		1: np.array([[1,0],[1,0],[1,1]]),
		2: np.array([[1,1,1],[1,0,0]]),
		3: np.array([[1,1],[0,1],[0,1]]),
		4: np.array([[0,0,1],[1,1,1]])
	},
	'bw l': {
		1: np.array([[0,1],[0,1],[1,1]]),
		2: np.array([[1,0,0],[1,1,1]]),
		3: np.array([[1,1],[1,0],[1,0]]),
		4: np.array([[1,1,1],[0,0,1]])
	},
	't': {
		1: np.array([[0,1,0],[1,1,1]]),
		2: np.array([[1,0],[1,1],[1,0]]),
		3: np.array([[1,1,1],[0,1,0]]),
		4: np.array([[0,1],[1,1],[0,1]])
	},
	'sq': {
		1: np.array([[1,1],[1,1]])
	},
	'long': {
		1: np.array([[1],[1],[1],[1]]),
		2: np.array([[1,1,1,1]])
	}
}

class ref_grid_handler:
	def __init__(self):
		self.ref_data = ref_grids
		self.minimised_data = minimised_grids

	def determine_tetromino(self, input_array: np.ndarray) -> tuple:
		for shape_key, variants in self.ref_data.items():
			for variant_id, ref_array in variants.items():
				if self.check_all_equal(input_array, ref_array):
					return shape_key, variant_id

		return (None, None)

	def check_all_equal(self, input_array: np.ndarray, reference_array: np.ndarray) -> bool:
		"""
		:param input_array:
		:param reference_array:
		:return bool:

		input and reference array must be the same size.
		designed for shape 4x4 but only requires shape to be equal
		"""
		difference = input_array - reference_array
		difference = difference[difference!=0]
		if len(difference) > 0:
			return False
		else:
			return True

if __name__ == "__main__":
	for key, array in ref_grids.items():
		print(f"current key: {key}")
		for index, value in array.items():
			print(f"{index})\n{value}")

	for key, array in minimised_grids.items():
		print(f"current key: {key}")
		for index, value in array.items():
			print(f"{index})\n{value}")