import Tetris_bot_OOP as tb
import keyboard as kb
import pprint as pp
import numpy as np
import Timer_class
import threading
import time
import Thread_bot_move_sim as MS


class frame_master:
	def __init__(self):
		empty_arr = np.zeros((20,10), dtype=np.uint8)
		# number of active squares
		self.n_ones = 0
		self.prev_n_ones = 0
		# standard frame
		self.frame = empty_arr
		self.prev_frame = empty_arr
		# captures the frame directly before the key frame
		self.significant_frame = empty_arr
		self.prev_sig_frame = empty_arr
		# captures the key frame where n increases
		self.key_frame = empty_arr
		self.prev_key_frame = empty_arr
		self.frame_num = 0

	def new_frame(self, frame):
		self.prev_frame = self.frame
		self.frame = frame

		self.prev_n_ones = self.n_ones
		self.n_ones = len(self.frame[self.frame == 1])
		self.delta_n_ones = self.n_ones - self.prev_n_ones

		self.frame_num +=1

	def new_significant_frame(self, frame):
		self.prev_sig_frame = self.significant_frame
		self.significant_frame = frame

	def new_key_frame(self, frame):
		self.prev_key_frame = self.key_frame
		self.key_frame = frame

	def do_frames_differ(self) -> bool:
		delta_frame = self.frame + self.prev_frame
		return bool(len(delta_frame[delta_frame == 1]))

	def get_argones(self, input_binary: np.ndarray) -> np.ndarray:
		return np.stack((np.where(input_binary !=1, 0, 1)).nonzero(), axis=-1)

	def find_shape_indexes(self, frame_one: np.ndarray, reference_frame:np.ndarray) -> np.ndarray:
		summed_arr = np.add(frame_one, reference_frame, dtype=np.uint8)
		return self.get_argones(summed_arr)

	def normalise_array_coords(self, input_coords: np.ndarray) -> np.ndarray:
		"""
		parameter: input_coords
		intended to be an np.ndarray of shape (x, 2) where x is typically 4.
		"""
		row_min_coord = (input_coords[:,0]).min()
		col_min_coord = (input_coords[:,1]).min()

		return input_coords - np.array([row_min_coord, col_min_coord])

	def slice_in_shape_grid(self, input_coord_array: np.ndarray) -> np.ndarray:
		blank_array = np.zeros((4,4), dtype=np.uint8)
		blank_array[input_coord_array[:,0], input_coord_array[:,1]] = 1
		return blank_array


##################################
### Tetris bot inherited class ###
##################################
class tetris_thread_bot(tb.TetrisGame):
	def __init__(self,  monitor: int =0, scn_width: int=300, scn_height: int=300, mss_instance=None, fps: int = 8, action_timer_delay: float = 0.04):
		super().__init__(monitor, scn_width, scn_height, mss_instance, fps, action_timer_delay)
		self.fm = frame_master()
		self.move_simulator = MS.tb_move_sim()
		self.hold_move_sim = MS.tb_move_sim()
		self.hold_used = False
		self.move_count =0
		self.running = False
		self.sim_signal = False

	def run_bot(self):
		print("logging screen shots")
		start_time = time.perf_counter()
		timer = Timer_class.timer(self.time_per_frame)
		timer.reset()
		self.move_count = 0
		self.report_str = ""

		while self.running:
			timer.tick()
			if timer:
				timer.reset()
				self.step_one()

			self.periodic_logging()
			if self.error_count > 40:
				print("self.error_count > 40")
				self.running = False
		print("stopped running")
		if self.debug_mode:
			self.write_to_gamelog(self.report_str)

	def step_one(self):
		self.update_screen_shot() # generates a new frame in fm
		# new frame automatically calculates new active sq count
		delta_squares = self.fm.delta_n_ones
		if delta_squares > 0:
			self.move_count += 1
			self.fm.new_significant_frame(self.fm.prev_frame)
			self.fm.new_key_frame(self.fm.frame)
			if not self.update_shape_info(self.fm.key_frame, self.fm.significant_frame):
				self.error_count += 1
				print("error from the delta n >0 bit")
				print(f"error count: {self.error_count}")
				return
			self.reset_error_count()
			# acess variables: self.shape_coords: np.ndarray (e.g. array([[0, 0], [0, 1], [1, 0], [1, 1]])
			# self.tet_shape_key: str (e.g. bw l, t, etc)
			# self.rotation_id: int (e.g. 1,2,3,4)
			# self.minimised_shape_dict: dict (e.g. 'sq': {1: np.array([[1,1],[1,1]])} we get the value from sq)
			self.update_report_str("#"*20)
			self.update_report_str(f"key frame detected on move count {self.move_count}:")
			self.update_report_str(f"{np.array2string(self.fm.key_frame)}")
			self.update_report_str(f"significant frame detected:")
			self.update_report_str(f"{np.array2string(self.fm.significant_frame)}")
			self.update_report_str(f"delta n = {delta_squares}\nnew positions detected, self.shape_coords:\n{np.array2string(self.shape_coords)}")
			self.update_report_str(f"current shape: {self.tet_shape_key}")
			self.update_report_str(f"current rotation id: {self.rotation_id}")
			self.update_report_str(f"current shape data:\n{self.minimised_shape_dict}\n")
			self.sim_signal = True
		elif delta_squares < 0:
			self.update_report_str(f"delta n = {delta_squares} which is < 0, still on move count: {self.move_count}")
		else:
			if self.fm.do_frames_differ():
				if not self.update_shape_info(self.fm.frame, self.fm.significant_frame):
					self.error_count += 1
					print("errored from the delta n is equal bit")
					print(f"error count: {self.error_count}")
					return
				self.reset_error_count()
				self.update_report_str(f"delta n = {delta_squares}, still on move count: {self.move_count}\nnew positions detected, self.shape_coords:\n{np.array2string(self.shape_coords)}")
				self.update_report_str(f"current shape: {self.tet_shape_key}")
				self.update_report_str(f"current rotation id: {self.rotation_id}")
				self.update_report_str(f"current shape data:\n{self.minimised_shape_dict}\n")
				# acess variables: self.tet_shape_key: str (e.g. bw l, t, etc)
				# self.rotation_id: int (e.g. 1,2,3,4)
				# self.minimised_shape_dict: dict (e.g. 'sq': {1: np.array([[1,1],[1,1]])} we get the value from sq)

	def update_screen_shot(self):
		self.present_scn = self.optimised_scn_grab()
		self.generate_minimised_px_means()
		difference = np.abs(self.mean_rgb_vals - self.bg_val)
		self.fm.new_frame(((difference > 2).astype(np.uint8)).reshape((20,10)))

	def update_shape_info(self, frame_one, frame_two):
		self.shape_coords = self.fm.find_shape_indexes(frame_one, frame_two)
		print(self.shape_coords)
		print(self.shape_coords.size)
		if len(self.shape_coords) != 4:
			return False
		_4x4_shape = self.fm.slice_in_shape_grid(self.fm.normalise_array_coords(self.shape_coords))
		self.get_tetromino(_4x4_shape)
		return True

	def get_tetromino(self, input_shape:np.ndarray):
		self.tet_shape_key, self.rotation_id = self.trg_handler.determine_tetromino(input_shape)
		if self.tet_shape_key is not None:
			self.minimised_shape_dict = self.trg_handler.get_minimised_array(self.tet_shape_key)

	def simulation_thread(self):
		while self.running:
			if self.sim_signal:
				self.sim_signal = False
				# do simulations now
				if self.minimised_shape_dict is None:
					return
				self.move_simulator.new_sim_moves(self.fm.significant_frame, self.minimised_shape_dict)
				self.move_simulator.find_best_move()
				self.best_move_obj = self.move_simulator.best_move
				self.update_report_str("Simulated: best move board")
				best_board = self.best_move_obj.final_move_grid.copy()
				print(self.best_move_obj.position_indexes)
				print(best_board.shape)
				best_board[self.best_move_obj.position_indexes[:,0], self.best_move_obj.position_indexes[:,1]] = 2
				self.update_report_str(np.array2string(best_board))

	def new_hold_routine(self):
		# temporarily extract the current shape data
		current_shape_dict = self.minimised_shape_dict.copy()
		current_shape_coords = self.shape_coords.copy()
		current_rotation_id = self.rotation_id
		current_shape_id = self.tet_shape_key

		# set the new shape data
		self.minimised_shape_dict = self.hold_piece.get("shape_data")
		self.shape_coords = self.hold_piece.get("obj_indexes")
		self.rotation_id = self.hold_piece.get("rotation_id")
		self.tet_shape_key = self.hold_piece.get("shape_key")

		# overwrite the old hold obj with that temp data
		# mutability shouldn't be an issue as im remaking the dict and thus not updating the same memory address
		self.hold_piece = {
			'shape_data': current_shape_dict,
			'obj_indexes': current_shape_coords,
			'rotation_id': current_rotation_id,
			'shape_key': current_shape_id
		}

	def periodic_logging(self):
		if self.move_count % 10 == 0 and self.report_str != "" and self.debug_mode:
			self.write_to_gamelog(self.report_str)
			self.reset_report_str()

	def check_quit(self):
		while True:
			event = kb.read_event()
			if event.event_type == kb.KEY_DOWN and event.name == "q" or not self.running:
				self.running = False
				if self.debug_mode and self.report_str != "":
					self.write_to_gamelog(self.report_str)
					self.reset_report_str()
				print("loop end")
				break

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
		print("o pressed")
		game_bot.reset_game()
		game_bot.running = True

		game_bot.screenshot_thread = threading.Thread(target=game_bot.run_bot)
		game_bot.sim_thread = threading.Thread(target=game_bot.simulation_thread)
		quit_thread = threading.Thread(target=game_bot.check_quit)
		quit_thread.start()
		game_bot.screenshot_thread.start()
		game_bot.sim_thread.start()
		first_time = time.perf_counter()

		game_bot.screenshot_thread.join()
		end_time = time.perf_counter() - first_time
		print(f"actual overall time: {end_time}")
		game_bot.sim_thread.join()
		quit_thread.join()

	if event.event_type == kb.KEY_DOWN and event.name == "q":
		if hasattr(game_bot, "running"):
			game_bot.running = False
		print("q pressed")
		break