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
		self.timer = tc.timer(self.tick_time)
		self.queue_batches = []

	def __len__(self):
		return len(self.queue) if self.action is None else len(self.queue) +1

	def __bool__(self):
		return len(self) > 0

	def start_move_queue(self):
		self.running = True
		self.timer.reset()
		while self.running:
			self.timer.tick()
			if self.timer:
				if len(self.queue_batches) > 0:
					print(self.queue_batches)
					batch = self.queue_batches.pop(0)
					self.queue.extend(batch)
				self.timer.reset()
				print("#"*10)
				print([str(obj) for obj in self.queue])
				if len(self.queue) > 0:
					self.action = self.queue.pop(0)
					print(self.action)
					self.action.q_method()
					print(self.action)
					self.action = None
					print(self.action)

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

	def queue_rotations(self, rotation_score:int):
			while rotation_score > 0:
				print(rotation_score)
				self.q_rotright()
				rotation_score -= 1
			while rotation_score < 0:
				print(rotation_score)
				self.q_rotleft()
				rotation_score += 1

	def queue_translations(self, move_score:int):
		while move_score > 0:
			self.q_right()
			move_score -= 1
		while move_score < 0:
			self.q_left()
			move_score += 1

	def queue_stuff(self, how_many:int, action:callable, name:str):
		self.queue_batches.append([action_packet(action, name) for _ in range(how_many)])



class action_packet:
	def __init__(self, action, name):
		self.q_method = action
		self.name = name
	def __str__(self):
		return self.name

if __name__=="__main__":
	move_q_system = queue_system(0.05)
	rot_q_system = queue_system(0.05)
	print("move to notepad for test")
	time.sleep(3)
	queue_thread = threading.Thread(target=move_q_system.start_move_queue)
	queue_thread_two = threading.Thread(target=rot_q_system.start_move_queue)
	queue_thread.start()
	queue_thread_two.start()


	time.sleep(0.2)

	rot_q_system.queue_stuff(10, rot_q_system._press_z, "press z")
	move_q_system.queue_stuff(10, move_q_system._press_space, "press space")
	move_q_system.queue_stuff(10, move_q_system._press_c, "press c")



	time.sleep(3)


	move_q_system.stop_queue()
	rot_q_system.stop_queue()
	queue_thread.join()
	queue_thread_two.join()




