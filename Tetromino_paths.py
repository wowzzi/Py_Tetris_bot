from pathlib import Path
from PIL import Image
import numpy as np
import numpy.ma as ma

file_dir = Path(__file__)
print(file_dir)
print(file_dir.parent)

tetromino_path = file_dir.parent.joinpath("Tetrominoes")
print(tetromino_path)

all_tetromino_paths = tetromino_path.glob("*.png")
all_tetromino_paths = list(all_tetromino_paths)

tetromino_dict = {}
images = []
for tetromino_path in all_tetromino_paths:
	print(tetromino_path)
	print(tetromino_path.stem)
	temp_img= Image.open(tetromino_path)
	images.append(temp_img)
	image_array = np.asarray(temp_img)
	rows_x_cols = image_array.shape[0] * image_array.shape[1]
	image_array = image_array.reshape(rows_x_cols, image_array.shape[2])
	print(image_array.shape)

	tetromino_dict[tetromino_path.stem] = image_array

for name, img_arr in tetromino_dict.items():
	for n, (temp_name, temp_arr) in enumerate(tetromino_dict.items(), start=1):
		if name == temp_name:
			continue
		temp_diff_arr = img_arr - temp_arr
		print()
		print(f"{n}. {name} vs {temp_name}\n{temp_diff_arr[:10]}")
		print("normal for loop")
		mask = np.all(temp_diff_arr == 0, axis=-1)
		for val in temp_diff_arr[:]:
			print(val)
			print(type(val))

		print(mask)

