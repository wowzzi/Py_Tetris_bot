import Tetris_bot_OOP as tb
import keyboard as kb
import pprint as pp
import numpy as np
import Timer_class
import threading
import time
import Thread_bot_move_sim as MS
import pathfinder as pf

class frame_master:
	def __init__(self, master):
		self.master = master
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

		# update_packet = None
		# if self.delta_n_ones > 0:
		# 	self.new_key_frame(self.frame)
		# 	self.new_significant_frame(self.prev_frame)
		# 	update_packet = "significant"
		# elif self.do_frames_differ():
		# 	self.find_shape_indexes(self.frame, self.significant_frame)
		# 	update_packet = "movement"


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
				'shape_array': shape_array
			}

		# elif self.do_frames_differ():
		# 	return {
		# 		'significant': False
		# 	}
		return None

	def run_processing(self):
		self.master.update_screen_shot()
		data = self.process_frame_significance()
		if data is not None:
			current_frame = self.frame

			# key - we have a dict
			self.master.shape_coords = data.get("new_indexes")
			new_shape = data.get("shape_array") # 4x4 normalised grid, use to get minimised grid.
			self.master.get_tetromino(new_shape)
			if self.master.tet_shape_key is None:
				error_code = self.master.handle_no_shape_error()
				return error_code
		return None



##################################
### Tetris bot inherited class ###
##################################
class tetris_thread_bot(tb.TetrisGame):
	def __init__(self,  monitor: int =0, scn_width: int=300, scn_height: int=300, mss_instance=None, fps: int = 8, action_timer_delay: float = 0.04):
		super().__init__(monitor, scn_width, scn_height, mss_instance, fps, action_timer_delay)
		self.fm = frame_master(self)
		self.move_simulator = MS.tb_move_sim()
		self.hold_move_sim = MS.tb_move_sim()
		self.hold_used = False
		self.move_count =0
		self.running = False
		self.sim_signal = False
		self.pathfinder = pf.Pathfinder(self, self.delay_time)
		self.move_queue = self.pathfinder.move_queue_master
		self.rot_queue = self.pathfinder.rot_queue_master

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
				error_code = self.fm.run_processing()
				if error_code is None:
					pass
				elif error_code == 1:
					break
				elif error_code == 0:
					continue

				# do the simulation stuff
				self.simulation_stuff()
			self.periodic_logging()

		print("stopped running")
		if self.debug_mode:
			self.write_to_gamelog(self.report_str)

	def simulation_stuff(self):
		self.move_simulator.new_sim_moves(self.fm.significant_frame, self.minimised_shape_dict)
		self.move_simulator.find_best_move()
		self.best_move_obj = self.move_simulator.best_move
		self.automate_moves_thread()
		self.stage_five_hit_space(delay_seconds=0.02)

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
			self.sim_signal = True
			self.pathfinder.send_data_to_pathfinder(
				curr_idxs=self.shape_coords,
				curr_rot_id=self.rotation_id,
				curr_board=self.fm.key_frame)
			self.pathfinder.path_signal = True

			# acess variables: self.shape_coords: np.ndarray (e.g. array([[0, 0], [0, 1], [1, 0], [1, 1]])
			# self.tet_shape_key: str (e.g. bw l, t, etc)
			# self.rotation_id: int (e.g. 1,2,3,4)
			# self.minimised_shape_dict: dict (e.g. 'sq': {1: np.array([[1,1],[1,1]])} we get the value from sq)
			if self.debug_mode:
				self.update_report_str("#"*20)
				self.update_report_str(f"key frame detected on move count {self.move_count}:")
				self.update_report_str(f"{np.array2string(self.fm.key_frame)}")
				self.update_report_str(f"significant frame detected:")
				self.update_report_str(f"{np.array2string(self.fm.significant_frame)}")
				self.update_report_str(f"delta n = {delta_squares}\nnew positions detected, self.shape_coords:\n{np.array2string(self.shape_coords)}")
				self.update_report_str(f"current shape: {self.tet_shape_key}")
				self.update_report_str(f"current rotation id: {self.rotation_id}")
				self.update_report_str(f"current shape data:\n{self.minimised_shape_dict}\n")

		elif delta_squares < 0:
			if self.debug_mode:
				self.update_report_str(f"delta n = {delta_squares} which is < 0, still on move count: {self.move_count}")
				self.update_report_str(f"significant frame:\n{np.array2string(self.fm.significant_frame)}")
				self.update_report_str(f"current frame:\n{np.array2string(self.fm.key_frame)}")
				self.update_report_str(f"current frame:\n{np.array2string(self.fm.frame)}")
		else:
			if self.fm.do_frames_differ():
				if not self.update_shape_info(self.fm.frame, self.fm.significant_frame):
					self.error_count += 1
					if self.debug_mode:
						self.update_report_str(f"error occured\nprev frame:\n{np.array2string(self.fm.prev_frame)}")
						self.update_report_str(f"current frame:\n{np.array2string(self.fm.frame)}")
					print("errored from the delta n is equal bit")
					print(f"error count: {self.error_count}")
					return
				self.reset_error_count()
				self.pathfinder.send_data_to_pathfinder(
					curr_idxs=self.shape_coords,
					curr_rot_id=self.rotation_id,
					curr_board=self.fm.frame)
				self.pathfinder.path_signal = True
				if self.debug_mode:
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
				self.pathfinder.send_data_to_pathfinder(target_move = self.best_move_obj)
				self.pathfinder.path_signal = True

				if self.debug_mode:
					self.update_report_str("Simulated: best move board")
					best_board = self.best_move_obj.final_move_grid.copy()
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

	def automate_moves_thread(self):
		self.required_rotate = self.rotation_id - self.best_move_obj.rotation_id
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
		# game_bot.sim_thread = threading.Thread(target=game_bot.simulation_thread)
		# game_bot.pf_thread = threading.Thread(target=game_bot.pathfinder.find_path)
		# game_bot.move_q_thread = threading.Thread(target=game_bot.move_queue.start_move_queue)
		# game_bot.rot_q_thread = threading.Thread(target=game_bot.rot_queue.start_move_queue)
		quit_thread = threading.Thread(target=game_bot.check_quit)
		quit_thread.start()
		first_time = time.perf_counter()
		game_bot.screenshot_thread.start()
		# game_bot.sim_thread.start()
		# game_bot.pf_thread.start()
		# game_bot.move_q_thread.start()
		# game_bot.rot_q_thread.start()


		game_bot.screenshot_thread.join()
		end_time = time.perf_counter() - first_time
		print(f"actual overall time: {end_time}")
		# game_bot.sim_thread.join()
		# game_bot.pf_thread.join()
		# game_bot.move_q_thread.join()
		# game_bot.rot_q_thread.join()
		quit_thread.join()

	if event.event_type == kb.KEY_DOWN and event.name == "q":
		if hasattr(game_bot, "running"):
			game_bot.running = False
		print("q pressed")
		break


# Exception in thread Thread-3 (run_bot):
# Traceback (most recent call last):
#   File "C:\Users\willd\AppData\Local\Programs\Python\Python310\lib\threading.py", line 1009, in _bootstrap_inner
#     self.run()
#   File "C:\Users\willd\AppData\Local\Programs\Python\Python310\lib\threading.py", line 946, in run
#     self._target(*self._args, **self._kwargs)
#   File "C:\Users\willd\PycharmProjects\Tetris_bot_git_repo\Py_Tetris_bot\Threaded_py_bot.py", line 166, in run_bot
#     self.simulation_stuff()
#   File "C:\Users\willd\PycharmProjects\Tetris_bot_git_repo\Py_Tetris_bot\Threaded_py_bot.py", line 177, in simulation_stuff
#     self.automate_moves_thread()
#   File "C:\Users\willd\PycharmProjects\Tetris_bot_git_repo\Py_Tetris_bot\Threaded_py_bot.py", line 338, in automate_moves_thread
#     self.required_rotate = game_bot.calc_rotation_needed(self.rotation_id, self.best_move_obj.rotation_id)
#   File "C:\Users\willd\PycharmProjects\Tetris_bot_git_repo\Py_Tetris_bot\Tetris_bot_OOP.py", line 506, in calc_rotation_needed
#     return rotation_id_final - rotation_id_current
# TypeError: unsupported operand type(s) for -: 'int' and 'NoneType'