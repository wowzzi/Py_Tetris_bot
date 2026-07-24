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
					simulation_grid, sim_pos_indexes = self.construct_a_move((col, row), cleaned_board, shape_array)
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

	def construct_a_move(self, start_xy_coord:tuple, clean_grid: np.ndarray, shape_array: np.ndarray):
		simulation_grid = clean_grid.copy()
		shape_dimensions = shape_array.shape
		start_x, start_y = start_xy_coord
		sim_pos_indexes = []

		for y_offset in range(shape_dimensions[0]):
			for x_offset in range(shape_dimensions[1]):
				current_grid_val = simulation_grid[start_y + y_offset][start_x + x_offset]
				simulation_grid[start_y + y_offset][start_x + x_offset] = current_grid_val + shape_array[y_offset][x_offset]
				if shape_array[y_offset][x_offset] == 1:
					sim_pos_indexes.append((start_y + y_offset, start_x + x_offset))

		return simulation_grid, sim_pos_indexes

	def check_for_hit(self, input_array: np.ndarray) -> bool:
		for n in input_array.flatten():
			if n == 2:
				return True
		return False

	def calculate_move_score(self, simulated_grid: np.ndarray, simulated_indexes: list, simulated_rotation: int):
		if simulated_grid is None or simulated_indexes is None:
			return stored_move(
			simulated_rotation,
			simulated_indexes,
			simulated_grid,
			5000,
			5000,
			0
			)

		y_coords = [position[0] for position in simulated_indexes]
		height_score = sum([(20-y) for y in y_coords])

		# print(f"range from min y_coords to 20: {list(range(min(y_coords), 20))}")
		# check for gaps created directly below the simulated move pieces
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
		)
		return move_obj

	def evaluate_all_moves(self):
		current_move_objects = self.simulated_move_objects

		# get any objects in the list which have a rows cleared >2
		short_list = [obj for obj in current_move_objects if obj.rows_cleared > 2]
		if len(short_list) > 0:
			return short_list[0]

		# short list the ones with the lowest blockage score
		min_blockage_score = min([obj.blockage_score for obj in current_move_objects])
		short_list = [obj for obj in current_move_objects if obj.blockage_score == min_blockage_score]
		if len(short_list) == 1:
			return short_list[0]

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
				 position_indexes: list,
				 final_move_grid: np.ndarray,
				 height_score: int,
				 blockage_score: int,
				 rows_cleared: int,
				 ):
		self.rotation_id = rotation_id
		self.position_indexes = position_indexes
		if self.position_indexes:
			self.min_x = min([position[1] for position in self.position_indexes])
		self.final_move_grid = final_move_grid
		self.height_score = height_score
		self.blockage_score = blockage_score
		self.rows_cleared = rows_cleared
		self.overall_score = ((self.blockage_score + 1) * self.height_score)/ (self.rows_cleared + 1)

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