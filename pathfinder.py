import Timer_class
import numpy as np
import action_queue as aq

# NOTES
# needs the current indexes, rotation id and board
# also needs the target indexes, rotation id and board, these are nicely packaged in our stored_move class obj.
# needs methods to read the queue.
# methods to add to queue.
# methods to clear queue.
# methods to calculate required translation and rotation
# threadable method to run the system.
#######################################

class Pathfinder:
	def __init__(self, master, action_frequency):
		self.master = master
		self.queue_master = aq.queue_system(action_frequency)
		self.path_signal = False
		self.curr_idxs = None
		self.curr_rot_id = None
		self.curr_board = None
		self.target_move = None

	def send_data_to_pathfinder(self, curr_idxs = None, curr_rot_id = None, curr_board = None, target_move = None):
		if curr_idxs is not None:
			self.curr_idxs = curr_idxs
		if curr_rot_id is not None:
			self.curr_rot_id = curr_rot_id
		if curr_board is not None:
			self.curr_board = curr_board
		if target_move is not None:
			self.target_move = target_move

	def find_path(self):
		while self.master.running:
			if self.path_signal:
				self.path_signal = False
				# do calculation logic for move automations
				# also check the queue

	def calc_req_moves(self):
		current_col = np.min(self.curr_idxs[:, 1])
		current_row = np.min(self.curr_idxs[:, 0])

		target_move = self.target_move
		target_col = np.min(target_move.min_x)
		target_row = np.min(target_move.min_y)

		translation_req = target_col - current_col
		current_q_items = [str(packet) for packet in self.queue_master.report_queues()]
		sorted_q_items = {}
		sorted_q_items = dict.fromkeys(current_q_items)
		for key in sorted_q_items.keys():
			sorted_q_items[key] = current_q_items.count(key)


