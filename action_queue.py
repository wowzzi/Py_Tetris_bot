import keyboard as kb
import Timer_class as tc

class queue_system:
	def __init__(self, tick_time):
		self.queue = []
		self.r_queue = []
		self.tick_time = tick_time
		self.running = False

	def _start_queue(self, target_queue):
		self.running = True
		q_timer = tc.Timer(self.tick_time)
		while self.running:
			q_timer.tick()
			if not q_timer:
				continue
			q_timer.reset()
			if len(target_queue) == 0:
				continue
			action = target_queue.pop(0)
			action()

	def start_move_queue(self):
		self._start_queue(self.queue)

	def start_rot_queue(self):
		self._start_queue(self.r_queue)

	def stop_queues(self):
		self.running = False

	def clear_queues(self):
		self.queue.clear()
		self.r_queue.clear()

	def q_left(self):
		self.queue.append(self._press_left)

	def q_right(self):
		self.queue.append(self._press_right)

	def q_rotleft(self):
		self.r_queue.append(self._press_z)

	def q_rotright(self):
		self.r_queue.append(self._press_up)

	def q_space(self):
		self.queue.append(self._press_space)

	def q_c(self):
		self.queue.append(self._press_c)

	def _press_space(self):
		# drop
		kb.send(57)

	def _press_left(self):
		# move left
		kb.send(75)

	def _press_right(self):
		# move right
		kb.send(77)

	def _press_z(self):
		# rotate left
		kb.send("z")

	def _press_up(self):
		# rotate right
		kb.send(72)

	def _press_c(self):
		# hold
		kb.send("c")
