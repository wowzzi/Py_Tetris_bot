import numpy as np
import pprint as pp

class move_simulator:
	def __init__(self):
		self.best_move = None
		self.simulated_move_objects = []

	def simulate_moves(self, board_state_array: np.ndarray, active_tetris_objects:list, shapes_data:dict):
		self.best_move = None
		self.simulated_move_objects.clear()
		board_height, board_width = board_state_array.shape

		# print(board_height, board_width)
		cleaned_board = board_state_array.copy()
		for obj in active_tetris_objects:
			cleaned_board[obj.index] = 0

		# shapes data is a dict with 1 - 4 keys all integers.
		# each key holds another rotation variant of the current shape.
		# simulate with each rotation from the top down.
		prev_sim_grid = None
		prev_sim_pos_indexes = None
		for rotation_id, shape_array in shapes_data.items():
			shape_height, shape_width = shape_array.shape
			# print(f"\nrotation variant: {rotation_id}\n{shape_array}")
			for col in range(board_width-(shape_width-1)):
				found_move_for_this_col = False
				for row in list(range(board_height))[:board_height-(shape_height-1)]:
					simulation_grid, sim_pos_indexes = self.construct_a_move((row, col), cleaned_board, shape_array)
					if self.check_for_hit(simulation_grid):
						# print("found hit")
						found_move_for_this_col = True
						final_grid = prev_sim_grid
						final_indexes = prev_sim_pos_indexes
						self.simulated_move_objects.append(self.calculate_move_score(final_grid, final_indexes, rotation_id))
						break
					prev_sim_grid = simulation_grid
					prev_sim_pos_indexes = sim_pos_indexes

				if not found_move_for_this_col:
					final_grid = simulation_grid
					final_indexes = sim_pos_indexes
					self.simulated_move_objects.append(self.calculate_move_score(final_grid, final_indexes, rotation_id))

	def construct_a_move(self, start_pos:tuple, clean_grid: np.ndarray, shape_array: np.ndarray) -> tuple:
		"""
		parameters: start_pos:tuple, clean_grid:np.ndarray, shape_array:np.ndarray
		returns: tuple[np.ndarray, np.ndarray]

		start_pos is (row, col), and represents the current position to simulate placing the move.
		clean_grid is a binary construction of the board without the active shape present (preventing collisons with self).
		shape_array is an array with the binary drawing for the current shape (from TRG module).

		shape_array.nonzero() returns the indexes of positions in the shape grid that are non-zero as tuple.
		np.stack combines the two arrays in the tuple to combine into one np.ndarray
		adding the shape_coords + start_pos gives you the actual indexes that the move needs to be placed.
		blank_construct is making a blank 20x10 grid (full of zeros) and I slice in the simulation coordinates and set them to 1.
		simulation_grid is just the addition of 2 20x10 grids, where I've added in the simulated coorindates.
		"""
		shape_coords = np.stack(shape_array.nonzero(), axis=-1)
		real_idxs = shape_coords + start_pos
		blank_construct = np.zeros((20,10))
		blank_construct[real_idxs[:,0], real_idxs[:, 1]] = 1
		simulation_grid = clean_grid + blank_construct
		simulation_grid =  simulation_grid.astype(np.uint8)

		return simulation_grid, real_idxs

	def check_for_hit(self, input_array: np.ndarray) -> bool:
		return len(input_array[input_array == 2]) > 0

	def calculate_move_score(self, simulated_grid: np.ndarray, simulated_indexes: np.ndarray, simulated_rotation: int):
		if simulated_grid is None or simulated_indexes is None:
			return stored_move(
			simulated_rotation,
			simulated_indexes,
			simulated_grid,
			5000,
			5000,
			0,
			1,
			1
			)

		all_idxs = np.stack(simulated_grid.nonzero(), axis=-1)
		height_range_factor = ((np.max(all_idxs[:,0]) - np.min(all_idxs[:,0])) + 1)/20
		width_range_factor = ((np.max(all_idxs[:,1]) - np.min(all_idxs[:,1])) + 1)/10


		height_score = np.sum(20 - simulated_indexes[:,0])
		blockage_score = 0

		for row, col in simulated_indexes:
			if row + 1 < len(simulated_grid):
				cell_below = simulated_grid[row+1][col]
				if cell_below == 0:
					blockage_score += 1

		# check if we complete any lines
		num_completed_rows = 0
		for row in simulated_grid:
			zero_only_array = row[row==0]
			if len(zero_only_array) == 0:
				num_completed_rows += 1

		move_obj = stored_move(
			simulated_rotation,
			simulated_indexes,
			simulated_grid,
			height_score,
			blockage_score,
			num_completed_rows,
			height_range_factor,
			width_range_factor
		)
		return move_obj

	def evaluate_all_moves(self):
		current_move_objects = self.simulated_move_objects
		min_overall_height = min(obj.height_score for obj in current_move_objects)
		max_overall_height = max(obj.height_score for obj in current_move_objects)
		adjusted_max = max_overall_height - min_overall_height
		if adjusted_max == 0:
			adjusted_max = max_overall_height
		for object in current_move_objects:
			normal_height = (object.height_score - min_overall_height) / adjusted_max
			setattr(object, "normalised_height", normal_height)
		# get any objects in the list which have a rows cleared >2
		short_list = [obj for obj in current_move_objects if obj.rows_cleared > 2]
		if len(short_list) > 0:
			return short_list[0]

		# short list the ones with the lowest blockage score
		min_blockage_score = min(obj.blockage_score for obj in current_move_objects)
		short_list = [obj for obj in current_move_objects if obj.blockage_score == min_blockage_score]
		if len(short_list) == 1:
			if short_list[0].normalised_height < 0.5:
				return short_list[0]
			else:
				print("evaluate by score")
				return self.evaluate_moves_by_score()

		# check if those remaining clear 2 lines
		cleared_two_shortlist = [obj for obj in short_list if obj.rows_cleared == 2]
		cleared_list_length = len(cleared_two_shortlist)
		if cleared_list_length == 1:
			return cleared_two_shortlist[0]
		elif cleared_list_length > 1:
			short_list = cleared_two_shortlist

		# get those remaining with the lowest height score
		min_height_score = min(obj.height_score for obj in short_list)
		short_list = [obj for obj in short_list if obj.height_score == min_height_score]
		if len(short_list) == 1:
			return short_list[0]

		# finally select the one remaining one with the lowest x coordinate
		min_x_coord = min(obj.min_x for obj in short_list)
		short_list = [obj for obj in short_list if obj.min_x == min_x_coord]
		return short_list[0]

	def evaluate_moves_by_score(self):
		return min(self.simulated_move_objects)

	def find_best_move(self):
		self.best_move = self.evaluate_all_moves()

	def generate_clean_binary_board(self, board_state_array: np.ndarray, active_tetris_objects: list) -> np.ndarray:
		if board_state_array is None or active_tetris_objects is None:
			return None
		cleaned_board = board_state_array.copy()
		for obj in active_tetris_objects:
			cleaned_board[obj.index] = 0

		return cleaned_board

class stored_move:
	def __init__(self,
				 rotation_id: int,
				 position_indexes: np.ndarray,
				 final_move_grid: np.ndarray,
				 height_score: int,
				 blockage_score: int,
				 rows_cleared: int,
				 height_range_factor: int,
				 width_range_factor: int,
				 ):
		self.rotation_id = rotation_id
		self.position_indexes = position_indexes
		if self.position_indexes is not None:
			self.min_x = np.min(self.position_indexes[:,1])
			self.min_y = np.min(self.position_indexes[:,0])
		self.final_move_grid = final_move_grid
		self.height_score = height_score
		self.blockage_score = blockage_score
		self.rows_cleared = rows_cleared
		self.overall_score = ((((self.blockage_score * 0.5) + 1) * self.height_score))/ ((self.rows_cleared + 1))

	def __lt__(self, other):
		return self.overall_score < other.overall_score

	def __gt__(self, other):
		return self.overall_score > other.overall_score

	def __eq__(self, other):
		return self.overall_score == other.overall_score

	def __le__(self, other):
		return self.overall_score <= other.overall_score

	def __ge__(self, other):
		return self.overall_score >= other.overall_score

	def __str__(self):
		return str(self.overall_score)