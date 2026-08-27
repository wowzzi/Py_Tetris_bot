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
		self.move_queue_master = aq.queue_system(action_frequency)
		self.rot_queue_master = aq.queue_system(action_frequency)
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
		print("pathfinder data received")

	def find_path(self):
		while self.master.running:
			if self.path_signal:
				self.path_signal = False
				if self.curr_idxs is None or self.curr_rot_id is None or self.curr_board is None or self.target_move is None:
					# skip and wait for the next update and thus signal
					continue
				final_board = self.target_move.final_move_grid
				if len(self.curr_board[self.curr_board == 1]) != len(final_board[final_board==1]):
					continue
				else:
					delta_board = final_board - self.curr_board
					if len(delta_board[delta_board != 0]) == 0:
						continue
				satisfied_rot = self.calc_req_rot()
				satisfied_trans = self.calc_req_moves()
				if satisfied_rot and satisfied_trans:
					self.move_queue_master.q_space()
				# if any data is missing, then skip - done
				# if current board count 1's != target_move board count 1's skip - done
				# if current board is identical to target_move board, skip (dont risk queueing space) - done
				# send data to pathfinder, every movement frame, keyframe and simulation event - done
				# do calculation logic for move automations - method complete, just call them now
				# also check the queue - done as part of the move automations logic
				# check if the col is correct and row delta is > 1 if so, queue a space hit
		self.move_queue_master.stop_queue()
		self.rot_queue_master.stop_queue()

	def calc_req_moves(self):
		current_col = np.min(self.curr_idxs[:, 1])
		# current_row = np.min(self.curr_idxs[:, 0])

		target_move = self.target_move
		target_col = np.min(target_move.min_x)
		# target_row = np.min(target_move.min_y)

		translation_req = target_col - current_col
		queued_move_score = 0
		if self.move_queue_master:
			# true is non-empty queue (len ge 1)
			current_q_items = self.move_queue_master.report_q()
			sorted_q_items = {packet: current_q_items.count(packet) for packet in current_q_items}
			queued_move_score = sorted_q_items.get("right", 0) - sorted_q_items.get("left", 0)
			print(sorted_q_items)
			print(queued_move_score)

		if translation_req != queued_move_score:
			self.move_queue_master.clear_queue()
			print("should clear queue")
			if translation_req < 0:
				for _ in range(abs(translation_req)):
					self.move_queue_master.q_left()
					print("queue left")
			elif translation_req > 0:
				for _ in range(translation_req):
					self.move_queue_master.q_right()
					print("queue right")
			else:
				return True
		else:
			if translation_req == 0:
				return True
		return False

	def calc_req_rot(self):
		target_move = self.target_move
		target_rot = target_move.rotation_id
		rot_required = target_rot - self.curr_rot_id

		queued_rot_score = 0
		if self.rot_queue_master:
			# true is non-empty queue (len ge 1)
			current_q_items = self.rot_queue_master.report_q()
			sorted_q_items = {packet: current_q_items.count(packet) for packet in current_q_items}
			queued_rot_score = sorted_q_items.get("rotright", 0) - sorted_q_items.get("rotleft", 0)

		if rot_required != queued_rot_score:
			self.rot_queue_master.clear_queue()
			if rot_required < 0:
				for _ in range(abs(rot_required)):
					self.rot_queue_master.q_rotleft()
					print("queue rotate left")
			elif rot_required > 0:
				for _ in range(rot_required):
					self.rot_queue_master.q_rotright()
					print("queue rotate right")
			else:
				return True
		else:
			if rot_required == 0:
				return True
		return False
