import keyboard as kb
import Timer_class as tc
import time
import threading

class queue_system:
	def __init__(self, tick_time):
		self.queue = []
		self.r_queue = []
		self.tick_time = tick_time
		self.running = False
		self.action = None
		self.r_action = None

	def __len__(self):
		return len(self.queue) + len(self.r_queue)

	def __bool__(self):
		return len(self) > 0

	def start_move_queue(self):
		self.running = True
		q_timer = tc.timer(self.tick_time)
		while self.running:
			q_timer.tick()
			if not q_timer:
				continue
			q_timer.reset()
			if len(self.queue) == 0:
				continue
			self.action = self.queue.pop(0)
			self.action.q_method()
			self.action = None

	def start_rot_queue(self):
		self.running = True
		q_timer = tc.timer(self.tick_time)
		while self.running:
			q_timer.tick()
			if not q_timer:
				continue
			q_timer.reset()
			if len(self.r_queue) == 0:
				continue
			self.r_action = self.r_queue.pop(0)
			self.r_action.q_method()
			self.r_action = None

	def stop_queues(self):
		self.running = False

	def clear_queues(self):
		self.queue.clear()
		self.r_queue.clear()

	def report_queues(self) -> list:
		report_list = []
		report_list.extend(self.queue)
		report_list.extend(self.r_queue)
		if self.action is not None:
			report_list.append(self.action)
		return report_list

	def q_left(self):
		self.queue.append(action_packet(self._press_left, "left"))

	def q_right(self):
		self.queue.append(action_packet(self._press_right, "right"))

	def q_rotleft(self):
		self.r_queue.append(action_packet(self._press_z, "rotleft"))

	def q_rotright(self):
		self.r_queue.append(action_packet(self._press_up, "rotright"))

	def q_space(self):
		self.queue.append(action_packet(self._press_space, "space"))

	def q_c(self):
		self.queue.append(action_packet(self._press_c, "c"))

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

class action_packet:
	def __init__(self, action, name):
		self.q_method = action
		self.name = name
	def __str__(self):
		return self.name

if __name__=="__main__":
	q_system = queue_system(0.02)
	print("move to notepad for test")
	time.sleep(3)
	queue_thread = threading.Thread(target=q_system.start_move_queue)
	queue_thread_two = threading.Thread(target=q_system.start_rot_queue)
	queue_thread.start()
	queue_thread_two.start()
	for n in range(10):
		time.sleep(1)
		for _ in range(3):
			q_system.q_c()
			q_system.q_rotleft()
		q_system.q_space()

	q_system.stop_queues()
	queue_thread.join()
	queue_thread_two.join()



