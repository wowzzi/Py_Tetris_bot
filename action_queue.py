import keyboard as kb
import Timer_class as tc
import time
import threading

class queue_system:
	def __init__(self, tick_time):
		self.queue = []
		self.tick_time = tick_time
		self.running = False
		self.action = None

	def __len__(self):
		return len(self.queue) if self.action is None else len(self.queue) +1

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
			print(f"processed order: {self.action}")
			self.action = None

	def stop_queue(self):
		self.running = False

	def clear_queue(self):
		self.queue.clear()
		print("queue cleared")

	def report_q(self) -> list:
		report_list = [str(packet) for packet in self.queue]
		if self.action is not None:
			report_list.append(str(self.action))
		return report_list

	def q_left(self):
		self.queue.append(action_packet(self._press_left, "left"))

	def q_right(self):
		self.queue.append(action_packet(self._press_right, "right"))

	def q_rotleft(self):
		self.queue.append(action_packet(self._press_z, "rotleft"))

	def q_rotright(self):
		self.queue.append(action_packet(self._press_up, "rotright"))

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
	move_q_system = queue_system(0.02)
	rot_q_system = queue_system(0.02)
	print("move to notepad for test")
	time.sleep(3)
	queue_thread = threading.Thread(target=move_q_system.start_move_queue)
	queue_thread_two = threading.Thread(target=rot_q_system.start_move_queue)
	queue_thread.start()
	queue_thread_two.start()
	for n in range(10):
		time.sleep(1)
		for _ in range(3):
			move_q_system.q_c()
			rot_q_system.q_rotleft()
		move_q_system.q_space()

	move_q_system.stop_queue()
	rot_q_system.stop_queue()
	queue_thread.join()
	queue_thread_two.join()



