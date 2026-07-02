import numpy as np

def sub_fractionate_3d_array(input_array: np.array,
							 reference_array: np.array,
							 start_row: int = 0,
							 start_col: int = 0,
							 ) -> np.array:
	ref_height, ref_width, _ = reference_array.shape
	return input_array[start_row:start_row + ref_height, start_col:start_col + ref_width]




def add_iterables(input_iterable, other) -> tuple:
	output = []
	if isinstance(other, int):
		output = [i + other for i in input_iterable]
	if isinstance(other, tuple) or isinstance(other, list):
		if len(input_iterable) == len(other):
			for i in range(len(input_iterable)):
				output.append(input_iterable[i] + other[i])
		else:
			return None
	return tuple(output)

def sub_iterables(input_iterable, other) -> tuple:
	output = []
	if isinstance(other, int):
		output = [i - other for i in input_iterable]
	if isinstance(other, tuple) or isinstance(other, list):
		if len(input_iterable) == len(other):
			for i in range(len(input_iterable)):
				output.append(input_iterable[i] - other[i])
		else:
			return None
	return tuple(output)