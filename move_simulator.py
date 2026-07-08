import numpy as np
import pprint as pp

part_completed_row_bonus = {
	1: 0.8,
	2: 0.6,
	3: 0.4,
	4: 0.2,
	5: 0.1,
	6: 0.0,
	7: 0.0,
	8: 0.0,
	9: 0.0,
	10: 0.0
}


class move_simulator:
	def __init__(self):
		self.min_score = None
		self.rotation_id = None
		self.position_indexes = None
		self.final_move_grid = None
		self.final_move_col = None

	def simulate_moves(self, board_state_array: np.ndarray, active_tetris_objects:list, shapes_data:dict):
		self.min_score = None
		self.rotation_id = None
		self.position_indexes = None
		self.final_move_grid = None
		self.final_move_col = None
		board_height, board_width = board_state_array.shape

		# print(board_height, board_width)
		cleaned_board = board_state_array.copy()
		for obj in active_tetris_objects:
			cleaned_board[obj.index] = 0

		# shapes data is a dict with 1 - 4 keys all integers.
		# each key holds another rotation variant of the current shape.
		# simulate with each rotation from the bottom of the board upwards.
		previous_move = None
		previous_position = None
		for rotation_id, shape_array in shapes_data.items():
			shape_height, shape_width = shape_array.shape
			# print(f"\nrotation variant: {rotation_id}\n{shape_array}")
			for col in range(board_width-(shape_width-1)):
				found_move_for_this_col = False
				for row in list(range(board_height))[:board_height-(shape_height-1)]:
					simulated_move, simulated_position = self.construct_a_move((col, row), cleaned_board, shape_array)
					if self.check_for_hit(simulated_move):
						# print("found hit")
						found_move_for_this_col = True
						final_move = previous_move
						final_position = previous_position
						move_score = self.calculate_move_score(final_move, final_position)
						# print(f"for column: {col}\nrotation id: {rotation_id}\nthe move scored: {move_score}\n{shape_array}")
						self.update_lowest_score(move_score, rotation_id, final_position, final_move, col)
						break
					previous_move = simulated_move
					previous_position = simulated_position



				if not found_move_for_this_col:
					final_move = simulated_move
					final_position = simulated_position
					move_score = self.calculate_move_score(final_move, final_position)
					self.update_lowest_score(move_score, rotation_id, final_position, final_move, col)

						# stuff to do when we have a hit
					# next thing to do is evaluate when any square in the simulated_move grid = 2
					# do this by flattening the array and iterating over for a 2
					# also save the previously simulated move because that will be the move used for that x/y.


	def construct_a_move(self, start_xy_coord:tuple, clean_grid: np.ndarray, shape_array: np.ndarray):
		clean_grid = clean_grid.copy()
		shape_dimensions = shape_array.shape
		start_x, start_y = start_xy_coord
		position_indexes = []

		for y_offset in range(shape_dimensions[0]):
			for x_offset in range(shape_dimensions[1]):
				current_grid_val = clean_grid[start_y + y_offset][start_x + x_offset]
				clean_grid[start_y + y_offset][start_x + x_offset] = current_grid_val + shape_array[y_offset][x_offset]
				position_indexes.append((start_y + y_offset, start_x + x_offset))

		return clean_grid, position_indexes



	def check_for_hit(self, input_array: np.ndarray) -> bool:
		for n in input_array.flatten():
			if n == 2:
				return True
		return False

	def calculate_move_score(self, simulated_move: np.ndarray, simulated_position: list):
		# print(f"sim move, shape: {simulated_move.shape}")
		# pp.pp(simulated_move)
		# print("sim pos")
		# pp.pp(simulated_position)
		if simulated_move is None or simulated_position is None:
			return 500
		y_coords = [position[0] for position in simulated_position]
		x_coords = [position[1] for position in simulated_position]

		y_coord_sum_score = sum([(20-y)**2 for y in y_coords])
		height_penalty = y_coord_sum_score

		x_min, x_max = min(x_coords), max(x_coords)

		# print(f"height penalty: {height_penalty}")
		# print(f"y_coords from sim position: {y_coords}")
		vertical_gap_penalty = 0
		horizontal_gap_penalty = 0
		# print(f"range from min y_coords to 20: {list(range(min(y_coords), 20))}")
		# check gap in y direction only from the shape downwards, minimise leaving gaps directly below
		for row, col in simulated_position:
			col_slice = simulated_move[row:20].T[col]
			for n, binary_no in enumerate(col_slice, start =1):
				if binary_no == 0:
					vertical_gap_penalty += 10.0 + 2.0/n

			# for checking gaps on either side of the tetromino
			row_slice = simulated_move[row][col-1:col+2]
			for binary_no in row_slice:
				if binary_no == 0:
					horizontal_gap_penalty += 5.0

		# check if we complete a line
		divisor_reward = 1
		num_completed_rows = 1
		unique_rows = list(set(y_coords))
		for row in unique_rows:
			row_slice = simulated_move[row]
			zero_count = len(row_slice[row_slice == 0])

			if zero_count == 0:
				divisor_reward += (1.0*num_completed_rows)
				num_completed_rows +=1.0

			additional_bonus = part_completed_row_bonus.get(zero_count, 0)
			divisor_reward += additional_bonus



		# for col in range(x_min, x_max+1):
		# 	col_heights =[]
		# 	for position in simulated_position:
		# 		if position[1] == col:
		# 			col_heights.append(position[0])
		# 	max_col_height = min(col_heights) # min because coordinate of 19 height is actually at the bottom.
		# 	gaps_in_a_row = 1
		# 	for row in range(max_col_height, 20):
		# 		if simulated_move[row][col] == 0:
		# 			gap_penalty += 10 * gaps_in_a_row
		# 			gaps_in_a_row += 1
		# 		else:
		# 			gaps_in_a_row = 1

		# print(f"gap penalty: {gap_penalty}")

		# for n, row in enumerate(range(min(y_coords), 20), start=0):
		# 	# print(f"n: {n}, row: {row}")
		# 	for col in simulated_move[row]:
		# 		if col == 0:
		# 			gap_penalty += 2**n
		return (height_penalty + vertical_gap_penalty + horizontal_gap_penalty) / divisor_reward

	def update_lowest_score(self, new_score, current_rotation, current_position_indexes, final_move_grid, final_move_col):
		if self.min_score is None:
			self.min_score = new_score
			self.rotation_id = current_rotation
			self.position_indexes = current_position_indexes
			self.final_move_grid = final_move_grid
			self.final_move_col = final_move_col
		elif self.min_score > new_score:
			self.min_score = new_score
			self.rotation_id = current_rotation
			self.position_indexes = current_position_indexes
			self.final_move_grid = final_move_grid
			self.final_move_col = final_move_col

	def generate_clean_binary_board(self, board_state_array: np.ndarray, active_tetris_objects: list) -> np.ndarray:
		if board_state_array is None or active_tetris_objects is None:
			return None
		cleaned_board = board_state_array.copy()
		for obj in active_tetris_objects:
			cleaned_board[obj.index] = 0

		return cleaned_board
