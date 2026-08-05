import Tetris_bot_OOP as tb
import keyboard as kb
import pprint as pp
import numpy as np
import Timer_class
import threading
import time

# self.present_scn = self.convert_sct_to_array()
# self.find_ref(ref_png_path, self.present_scn, search_resolution=2)
# self.generate_px_grid()
# self.generate_board_px_means()
# self.determine_bg_col()
# self.determine_board_state()
# self.setup_done = True

class frame_master:
	def __init__(self):
		self.frame = None
		self.prev_frame = None
		self.significant_frame = None
		self.prev_sig_frame = None
		self.key_frame = None
		self.prev_key_frame = None

	def new_frame(self, frame):
		self.prev_frame = self.frame
		self.frame = frame

	def new_significant_frame(self, frame):
		self.prev_sig_frame = self.significant_frame
		self.significant_frame = frame

	def new_key_frame(self, frame):
		self.prev_key_frame = self.key_frame
		self.key_frame = frame




class tetris_thread_bot(tb.TetrisGame):
	def __init__(self,  monitor: int =0, scn_width: int=300, scn_height: int=300, mss_instance=None, fps: int = 8, action_timer_delay: float = 0.04):
		super().__init__(monitor, scn_width, scn_height, mss_instance, fps, action_timer_delay)
		self.fm = frame_master()

	def update_screen_shot(self):
		self.present_scn = self.optimised_scn_grab()
		self.generate_board_px_means()
		bg_mean_rgbs = np.full_like(self.mean_rgb_vals, self.bg_val)
		difference = np.abs(self.mean_rgb_vals - bg_mean_rgbs)
		self.fm.new_frame(((difference > 2).astype(np.uint8)).reshape((20,10)))

	def log_screen_shots(self):
		print("logging screen shots")
		timer = Timer_class.timer(self.time_per_frame)
		timer.reset()
		report_str = ""
		n = 0
		# self.update_screen_shot()
		while True:
			if timer:
				n+=1
				print("timer true")
				scn_shot_thread = threading.Thread(target=self.update_screen_shot())
				scn_shot_thread.start()
				scn_shot_thread.join()
				report_str = report_str +f"frame id: {n}, {timer.total_time} seconds\n"
				report_str = report_str +f"previous  frame:\n"
				if self.fm.prev_frame is not None:
					report_str = report_str +np.array2string(self.fm.prev_frame)
				else:
					report_str = report_str +"None"
				report_str = report_str +f"\ncurrent frame:\n"
				if self.fm.frame is not None:
					report_str = report_str +np.array2string(self.fm.frame)
				else:
					report_str = report_str +"None"
				report_str = report_str +f"\n\n"
				print("tick")
				timer.reset()
				print("timer reset")
			timer.tick()
			if not self.running:
				self.write_to_gamelog(report_str)
				break
			if timer.total_time > 10:
				self.write_to_gamelog(report_str)
				print("10 done")
				break

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


game_bot = tetris_thread_bot(monitor=2, scn_width=820, scn_height=1000, fps=1, action_timer_delay=0.02)
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
		game_bot.running = True
		# game_bot.screenshot_thread = threading.Thread(target=game_bot.log_screen_shots)
		quit_thread = threading.Thread(target=game_bot.check_quit)
		quit_thread.start()
		# game_bot.screenshot_thread.start()

		first_time = time.perf_counter()
		game_bot.log_screen_shots()
		end_time = time.perf_counter() - first_time
		print(f"actual overall time: {end_time}")
		quit_thread.join()
		# game_bot.screenshot_thread.join()

	if event.event_type == kb.KEY_DOWN and event.name == "q":
		if hasattr(game_bot, "running"):
			game_bot.running = False
		print("q pressed")
		break