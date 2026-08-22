import move_simulator as MS
import numpy as np

class tb_move_sim(MS.move_simulator):
	def __init__(self):
		super().__init__()

	def new_sim_moves(self, board_state_array: np.ndarray, shapes_data: dict):
		self.best_move = None
		self.simulated_move_objects.clear()
		board_height, board_width = board_state_array.shape

		# shapes data is a dict with 1 - 4 keys all integers.
		# each key holds another rotation variant of the current shape.
		# simulate with each rotation from the top down.
		prev_sim_grid = None
		prev_sim_pos_indexes = None
		for rotation_id, shape_array in shapes_data.items():
			shape_height, shape_width = shape_array.shape
			# print(f"\nrotation variant: {rotation_id}\n{shape_array}")
			for col in range(board_width - (shape_width - 1)):
				found_move_for_this_col = False
				for row in list(range(board_height))[:board_height - (shape_height - 1)]:
					simulation_grid, sim_pos_indexes = self.construct_a_move((row, col), board_state_array, shape_array)
					if self.check_for_hit(simulation_grid):
						# print("found hit")
						found_move_for_this_col = True
						final_grid = prev_sim_grid
						final_indexes = prev_sim_pos_indexes
						self.simulated_move_objects.append(
							self.calculate_move_score(final_grid, final_indexes, rotation_id))
						break
					prev_sim_grid = simulation_grid
					prev_sim_pos_indexes = sim_pos_indexes

				if not found_move_for_this_col:
					final_grid = simulation_grid
					final_indexes = sim_pos_indexes
					self.simulated_move_objects.append(
						self.calculate_move_score(final_grid, final_indexes, rotation_id))
