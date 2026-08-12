import Tetris_bot_OOP as tb
import keyboard as kb
import pprint as pp
import numpy as np
import Timer_class
import threading
import time
import Thread_bot_move_sim as MS

# self.present_scn = self.convert_sct_to_array()
# self.find_ref(ref_png_path, self.present_scn, search_resolution=2)
# self.generate_px_grid()
# self.generate_board_px_means()
# self.determine_bg_col()
# self.determine_board_state()
# self.setup_done = True

class frame_master:
	def __init__(self):
		empty_arr = np.zeros((20,10), dtype=np.uint8)
		self.n_ones = 0
		self.prev_n_ones = 0
		self.frame = empty_arr
		self.prev_frame = empty_arr
		self.minor_frame = empty_arr
		self.prev_minor_frame = empty_arr
		self.significant_frame = empty_arr
		self.prev_sig_frame = empty_arr
		self.key_frame = empty_arr
		self.prev_key_frame = empty_arr
		self.frame_num = 0

	def new_frame(self, frame):
		self.prev_frame = self.frame
		self.frame = frame

		self.prev_n_ones = self.n_ones
		self.n_ones = len(self.frame[self.frame == 1])

		self.frame_num +=1

	def new_minor_frame(self, frame):
		self.prev_minor_frame = self.minor_frame
		self.minor_frame = frame

	def new_significant_frame(self, frame):
		self.prev_sig_frame = self.significant_frame
		self.significant_frame = frame

	def new_key_frame(self, frame):
		self.prev_key_frame = self.key_frame
		self.key_frame = frame

	def calc_frame_delta(self):
		delta_frame = np.abs(self.frame + self.prev_frame)
		number_of_ones = len(delta_frame[delta_frame == 1])

		if number_of_ones > 0:
			self.new_minor_frame(self.frame)
			return True
		return False

	def get_argones(self, input_binary: np.ndarray) -> np.ndarray:
		return np.stack((np.where(input_binary !=1, 0, 1)).nonzero(), axis=-1)

	def find_shape_indexes(self, frame_one: np.ndarray, reference_frame:np.ndarray) -> np.ndarray:
		summed_arr = np.add(frame_one, reference_frame, dtype=np.uint8)
		return self.get_argones(summed_arr)

	def process_frame_significance(self):
		delta_n = self.n_ones - self.prev_n_ones
		# key frame logic
		if delta_n > 0:
			# log the key frame
			self.new_key_frame(self.frame)
			# calculate the difference to the previous frame and find the different indexes
			new_piece_indexes = self.find_shape_indexes(self.key_frame, self.prev_frame)
			# if it finds 4, then its legit
			shape_array = None
			if len(new_piece_indexes) == 4:
				normalised_new_piece_coords = self.normalise_array_coords(new_piece_indexes)
				shape_array = self.slice_in_shape_grid(normalised_new_piece_coords)
			# significant frame is the frame directly previous to the key frame, it acts as a good frame of reference.
			self.new_significant_frame(self.prev_frame)

			return {
				'significant': True,
				'new_indexes': new_piece_indexes,
				'shape array': shape_array
			}

		elif self.calc_frame_delta():
			return {
				'significant': False
			}
		return None

	def normalise_array_coords(self, input_array_of_coords: np.ndarray) -> np.ndarray:
		"""
		parameter: input_array_of_coords
		intended to be an np.ndarray of shape (x, 2) where x is typically 4.
		"""
		row_min_coord = (input_array_of_coords[:,0]).min()
		col_min_coord = (input_array_of_coords[:,1]).min()

		return input_array_of_coords - np.array([row_min_coord, col_min_coord])

	def slice_in_shape_grid(self, input_coord_array: np.ndarray) -> np.ndarray:
		blank_array = np.zeros((4,4), dtype=np.uint8)
		blank_array[input_coord_array[:,0], input_coord_array[:,1]] = 1
		return blank_array






class tetris_thread_bot(tb.TetrisGame):
	def __init__(self,  monitor: int =0, scn_width: int=300, scn_height: int=300, mss_instance=None, fps: int = 8, action_timer_delay: float = 0.04):
		super().__init__(monitor, scn_width, scn_height, mss_instance, fps, action_timer_delay)
		self.fm = frame_master()
		self.move_simulator = MS.tb_move_sim()
		self.hold_move_sim = MS.tb_move_sim()

	def update_screen_shot(self):
		self.present_scn = self.optimised_scn_grab()
		self.generate_minimised_px_means()
		difference = np.abs(self.mean_rgb_vals - self.bg_val)
		self.fm.new_frame(((difference > 2).astype(np.uint8)).reshape((20,10)))

	def log_screen_shots(self):
		print("logging screen shots")
		timer = Timer_class.timer(self.time_per_frame)
		timer.reset()
		report_str = ""
		n = 0

		while True:
			if timer:
				timer.reset()
				n+=1
				self.update_screen_shot()
				response = self.fm.process_frame_significance()
				if response is not None:
					current_frame = self.fm.frame
					if len(response) > 1:
						# significant
						self.shape_coords = response.get("new_indexes")
						new_shape = response.get("shape array")
						self.get_tetromino(new_shape)
						if self.tet_shape_key is None:
							error_code = self.handle_no_shape_error()
							if error_code == 1:
								print("break loop")
								break
							elif error_code == 0:
								continue
						if self.debug_mode:
							report_str = report_str + f"\ncurrent tetro:\n{self.minimised_shape_dict.get(self.rotation_id)}"

						self.move_simulator.new_sim_moves(self.fm.significant_frame, self.minimised_shape_dict)
						self.move_simulator.find_best_move()
						self.best_move_obj = self.move_simulator.best_move
						self.automate_moves_thread()
						self.stage_five_hit_space(delay_seconds=0.02)

					else:
						# just check pos
						reference_frame = self.fm.significant_frame
						current_indexes = self.fm.find_shape_indexes(current_frame, reference_frame)
						if self.debug_mode:
							report_str = report_str + f"\ncurrent_pos: \n{current_indexes}"

					if self.debug_mode:
						report_str = report_str + f"\n current board state:\n{current_frame}"

				# print("tick")

			timer.tick()
			if not self.running:
				if self.debug_mode:
					self.write_to_gamelog(report_str)
				break
			# if timer.total_time > 10:
			# 	self.write_to_gamelog(report_str)
			# 	print("10 done")
			# 	break

	def check_quit(self):
		while True:
			event = kb.read_event()
			if event.event_type == kb.KEY_DOWN and event.name == "q":
				self.running = False
				print("loop end")
				break

	def auto_thread_scn_shots(self):
		timer = Timer_class.timer(self.time_per_frame)
		timer.reset()
		while True:
			if timer:
				self.update_screen_shot()
			timer.tick()
			if not self.running:
				break

	def scn_shot_analysis_thread(self):
		pass

	def get_tetromino(self, input_shape:np.ndarray):
		self.tet_shape_key, self.rotation_id = self.trg_handler.determine_tetromino(input_shape)
		if self.tet_shape_key is not None:
			self.minimised_shape_dict = self.trg_handler.get_minimised_array(self.tet_shape_key)

	def automate_moves_thread(self):
		self.required_rotate = game_bot.calc_rotation_needed(self.rotation_id, self.best_move_obj.rotation_id)
		self.rotation_automate(self.required_rotate)
		self.new_calc_x_translation(
			self.required_rotate,
			self.shape_coords,
			self.best_move_obj.min_x,
			self.tet_shape_key
		)

	def new_calc_x_translation(self, rotation_score, current_shape_coords, target_column, piece_id):
		current_min_x = min([coord[1] for coord in current_shape_coords])
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

	def handle_no_shape_error(self):
		if self.tet_shape_key is None:
			print("no tet shape key")
			self.add_error()
			if self.error_count > 40:
				return 1
			else:
				return 0
		else:
			self.reset_error_count()
		return None




game_bot = tetris_thread_bot(monitor=2, scn_width=820, scn_height=1000, fps=60, action_timer_delay=0.02)
game_bot.set_ref_path()
game_bot.define_screen_region()
game_bot.set_grid_dims(x_rel_offset=-195, y_rel_offset=33, grid_px_width=234, grid_px_height=495)
game_bot.debug_mode = False
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
		print("o pressed")
		game_bot.running = True

		game_bot.screenshot_thread = threading.Thread(target=game_bot.log_screen_shots)
		quit_thread = threading.Thread(target=game_bot.check_quit)
		quit_thread.start()
		first_time = time.perf_counter()
		game_bot.screenshot_thread.start()

		game_bot.screenshot_thread.join()
		end_time = time.perf_counter() - first_time
		print(f"actual overall time: {end_time}")
		quit_thread.join()

	if event.event_type == kb.KEY_DOWN and event.name == "q":
		if hasattr(game_bot, "running"):
			game_bot.running = False
		print("q pressed")
		break