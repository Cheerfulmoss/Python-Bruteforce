"""
Alexander Burow

License: GPL3
"""

from itertools import product
from string import ascii_letters, digits, punctuation
from hashlib import md5
from threading import Thread, active_count
from multiprocessing import Process
from time import perf_counter_ns, sleep
import threading
import multiprocessing


def close_threads():
	for thread in threading.enumerate():
		if thread.name != "MainThread":
			thread.join()


def listener(queue):
	if not queue.empty():
		pass_found, password, duration = queue.get()
		return pass_found, password, duration
	return False, "unknown", 0


# ----- REWRITE PROCESSOR HANDLER TO PASS OUT TASKS TO PROCESSES WHICH HAVE COMPLETED THEIR JOBS
class Bruteforce:
	def __init__(self, input_hash, min_len, max_len, threads, processes):
		self.DEBUG_TEXT = True
		self.PARTIAL_DEBUG = True

		self.hash_in = input_hash
		self.threads = threads
		self.processes = processes
		self.min_len = min_len
		self.max_len = max_len

		self.pass_found = False
		self.password = ""

		self.characters = ascii_letters + digits + punctuation

	def checker(self, combo_list, queue):
		start = perf_counter_ns()
		if self.pass_found:
			if __name__ == "__main__":
				print(
					f"password found by other thread, exiting  |  {combo_list[0]} - {combo_list[-1]}  |  {perf_counter_ns() - start} ns")
			return
		for combo in combo_list:
			if self.pass_found:
				if __name__ == "__main__":
					print(
						f"password found by other thread, exiting  |  {combo_list[0]} - {combo_list[-1]}  |  {perf_counter_ns() - start} ns")
				return
			elif md5(combo.encode()).hexdigest() == self.hash_in:
				self.pass_found = True
				self.password = combo
				if __name__ == "__main__":
					print(
						f"password  |  {self.password}  |  found in range  |  {combo_list[0]} - {combo_list[-1]}  |  {perf_counter_ns() - start} ns")
				queue.put((self.pass_found, self.password, perf_counter_ns() - start))
				return
		if __name__ == "__main__" and self.DEBUG_TEXT:
			print(
				f"Thread completed with no match  |  {combo_list[0]} - {combo_list[-1]}  |  {perf_counter_ns() - start} ns")

	def generator_process(self, queue, length):
		start = perf_counter_ns()
		# combos per sub list
		cpsl = 1_000_00
		sub_list = list()
		task_queue = list()
		for combination in product(self.characters, repeat=length):

			# ----- Checks to see if the password has been found ----- #
			if self.pass_found:
				close_threads()
				duration = perf_counter_ns() - start
				return duration
			# The queue is only populated when the password is found so actually grabbing the value is unnecessary
			# ( and also removes the item from the queue )
			elif not queue.empty() and not self.pass_found:
				return

			# ----- Generates the lists for the checker functions ----- #
			# sub list holds the character sequences (e.g. "aaaa", "aaab" ... "xxxx" )
			elif len(sub_list) < cpsl:
				sub_list.append("".join(combination))
			else:
				# ----- While the amount of active threads ( -1 due to main thread ) is less than total allowed threads ----- #
				while (active_count() - 1) < self.threads:
					# If the queue ( not the multiprocessing queue ) is empty then the thread is given what's in the queue
					if len(task_queue) > 0:
						thread = Thread(target=self.checker, args=(task_queue[0], queue))
						thread.start()
						del task_queue[0]
						sub_list = ["".join(combination)]
					# Else the thread is given the sub_list
					else:
						thread = Thread(target=self.checker, args=(sub_list, queue))
						thread.start()
						sub_list = ["".join(combination)]
						break
				else:
					# ----- if all threads are in use the list is appended to task_queue ----- #
					task_queue.append(sub_list)
					sub_list = ["".join(combination)]

		# ----- Once all combinations are complete any leftover combinations in sub_list are processed ----- #
		if len(sub_list) > 0:
			task_queue.append(sub_list)
		while len(task_queue) > 0:
			if self.pass_found:
				close_threads()
				duration = perf_counter_ns() - start
				return duration
			elif not queue.empty:
				return
			elif (active_count() - 1) < self.threads:
				thread = Thread(target=self.checker, args=(task_queue[0], queue))
				thread.start()
				del task_queue[0]

		close_threads()
		duration = perf_counter_ns() - start
		return duration

	def queue_thread(self):
		start = perf_counter_ns()
		queue = multiprocessing.Queue()
		# makes a list of all lengths to provide to the generator processes
		length_list = list(range(self.min_len, self.max_len + 1))
		while len(length_list) > 0 and queue.empty():
			if len(multiprocessing.active_children()) < self.processes:
				process = Process(target=self.generator_process, args=(queue, length_list[0]))
				process.start()
				del length_list[0]
				if __name__ == "__main__":
					print(
						f"{len(multiprocessing.active_children())} active children processes, queue size {queue.qsize()}",
						end="\r")
		while len(multiprocessing.active_children()) > 0:
			if __name__ == "__main__":
				print(f"{len(multiprocessing.active_children())} active children processes, queue size {queue.qsize()}",
					  end="\r")
		_, password, _ = listener(queue)
		duration = perf_counter_ns() - start
		return password, duration


if __name__ == "__main__":
	pass_hash = md5(str(input(": ")).encode()).hexdigest()
	print(Bruteforce(pass_hash, 1, 5, 5, 2).queue_thread(), end="\r")

# ---------- Make multiprocessing file reader ---------- #
