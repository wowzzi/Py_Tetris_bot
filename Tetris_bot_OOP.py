from pathlib import Path
from PIL import Image
import mss
from mss import tools
import numpy as np
# from numpy.lib.recfunctions import structured_to_unstructured

import tetris_helper_funcs as tf
import keyboard as kb
import pprint as pp
import time
import Tetris_square_obj as Tetob
import Tetromino_ref_grids as trg
import move_simulator as MS
import Timer_class




class TetrisGame:
	def __init__(self, monitor: int =0, scn_width: int=300, scn_height: int=300, mss_instance=None, fps = 8):
		self.mon_number = monitor
		self.width = scn_width
		self.height = scn_height
		self.sct = mss_instance
		self.screen_region = {}
		self.error_count = 0
		self.fps = fps
		self.time_per_frame = 1.00/self.fps
		print(self.time_per_frame)
		self.clock = Timer_class.timer(self.time_per_frame)

	def define_screen_region(self):
			monitor = self.sct.monitors[self.mon_number]
			mon_center_x = monitor['left'] + monitor['width'] // 2
			mon_center_y = monitor['top'] + monitor['height'] // 2

			top = mon_center_y - self.height // 2
			left = mon_center_x - self.width // 2
			# region defining portion of the screen to take screenshot of
			self.screen_region = {
				'top': top,
				'left': left,
				'width': self.width,
				'height': self.height,
				'mon': self.mon_number
			}
			print(self.screen_region)


	def convert_sct_to_array(self):
			screen_grab = self.sct.grab(self.screen_region)
			scn_grab_as_img = Image.new('RGB', screen_grab.size)
			RGB_pixel_tuple = zip(screen_grab.raw[2::4], screen_grab.raw[1::4], screen_grab.raw[::4])
			scn_grab_as_img.putdata(list(RGB_pixel_tuple))
			return np.array(scn_grab_as_img)


	def find_ref(self, ref_png_path, scrn_shot_array, search_resolution: int = 1) -> tuple:
		reference_game_screen = Image.open(ref_png_path)
		ref_data = np.asarray(reference_game_screen)
		ref_height, ref_width, _ = ref_data.shape

		# ref pixel height and width / search res
		ref_used_height = ref_height / search_resolution
		ref_used_width = ref_width / search_resolution

		# shape is equivalent to getting height and width as this is an np.array
		screen_shape = scrn_shot_array.shape
		y_iterations = screen_shape[0] / ref_used_height
		x_iterations = screen_shape[1] / ref_used_width

		# this limit clamps the positions to check the reference within the limits of the screenshot
		y_limit = screen_shape[0] - ref_height
		x_limit = screen_shape[1] - ref_width

		y_starts = [int(n * ref_used_height) for n in range(int(y_iterations)) if n * ref_used_height < y_limit]
		if isinstance(y_iterations, float):
			y_starts.append(y_limit)

		x_starts = [int(n * ref_used_width) for n in range(int(x_iterations)) if n * ref_used_width < x_limit]
		if isinstance(x_iterations, float):
			x_starts.append(x_limit)

		print(f"y_starts: {y_starts}\nx_starts: {x_starts}")
		print(screen_shape)

		screen_regions = []
		region_coords = []
		for y_level in y_starts:
			for x_level in x_starts:
				screen_regions.append(tf.sub_fractionate_3d_array(
					scrn_shot_array,
					ref_data,
					start_row=y_level,
					start_col=x_level
				))
				region_coords.append((y_level, x_level))

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

		n = 1
		while closest_match_value > 1:
			if n >= 20:
				break
			print(n)
			n += 1
			previous_min = closest_match_value
			screen_regions.clear()
			px_factor = (closest_match_value / 255) / (n - 0.5)
			px_move_dist = np.array([ref_height * px_factor, ref_width * px_factor], dtype=np.int16)
			if px_move_dist[0] < 1:
				px_move_dist[0] = 1
			if px_move_dist[1] < 1:
				px_move_dist[1] = 1

			print(f"px move dist array: {px_move_dist}")
			max_x = screen_shape[1] - px_move_dist[1]
			max_y = screen_shape[0] - px_move_dist[0]
			# coords are y then x because of how arrays have to work
			# also (0,0) is always the top left of the image, so going down means adding y, not subtracting y value.
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
					scrn_shot_array,
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
				print("generating a closer match", "." * 20)
				print(f"closest coords: {closest_match_coords}")
				print(f"closest val: {closest_match_value}")

		return closest_match_coords, closest_match_region

	def check_ref_location(self, scrn_shot_array):
		if hasattr(self, "ref_region"):
			ref_region = getattr(self, "ref_region")
			ref_region[:,:] = [255, 0, 0]
		if hasattr(self,"pixel_grid"):
			scrn_shot_array[self.pixel_grid[:, :, 1], self.pixel_grid[:, :, 0]] = [255,0,0]
		calibrated_img = Image.fromarray(scrn_shot_array)
		calibrated_img.show()

	def set_grid_dims(self, x_rel_offset=0, y_rel_offset=0, grid_px_width=10, grid_px_height=10):
		self.grid_x_offset = x_rel_offset
		self.grid_y_offset = y_rel_offset
		self.grid_width = grid_px_width
		self.grid_height = grid_px_height

	def generate_px_grid(self):
		_with_offset_x = self.closest_coords[1] + self.grid_x_offset
		_with_offset_y = self.closest_coords[0] + self.grid_y_offset
		x_grid_vals = np.linspace(_with_offset_x, _with_offset_x - self.grid_width, num=10, dtype=np.int32)
		y_grid_vals = np.linspace(_with_offset_y, _with_offset_y - self.grid_height, num=20, dtype=np.int32)
		x_y_mesh = np.meshgrid(x_grid_vals, y_grid_vals)
		x_y_mesh = np.stack(x_y_mesh, axis=-1)
		inverted_xy_arr = np.flipud(x_y_mesh)
		self.pixel_grid = np.fliplr(inverted_xy_arr)

	def generate_board_px_means(self):
		if not hasattr(self, "pixel_grid"):
			self.generate_px_grid()
		self.board_pixels = self.present_scn[self.pixel_grid[:,:,1], self.pixel_grid[:,:,0]]
		self.mean_rgb_vals = np.mean(self.board_pixels, axis=-1, keepdims=True, dtype=np.int16)

	def determine_bg_col(self):
		if not hasattr(self, "pixel_grid"):
			self.generate_px_grid()
		lowest_rgb = self.mean_rgb_vals[0,0,0]
		lowest_index = (0,0)
		for row_num, row in enumerate(self.mean_rgb_vals):
			for col_num, col in enumerate(row):
				pixel_mean = col[0]
				if pixel_mean < lowest_rgb:
					lowest_rgb = pixel_mean
					lowest_index = (row_num, col_num)
				print(f"row: {row_num}, col: {col_num}\nvalue: {pixel_mean}")
		print(f"lowest index: {lowest_index}, lowest value: {lowest_rgb}")

		self.bg_val =lowest_rgb
		print(self.bg_val)

	def determine_board_state(self):
		"""loop through all pixels from the current self.mean_rgb_vals
		that contains the mean rgb for all pixels in a broadcastable grid shape: 20,10,1
		if a mean is found that is > bg which is 0, find all connected squares to it
		if it is connected to the bottom directly or indirectly through others it should be determined to be fixed
		so to do that we are going to initially recreate the mean px grid as 0 for bg or 1 for a shape of some kind
		ooo we could create a separate object for the mean pixels detected, that can store its mean and position
		we can then use those values to compare to all the grid-space around in a 4x4 grid (16 total) which is big
		enough to contain all shapes
		so instead of keeping a grid of ints we keep a grid of objects"""
		if not hasattr(self, "tetris_obj_grid"):
			self.tetris_obj_grid = []
			for row_num, row in enumerate(self.mean_rgb_vals):
				col_list = []
				for col_num, col in enumerate(row):
					pixel_mean = col[0]
					col_list.append(Tetob.tetris_square(row_num, col_num, pixel_mean, self.bg_val))
				self.tetris_obj_grid.append(col_list)

			for row in self.tetris_obj_grid:
				for obj in row:
					obj.get_neighbours(self.tetris_obj_grid)
		else:
			for row_num, row in enumerate(self.tetris_obj_grid):
				for col_num, obj in enumerate(row):
					obj.update_val(self.mean_rgb_vals[row_num, col_num])

	def add_error(self):
		self.error_count +=1

	def reset_error_count(self):
		self.error_count = 0

	def get_active_objs(self):
		"""
		lists any object in the self.tetris_obj_grid
		of which attr .is_bg is False
		:return list:
		"""
		active_objs = []
		for row in self.tetris_obj_grid:
			for obj in row:
				if not obj.is_bg:
					active_objs.append(obj)
		return active_objs

	def infect_neighbours(self, neighbouring_objs, result: list = None, iteration = 0):
		print(iteration)
		iteration += 1
		print(f"neighbours objects: {neighbouring_objs}")
		print(f"current result list: {result}")
		if result is None:
			infected_list = []
		else:
			infected_list = result
		print(f"infected list: {infected_list}")
		neighbouring_objs = [obj for obj in neighbouring_objs if not obj.is_static]
		print(f"neighbours objects (after purging): {neighbouring_objs}")

		for obj in neighbouring_objs:
			obj.is_static = True
		if len(neighbouring_objs) > 1:
			print("re-running the recursion")
			for n, obj in enumerate(neighbouring_objs, start=0):
				print(f"loop {n} for neighbours")
				infected_list.extend(self.infect_neighbours(obj.return_active_neighbours(), result = infected_list, iteration=iteration))

		else:
			print("len objects is 0 so returning the list of objects now")
		return infected_list



	def determine_if_static(self, active_objs):
		border_pieces = [obj for obj in active_objs if obj.is_bottom_border]
		if len(border_pieces) < 1:
			print(f"all current pieces are active (one shape on screen)"
				  f"\nthose squares are at: ")
			for obj in active_objs:
				print(obj.index)
		else:
			for piece in border_pieces:
				#infect connected pieces
				piece.is_static = True

				connected_pieces = piece.return_active_neighbours()
				while len(connected_pieces) > 0:
					for neighbour in connected_pieces:
						neighbour.is_static = True

	def list_obj_neighbours_in_dict(self):
		"""
		gets all non background objects in the current self.tetris_obj_grid.
		then returns their neighbouring non background objects.
		appends the current obj and its neighbours to a list and places that list in a dict

		this function is for sorting which objects are grouped together.
		see follow on function self.sort_obj_dict where the sorting is done.
		:return dict:
		"""
		active_objs = self.get_active_objs()
		grouped_objects = {}

		for n, obj in enumerate(active_objs, start=1):
			active_neighbours = obj.return_active_neighbours()
			active_neighbours.append(obj)
			grouped_objects[f"group{n}"] = active_neighbours

		return grouped_objects

	def sort_obj_dict(self, input_dict):
		"""
		:param input_dict:
		:return altered_dict:

		input_dict intended to be 1 dimensional, that is 1 key 1 value, no nested dictionaries.
		each value in the input dict must be a list.
		this function checks the values in each list compared to the other lists within the same dict.
		if it finds a match it extends matching list with the values in the current list.
		then it clears the current list .
		it assumes the items in each individual list are linked and should be kept together.
		returns the filtered/sorted dict.
		"""
		altered_dict = input_dict.copy()
		any_match_found = True
		while any_match_found:
			any_match_found = False # assume we dont find a match, until we do
			# iterate through the input dict for the first time
			for key, first_list in altered_dict.items():
				found = False
				for current_value in first_list:
					if found:
						break
					# iterate the same dict the second time
					for second_key, second_list in altered_dict.items():
						if key == second_key:
							continue
							# ignore checking the same list to the same list
						if current_value in second_list:
							second_list.extend(first_list)
							first_list.clear()
							found = True
							any_match_found = True
							break
		# remove duplicate items from the sorted dict
		empty_keys = []
		for key, value in altered_dict.items():
			if len(value) > 0:
				altered_dict[key] = list(set(value))
			else:
				empty_keys.append(key)

		# remove empty keys
		for key in empty_keys:
			altered_dict.pop(key)

		return altered_dict

	def find_active_group(self, input_dict):
		"""
		input dict intended to be sorted/grouped tetris objects dict generated from self.sort_obj_dict.
		returned string is the key to acess the correct tetris shape type.

		found bug where screencap is taken without tetromino fully visible.
		this ends up with the static objects selected as the main tetromino group.

		:param input_dict:
		:return string:
		"""
		sorting_dict = {}
		active_key = None
		# if len(input_dict) == 1:
		# 	return list(input_dict.keys())[0]

		for key, value in input_dict.items():
			if len(value) == 4:
				sorting_dict[key] = value

		if len(sorting_dict) == 1:
			return list(sorting_dict.keys())[0]
		elif len(sorting_dict) >1:
			eliminated_list = []
			for key, value in sorting_dict.items():
				for obj in value:
					if obj.is_bottom_border:
						eliminated_list.append(key)

			eliminated_list = list(set(eliminated_list))
			for elimination_key in eliminated_list:
				sorting_dict.pop(elimination_key)

			active_key = list(sorting_dict.keys())[0]


		return active_key

	def generate_shape_coords(self, tetris_objects: list):
		indexes = [obj.index for obj in tetris_objects]

		rows = [coord[0] for coord in indexes]
		cols = [coord[1] for coord in indexes]

		min_row = min(rows)
		min_col = min(cols)

		min_array = np.array([min_row, min_col])

		normalised_indexes = []
		for index in indexes:
			normalised_indexes.append(index - min_array)

		normalised_indexes = np.array(normalised_indexes)

		return normalised_indexes

	def generate_shape_grid(self, shape_coordinates):
		shaped_array = np.zeros((4,4))
		for coord in shape_coordinates:
			shaped_array[coord[0], coord[1]] = 1

		return shaped_array

	def generate_binary_grid(self) -> np.ndarray:
		if not hasattr(self, "tetris_obj_grid"):
			return
		binary_array = []
		for row in self.tetris_obj_grid:
			binary_array.append([int(not obj.is_bg) for obj in row])
		return np.array(binary_array, dtype=np.int8)


	def calc_rotation_needed(self, rotation_id_current, rotation_id_final):
		return rotation_id_final - rotation_id_current

	def rotation_automate(self, rotation_score):
		# print("rotation automation function:")
		# print(rotation_score)
		rotation_timer = Timer_class.timer(0.04)

		#rotate left
		while rotation_score < 0:
			print("pressing z")
			kb.send('z')
			rotation_score += 1
			while True:
				rotation_timer.tick()
				if rotation_timer:
					rotation_timer.reset()
					break

		while rotation_score > 0:
		#rotate right
			# 72 is the scan code for up arrow key
			print("pressing up")
			kb.send(72)
			rotation_score -= 1
			while True:
				rotation_timer.tick()
				if rotation_timer:
					rotation_timer.reset()
					break

	def calculate_x_translation_required(self, rotation_score, current_active_objs, target_column, piece_id):
		current_min_x = min([obj.index[1] for obj in current_active_objs])
		x_offset = 0

		if rotation_score == 0:
			pass
		else:
			if piece_id == "long":
				if rotation_score > 0:
					x_offset = 2
				else:
					x_offset = 1
			else:
				if rotation_score == 1 or rotation_score == -3:
					x_offset = 1
		self.translation_automate(current_min_x + x_offset, target_column)

	def translation_automate(self, current_x, target_x):
		move_score = target_x - current_x
		print(f"required moves: {move_score}")
		move_timer = Timer_class.timer(0.04)

		while move_score > 0:
			print("pressing right")
			kb.send(77)
			move_score -= 1
			while True:
				move_timer.tick()
				if move_timer:
					move_timer.reset()
					break

		while move_score < 0:
			print("pressing left")
			kb.send(75)
			move_score += 1
			while True:
				move_timer.tick()
				if move_timer:
					move_timer.reset()
					break

	def press_space(self):
		kb.send(57)






######################
#### Script Start ####
######################

mss_instance = mss.MSS()
ref_png_path = Path(__file__).with_name("Pause_button_ref.png")

game_bot = TetrisGame(monitor=2, scn_width=820, scn_height=1000, mss_instance=mss_instance, fps=5)
game_bot.define_screen_region()
game_bot.set_grid_dims(x_rel_offset=-195, y_rel_offset=33, grid_px_width=234, grid_px_height=495)
trg_handler = trg.ref_grid_handler()
move_simulator = MS.move_simulator()

setup_done = False
while True:
	# wait for next event.
	event = kb.read_event()
	if event.event_type == kb.KEY_DOWN and event.name == "p":
		game_bot.present_scn = game_bot.convert_sct_to_array()
		game_bot.closest_coords, game_bot.ref_region = game_bot.find_ref(ref_png_path, game_bot.present_scn, search_resolution=2)
		game_bot.generate_px_grid()
		game_bot.generate_board_px_means()
		# game_bot.check_ref_location(game_bot.present_scn)
		game_bot.determine_bg_col()
		game_bot.determine_board_state()
		setup_done = True

	elif setup_done and event.event_type == kb.KEY_DOWN and event.name == "o":
		print("o pressed")

		n = 0
		# game_bot.clock.reset()
		# while True:
		#
		# 	game_bot.clock.tick()
		# 	if game_bot.clock:

		# gets the screenshot, makes it an numpy array
		game_bot.present_scn = game_bot.convert_sct_to_array()
		game_bot.generate_board_px_means()
		game_bot.determine_board_state() # makes a 2-d list filled with tetris objects from Tetris_square_obj rather than just mean rgb

		# groups objects into a dict and sorts them based on proximity
		obj_neighbour_dict = game_bot.list_obj_neighbours_in_dict()
		sorted_neighbour_dict = game_bot.sort_obj_dict(obj_neighbour_dict)

		# this is a string; key used to acess the shape data usually group4
		active_tetris_group_key = game_bot.find_active_group(sorted_neighbour_dict)
		if not active_tetris_group_key:
			print("couldn't find the active group")

			game_bot.add_error()
			if game_bot.error_count > 50:
				break
			# add some logic to turn off bot if 3 in a row are unable to find, probably means the user tabbed out
			continue
		else:
			game_bot.reset_error_count()
		#returns a list of objects that are currently involved with the active piece
		active_tetris_objects = sorted_neighbour_dict.get(active_tetris_group_key)

		# print(f"active tetris group: {active_tetris_group_key}")
		# for obj in active_tetris_objects:
		# 	print(f"Object ID: {obj}"
		# 		  f"\nObject index: {obj.index}")

		# normalised coords takes the index of each object in the active group and subtracts the minimum from each dimension
		normalised_coords = game_bot.generate_shape_coords(active_tetris_objects)
		# generates a 4x4 shape grid to comapre to the reference 4x4 grids so I can tell which shape it is
		shape_grid = game_bot.generate_shape_grid(normalised_coords)

		# remember trg_handler stands for Tetromino ref grids handler (stored all the 4x4 and smaller grids for tetromino reference here)
		tet_shape_key, rotation_id = trg_handler.determine_tetromino(shape_grid)
		# minimised grid is just the smallest dimension array to hold the shape in binary
		minimised_shape_dict = trg_handler.minimised_data.get(tet_shape_key)

		# just a 20x10 dimensional array filled with 1's where shapes exist and 0's where they dont, inteded for simulations
		binary_board_state = game_bot.generate_binary_grid()

		# setup to test if I can find a match between previous and current board states
		current_clean_board = move_simulator.generate_clean_binary_board(binary_board_state, active_tetris_objects)
		# print("current cleaned board")
		# print(current_clean_board)
		previous_clean_board = move_simulator.final_move_grid
		# print("previous cleaned board")
		# print(previous_clean_board)
		if current_clean_board is None or previous_clean_board is None:
			pass
		else:
			difference = abs(current_clean_board - previous_clean_board)
			if difference.mean() == 0:
				print("LAST MOVE ACTUALLY MATCHED THE INTENDED MOVE!!!!")

		# class object to handle simulated board states and produce the optimal move
		move_simulator.simulate_moves(binary_board_state, active_tetris_objects, minimised_shape_dict)
		# print(f"lowest score achieved: {move_simulator.min_score}")
		# print(f"\nfinal position rotation id: {move_simulator.rotation_id}")
		# print(f"\nfinal positional indexes: {move_simulator.position_indexes}")
		# print(f"\nfinal move grid: {move_simulator.final_move_grid}")
		# printf("\nfinal move column: {move_simulator.final_move_col}"))


		# need to calculate how many button presses to do the move from the current position
		# then i will figure out how I implement that in keyboard or autogui

		required_rotate = game_bot.calc_rotation_needed(rotation_id, move_simulator.rotation_id)
		print(f"required number of rotations: {required_rotate}")
		game_bot.rotation_automate(required_rotate)
		game_bot.calculate_x_translation_required(required_rotate, active_tetris_objects, move_simulator.final_move_col, tet_shape_key)

		# if n >= 3:
		time.sleep(0.2)
		game_bot.press_space()
			# n=0
		# n+=1
		# time.sleep(0.2)
		# game_bot.clock.reset()
		print("o ran")

# thoughts from last session is that the keyboard keypresses are too fast, use time module to add a delay

	elif event.event_type == kb.KEY_DOWN and event.name == "q":
		break



