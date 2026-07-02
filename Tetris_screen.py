from pathlib import Path
from PIL import Image
import mss
from mss import tools
import numpy as np
import tetris_helper_funcs as tf
import keyboard as kb
import pprint as pp
import time

width = 820
height = 1000
num_mon = 2
screen_grab = None

reference_game_screen = Image.open("Pause_button_ref.png")
ref_data = np.asarray(reference_game_screen)
ref_height, ref_width, _ = ref_data.shape
print(f"ref height: {ref_height}, ref width: {ref_width}")


with mss.MSS() as sct:
	monitor = sct.monitors[num_mon]
	center_x = monitor['left'] + monitor['width']//2
	center_y = monitor['top'] + monitor['height']//2
	center = (center_x, center_y)
	print(center)
	top = center[1] - height // 2
	left = center[0] - width // 2
	region ={
		'top': top,
		'left': left,
		'width': width,
		'height': height,
		'mon': num_mon
	}
	print(region)
	while True:
		#wait for next event.
		event = kb.read_event()
		if event.event_type == kb.KEY_DOWN and event.name == "p":
			screen_grab = sct.grab(region)
			tools.to_png(screen_grab.rgb, screen_grab.size, output="screen_grab.png")
		elif event.event_type == kb.KEY_DOWN and event.name == "q":
			break

	if screen_grab is not None:
		#convert screen_grab to PIL
		scn_grab_as_img = Image.new('RGB', screen_grab.size)
		RGB_pixel_tuple = zip(screen_grab.raw[2::4],   screen_grab.raw[1::4], screen_grab.raw[::4])
		scn_grab_as_img.putdata(list(RGB_pixel_tuple))
		scn_grab_array = np.array(scn_grab_as_img)

		#now check vs reference
		#in logical theory I want to take my pause button and compare it to the reference
		#lets say take a portion of the scn_grab equal to 75px x 74px png I have (thats the size of the pause button png)
		#then subtact my scn_grab portion from my ref png, take absolute value
		# then take a mean of the all values, if less than 2 or something its probably a match? i guess.
		ref_used_height = ref_height/2
		ref_used_width = ref_width/2
		screen_shape = scn_grab_array.shape
		y_iterations = screen_shape[0]/ref_used_height #74px reference icon height
		x_iterations = screen_shape[1]/ref_used_width #75px reference icon width
		y_limit = screen_shape[0] - ref_height
		y_starts = [int(n*ref_used_height) for n in range(int(y_iterations)) if n*ref_used_height < y_limit]
		if isinstance(y_iterations, float):
			y_starts.append(y_limit)

		x_limit = screen_shape[1] - ref_width
		x_starts = [int(n*ref_used_width) for n in range(int(x_iterations)) if n*ref_used_width < x_limit]
		if isinstance(x_iterations, float):
			x_starts.append(x_limit)

		print(f"y_starts: {y_starts}\nx_starts: {x_starts}")
		print(screen_shape)
		screen_regions = []
		region_coords = []
		for y_level in y_starts:
			for x_level in x_starts:
				screen_regions.append(tf.sub_fractionate_3d_array(
					scn_grab_array,
					ref_data,
					start_row = y_level,
					start_col = x_level
				))
				region_coords.append((y_level,x_level))


		diff_array = [np.abs(region - ref_data) for region in screen_regions]
		mean_array = [np.mean(diff) for diff in diff_array]
		print(mean_array)
		closest_match_index = np.argmin(mean_array)
		closest_match_value = np.min(mean_array)
		print(f"closest val: {closest_match_value}")
		closest_match_coords = np.array(region_coords[closest_match_index])
		print(f"closest coords: {closest_match_coords}")
		closest_match_region = screen_regions[closest_match_index]
		print(f"closest region: {closest_match_region.shape}")



		n=1
		while closest_match_value > 1:
			if n >= 20:
				break
			print(n)
			n+=1
			previous_min = closest_match_value
			screen_regions.clear()
			px_factor = (closest_match_value / 255) /(n-0.5)
			px_move_dist = np.array([ref_height*px_factor, ref_width*px_factor], dtype=np.int16)
			if px_move_dist[0] < 1:
				px_move_dist[0] = 1
			if px_move_dist[1] < 1:
				px_move_dist[1] = 1

			print(f"px move dist array: {px_move_dist}")
			max_x = screen_shape[1] - px_move_dist[1]
			max_y = screen_shape[0] - px_move_dist[0]
			#coords are y then x because of how arrays have to work
			#also (0,0) is always the top left of the image, so going down means adding y, not subtracting y value.
			new_points = {
			"up": closest_match_coords + (-px_move_dist[0], 0),
			"down": closest_match_coords + (px_move_dist[0], 0),
			"left": closest_match_coords + (0, -px_move_dist[1]),
			"right": closest_match_coords + (0, px_move_dist[1]),
			"upr": closest_match_coords + (-px_move_dist[0], px_move_dist[1]),
			"upl": closest_match_coords + (-px_move_dist[0], -px_move_dist[1]),
			"dnr": closest_match_coords + (px_move_dist[0], px_move_dist[1]),
			"dnl": closest_match_coords + (px_move_dist[0], -px_move_dist[1]),
			}
			print(list(new_points.values()))
			for new_coord in new_points.values():
				if new_coord[0] > max_y:
					new_coord[0] = max_y
				elif new_coord[0] < 0:
					new_coord[0] = 0
				if new_coord[1] > max_x:
					new_coord[1] = max_x
				elif new_coord[1] < 0:
					new_coord[1] = 0
				screen_regions.append(tf.sub_fractionate_3d_array(
					scn_grab_array,
					ref_data,
					start_row=new_coord[0],
					start_col=new_coord[1]
				))
			diff_array = [np.abs(region - ref_data) for region in screen_regions]
			mean_array = [np.mean(diff) for diff in diff_array]
			print(mean_array)
			closest_match_index = np.argmin(mean_array)
			closest_match_value = np.min(mean_array)
			if previous_min < closest_match_value:
				pass
			else:
				closest_match_key = list(new_points.keys())[closest_match_index]
				closest_match_coords = new_points.get(closest_match_key)
				closest_match_region = screen_regions[closest_match_index]
				print("generating a closer match", "."*20)
				print(f"closest coords: {closest_match_coords}")
				print(f"closest val: {closest_match_value}")







		y_lim, x_lim, _ = closest_match_region.shape
		#highlight the screengrab red where it has placed the location of the reference image
		scn_grab_array[closest_match_coords[0]: closest_match_coords[0] +y_lim, closest_match_coords[1]: closest_match_coords[1] +x_lim] = [255, 0, 0]

		#ok so now I can consistently find my reference location, we can access that btw by using closest_match_coords variable, it has the upper-left corner pixel
		#so the grid is 10 squares wide, 20 squares up, so lets make a coord array relative to our anchor
		x_rel_offset = -195
		y_rel_offset = 33
		grid_px_width = 234
		grid_px_height = 495
		_with_offset_x = closest_match_coords[1] + x_rel_offset
		_with_offset_y = closest_match_coords[0] + y_rel_offset
		x_grid_vals = np.linspace(_with_offset_x, _with_offset_x - grid_px_width, num=10, dtype=np.int32)
		y_grid_vals = np.linspace(_with_offset_y, _with_offset_y - grid_px_height, num=20, dtype=np.int32)
		x_y_mesh = np.meshgrid(x_grid_vals, y_grid_vals)
		x_y_stacked = np.stack(x_y_mesh, axis=-1)

		# print(f"x_grid_vals: {x_grid_vals}")
		# print(f"y_grid_vals: {y_grid_vals}")
		# pp.pp(f"x_y_mesh: {x_y_mesh}")
		print("-"*100)
		# print(f"x_y_stacked: {x_y_stacked.shape}")
		# print(f"x_y_stacked\n: {x_y_stacked}")


		#use this to check calibration
		# for row in x_y_stacked:
		# 	for col in row:
		# 		x_px = col[0]
		# 		y_px = col[1]
		# 		scn_grab_array[y_px,  x_px] = np.array([255, 0, 0])
		#
		# final_image = Image.fromarray(scn_grab_array)
		# final_image.show()

		inverted_xy_arr = np.flipud(x_y_stacked)
		inverted_xy_arr = np.fliplr(inverted_xy_arr)

		print(f"my image array shape: {scn_grab_array.shape}")
		print(f"my coords shape: {inverted_xy_arr.shape}")
		print(inverted_xy_arr)

		board_pixels = scn_grab_array[inverted_xy_arr[:,:,1], inverted_xy_arr[:,:,0]]
		print("\nactual pixel grid:")
		print(board_pixels.shape)
		print(board_pixels)
		mean_board_pixels = np.mean(board_pixels, axis=-1, keepdims=True)
		print(f"\nmean board pixels: {mean_board_pixels.shape}")
		print(mean_board_pixels)

		print("\nfor loop start")
		for row_num, row in enumerate(mean_board_pixels):
			for col_num, col in enumerate(row):
				pixel_mean = col[0]
				print(f"row: {row_num}, col: {col_num}\nvalue: {pixel_mean}")
				if pixel_mean == 0:
					lowest_index = (row_num, col_num)
					print(f"lowest index: {lowest_index}")
					break
			if pixel_mean == 0:
				break

		bg_pixel = board_pixels[lowest_index]
		print(bg_pixel)

		

		final_image = Image.fromarray(board_pixels)
		final_image.show()





