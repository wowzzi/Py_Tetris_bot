import Tetris_bot_OOP as tb
import keyboard as kb
import pprint as pp
import numpy as np
import Timer_class
import threading
import time
import Thread_bot_move_sim as MS
import action_queue as aq

#####################
### Tetrobot_v1.0 ###
#####################

class tetris_thread_bot(tb.TetrisGame):
	def __init__(self,  monitor: int =0, scn_width: int=300, scn_height: int=300, mss_instance=None, fps: int = 8, action_timer_delay: float = 0.04):
		super().__init__(monitor, scn_width, scn_height, mss_instance, fps, action_timer_delay)
		self.move_simulator = MS.tb_move_sim()
		self.init_frame_states()
		self.frame_history = [None for n in range(10)]
		self.queue = aq.queue_system(self.delay_time)
		self.move_clock = Timer_class.timer(self.delay_time)
		self.stage = 1
		self.stage_2_error = False
		self.clock.set_sleep_time(10)

	def init_frame_states(self):
		self.prev_ones_count = 0
		self.ones_count = 0
		blank_frame = np.zeros((20,10), dtype=np.uint8)
		self.frame_count = 0
		self.board_state = blank_frame.copy()
		self.prev_board_state = blank_frame.copy()
		self.significant_frame = blank_frame.copy()

	def update_screen_shot(self):
		self.frame_count += 1
		self.present_scn = self.optimised_scn_grab()
		self.generate_minimised_px_means()
		difference = np.abs(self.mean_rgb_vals - self.bg_val)
		return ((difference > 2).astype(np.uint8)).reshape((20,10))

	def shift_list(self, input_list, new_val):
		input_list.insert(0, new_val)
		input_list.pop(-1)

	def process_new_screen(self, new_screen):
		self.prev_board_state = self.board_state.copy()
		self.board_state = new_screen.copy()
		self.shift_list(self.frame_history, self.board_state)
		self.prev_ones_count = self.ones_count
		self.ones_count = len(self.board_state[self.board_state==1])
		self.delta_ones = self.ones_count - self.prev_ones_count
		if self.delta_ones > 0:
			self.significant_frame = self.prev_board_state.copy()
			return True
		return False

	def _get_argones(self, input_binary: np.ndarray) -> np.ndarray:
		"""
		parameters: input_binary
		returns: np.ndarray
		input_binary is the board state 1/0 grid which represents the current state of the game
		np.where replaces any value in the grid which isn't 1 with a zero, then .nonzero() returns indexes of nonzeros.
		indexes are returned as an array shape (2, number_of_ones), np.stack combines them into a coordinate array. shape (n,2)
		"""
		return np.stack((np.where(input_binary !=1, 0, 1)).nonzero(), axis=-1)

	def find_shape_indexes(self, frame_one: np.ndarray, reference_frame:np.ndarray) -> np.ndarray:
		summed_arr = np.add(frame_one, reference_frame, dtype=np.uint8)
		return self._get_argones(summed_arr)

	def make_shape_grid(self, input_coords: np.ndarray) -> np.ndarray:
		"""
		parameter: input_coords
		intended to be an np.ndarray of shape (x, 2) where x is typically 4.
		"""
		if len(input_coords) == 0:
			return None
		row_min_coord = (input_coords[:,0]).min()
		col_min_coord = (input_coords[:,1]).min()

		normalised_coords = input_coords - np.array([row_min_coord, col_min_coord])

		blank_array = np.zeros((4,4), dtype=np.uint8)
		blank_array[normalised_coords[:,0], normalised_coords[:,1]] = 1
		return blank_array

	def calculate_x_translation(self) -> int:
		current_min_x = np.min(self.active_coords[:,1])
		x_offset = 0
		if self.required_rotate == 0:
			pass
		else:
			if self.tet_shape_key == "long":
				if self.required_rotate > 0:
					x_offset = 2
				else:
					x_offset = 1
			else:
				if self.required_rotate == 1 or self.required_rotate == -3:
					x_offset = 1
		return self.best_move_obj.min_x - (current_min_x + x_offset)

	def automate_rotations(self):
		rotation_score = self.required_rotate
		while rotation_score < 0:
			# rotate left
			self.move_clock.tick()
			if self.move_clock:
				self.press_z()
				rotation_score += 1
				self.move_clock.reset()

		while rotation_score > 0:
			# rotate right
			self.move_clock.tick()
			if self.move_clock:
				self.press_up()
				rotation_score -= 1
				self.move_clock.reset()



	def automate_left_right(self):
		move_score = self.move_score
		while move_score >  0:
			self.move_clock.tick()
			if self.move_clock:
				self.press_right()
				move_score -= 1
				self.move_clock.reset()

		while move_score < 0:
			self.move_clock.tick()
			if self.move_clock:
				self.press_left()
				move_score += 1
				self.move_clock.reset()

	def step_one_scn_shotting(self) -> bool:
		"""
		First step of the tetrobot flow:
		-> grabs a screenshot (new_screen)
		-> determines if it is a new piece that its observed
		-> returns True if its a new piece (tetromino) else False
		"""
		new_screen = self.update_screen_shot()
		return self.process_new_screen(new_screen)

	def step_two_shape_attributes(self):
		"""
		Second step of the tetrobot flow:
		-> finds the index of the active tetromino by comparing to the last significant frame
		-> handles an edge case where more than 4 coordinates are passed, cuts those down with some array slicing
		-> gets the shape grid which is a 4x4 geometric represntation of the tetromino
		-> uses the 4x4 shape grid to get the tetromino shape key from TRG class and rotation id
		-> uses the tetromino shape key to get the minimised shape dict, which is also a geometric representation..
		.. of the tetromino, but all the dimensions are minimised as small as possible
		"""
		self.active_coords = self.find_shape_indexes(self.board_state, self.significant_frame)
		if len(self.active_coords) > 4:
			row_min_coord = (self.active_coords[:, 0]).min()
			col_min_coord = (self.active_coords[:, 1]).min()
			normalised_coords = self.active_coords - np.array([row_min_coord, col_min_coord])
			cleaned_coords = self.active_coords[(self.active_coords[:, 0] < 4) & (self.active_coords[:, 1] < 4)]
			self.active_coords = cleaned_coords.copy()
		try:
			self.shape_grid = self.make_shape_grid(self.active_coords)
		except Exception as exs:
			print(f"error raised, final coords:\n{self.active_coords}")
			self.log_parameters(frame_no=self.frame_count,
								number_of_ones=self.ones_count,
								prev_number_of_ones=self.prev_ones_count,
								current_frame=self.board_state,
								significant_frame=self.significant_frame,
								frame_difference=self.significant_frame + self.board_state,
								active_coords=self.active_coords,
								past_frames=self.frame_history)
			for array in self.frame_history:
				if array is not None:
					print(np.array2string(array))
			raise exs
		self.tet_shape_key, self.rotation_id = self.trg_handler.determine_tetromino(self.shape_grid)
		self.minimised_shape_dict = self.trg_handler.get_minimised_array(self.tet_shape_key)

	def step_three_simulations(self, by_score: bool = False):
		"""
		Third step of the tetrobot flow:
		-> call the new_sim_moves method from the move_simulator instance
		-> it takes the significant frame (which is supposed to always be a clean reference frame) and ..
		.. it takes the minimised_shape_dict which is a dictionary which contains numpy arrays representing ..
		.. the geometric representation of the tetromino with the smallest np.ndarray.size attribute ..
		.. each key in the dictionary is an integer from 1 - 4 depending on how many different rotation states ..
		.. that particular tetromino has

		-> it calculates all possible moves and stores its 'score' and other attributes in an instance of ..
		..the stored_move class

		-> call the find_best_move method which picks the best move from the list of stored_moves and sets the ..
		.. move_simulator instance attribute .best_move as the stored object with the best score / evaluation
		-> we then set our Tetrobot instance attribute of .best_move_obj equal to the move_sim best move
		> note this means that self.best_move_obj is actually an instance of stored_move from the move_simulator module
		"""
		self.move_simulator.new_sim_moves(self.significant_frame, self.minimised_shape_dict)
		if not by_score:
			self.move_simulator.find_best_move()
			self.best_move_obj = self.move_simulator.best_move
		else:
			self.best_move_obj = self.move_simulator.evaluate_moves_by_score()

	def step_four_calc_moves(self):
		"""
		Fourth step of the tetrobot flow:
		-> set self.required_rotate to the difference between the required rotation_id and the current rotation_id
		-> the number given is equal to the amount of rotations required, a positive integer indicates clock-wise..
		.. rotation and vice versa
		-> set self.move_score to the output of the calculate_x_translation method which calculates the difference..
		.. between the required min_x coordinate and the current min_x coordinate, additionally taking into account..
		.. the offset due to rotation
		"""
		self.required_rotate = self.best_move_obj.rotation_id - self.rotation_id
		self.move_score = self.calculate_x_translation()

	def step_five_execute_moves(self):
		"""
		Fifth step of the tetrobot flow:
		-> creates a thead for automation of rotations
		-> creates a thread for automation of translations
		-> start and join both threads
		"""
		rotations = threading.Thread(target=self.automate_rotations)
		translations = threading.Thread(target=self.automate_left_right)
		rotations.start()
		translations.start()
		rotations.join(timeout=0.5)
		translations.join(timeout=0.5)


	def main_bot_loop(self):
		self.clock.reset()
		while self.running:
			self.clock.tick()
			if self.clock:
				self.clock.reset()
				if self.step_one_scn_shotting() or self.stage_2_error:
					self.stage_2_error = False
					self.stage = 1
					self.step_two_shape_attributes()
					if self.minimised_shape_dict is None:
						print("couldn't find our shape so will have to try again sometime")
						continue
					self.step_three_simulations(by_score=True)
					self.step_four_calc_moves()
					self.step_five_execute_moves()
					time.sleep(0.04)
					# self.press_space()
					if self.step_one_scn_shotting():
						self.stage_2_error = True
						print("stage 2 error occured")
						continue
					self.step_two_shape_attributes()
					if self.minimised_shape_dict is None:
						print("couldn't find our shape so will have to try again sometime")
						continue
					self.step_four_calc_moves()
					if self.required_rotate == 0 and self.move_score == 0:
						pass
					else:
						self.step_five_execute_moves()
						print("extra moves executed")
						time.sleep(0.04)
					self.press_space()

					# self.stage = 2
					self.log_parameters(frame_no=self.frame_count,
										number_of_ones=self.ones_count,
										prev_number_of_ones=self.prev_ones_count,
										current_frame=self.board_state,
										significant_frame=self.significant_frame,
										frame_difference=self.significant_frame + self.board_state,
										active_coords=self.active_coords,
										shape_grid=self.shape_grid,
										shape_key=self.tet_shape_key,
										rotation_id=self.rotation_id,
										shape_dict=self.minimised_shape_dict,
										simulated_move=self.best_move_obj.final_move_grid,
										required_rotation=self.required_rotate,
										required_moves=self.move_score)


				# if self.stage == 2:
					#### follows on from stage 1, unless a new piece is detected
					#### for checking the position of the piece before hitting space
					#### will execute more moves if necessary
					# self.stage_2_error = self.step_one_scn_shotting()
					# if self.stage_2_error: continue

					### if we reach this line no error was present
					### screenshot has been updated but we haven't updated the position of the tetromino yet
					### running step two again, should update our attribute self.active_coords
					### it will also re-acquire our various shape data from the TRG class methods
					### I can later refactor to isolate just the singel required function, but performance impact..
					### .. is relatively low as its only looking up keys in dictionaries and numpy array operations
					# self.step_two_shape_attributes()
					# self.step_four_calc_moves()
					# if self.required_rotate == 0 and self.move_score == 0:
					# 	time.sleep(0.05)
					# 	self.press_space()
					# else:
					# 	self.step_five_execute_moves()
					# 	time.sleep(0.05)
					# 	self.press_space()
					# self.stage = 1







	def log_parameters(self, **kwargs):
		if kwargs is None: return
		for arg_id, arg_data in kwargs.items():
			if isinstance(arg_data, np.ndarray):
				self.update_report_str(f"{arg_id}\n{np.array2string(arg_data)}")
			elif isinstance(arg_data, dict):
				for key, val in arg_data.items():
					self.update_report_str(f"{key}\n{(val)}")
			else:
				self.update_report_str(f"{arg_id}\n{arg_data}")

	def end_bot_loop(self):
		kb.wait("q")
		self.running = False
		self.queue.stop_queue()
		print("bot stopped")
		if self.debug_mode: self.write_to_gamelog(self.report_str)







####################
### Script start ###
####################

game_bot = tetris_thread_bot(monitor=2, scn_width=820, scn_height=1000, fps=60, action_timer_delay=0.02)
game_bot.set_ref_path()
game_bot.define_screen_region()
game_bot.set_grid_dims(x_rel_offset=-195, y_rel_offset=33, grid_px_width=234, grid_px_height=495)
game_bot.debug_mode = True
if game_bot.debug_mode:
	game_bot.set_game_log_path()


while True:
	# wait for next event.
	event = kb.read_event()
	if event.event_type == kb.KEY_DOWN and event.name == "p":
		game_bot.present_scn = game_bot.convert_sct_to_array()
		print(game_bot.present_scn)
		game_bot.find_ref(game_bot.ref_png_path, game_bot.present_scn, search_resolution=2)
		game_bot.generate_px_grid()
		game_bot.generate_board_px_means()
		game_bot.determine_bg_col()

	if event.event_type == kb.KEY_DOWN and event.name == "o":
		print("game bot start")
		game_bot.reset_game()
		game_bot.frame_count = 0
		game_bot.running = True
		main_thread = threading.Thread(target=game_bot.main_bot_loop)
		quit_thread = threading.Thread(target=game_bot.end_bot_loop)
		main_thread.start()
		quit_thread.start()
		quit_thread.join()
		main_thread.join()


	if event.event_type == kb.KEY_DOWN and event.name == "q":
		print("program terminated")
		break