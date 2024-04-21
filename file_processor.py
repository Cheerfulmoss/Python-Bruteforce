"""
Alexander Burow

License: GPL3
"""

from string import punctuation
from multiprocessing import Pool, Lock
import threading
from os import getcwd
import os
from time import sleep, perf_counter_ns


# https://en.wikipedia.org/wiki/Letter_frequency, https://link.springer.com/content/pdf/10.3758/BF03195586.pdf

def init(lock):
	global glock
	glock = lock


class SplitOrderFile:
	def __init__(self):
		self.total_size = 0
		self.out_addr = f"{getcwd()}\\character_frequency"
		self.running = True
		fl_upper = [
			"T", "S", "A", "M", "C", "I", "N", "B", "R", "P", "E", "D", "H", "W", "L", "O", "F", "Y", "G", "J", "U",
			"K", "V", "Q", "X", "Z"
		]
		fl_lower = [
			"e", "t", "a", "o", "i", "n", "s", "h", "r", "d", "l", "c", "u", "m", "w", "f", "g", "y", "p", "b", "v",
			"k", "j", "x", "q", "z"
		]
		fl_digits = list()
		for number in range(0, 10):
			fl_digits.append(str(number))
		fl_punctuation = list(punctuation)
		self.frequency_list = fl_upper + fl_lower + fl_digits + fl_punctuation + ["\n"]

	def process_line(self, line):
		try:
			first_letter = str(line[0])
		except IndexError:
			return
		index = self.frequency_list.index(first_letter)
		with glock:
			with open(f"{self.out_addr}\\word_list_{index}.txt", "a") as out_file:
				out_file.write(line)

	def on_file(self, file_addr):
		self.total_size = os.path.getsize(file_addr)
		threading.Thread(target=self.progress).start()
		lock = Lock()
		pool = Pool(processes=15, initializer=init, initargs=(lock,))
		with open(file_addr, "r", encoding="utf-8") as source_file:
			pool.map(self.process_line, source_file, 15)
		pool.close()
		pool.join()
		self.running = False
		for thread in threading.enumerate():
			if thread.name != "MainThread":
				thread.join()

	def progress(self):
		start = perf_counter_ns()
		print("Getting Progress...")
		progress = 0
		while self.running:
			if progress > 1:
				continue
			progress_size = 0
			sleep_time = 5 * (1 - progress)
			if sleep_time < 0:
				sleep_time = 0
			sleep(sleep_time)
			for dirpath, _, filenames in os.walk(self.out_addr):
				for filename in filenames:
					file_path = os.path.join(dirpath, filename)
					if not os.path.islink(file_path):
						progress_size += os.path.getsize(file_path)
			duration_ns = perf_counter_ns() - start
			try:
				progress = (progress_size / self.total_size)
				estimated_duration_s = round((((1 / progress) * duration_ns) - duration_ns) / 1000000000, 3)
			except ZeroDivisionError:
				estimated_duration_s = "Unknown"
			print(
				f"Progress: {round(progress * 100, 2)}% -- {estimated_duration_s} "
				f"seconds left -- Current runtime: {round(duration_ns / 1000000000, 2)} seconds                       ",
				end="\r"
			)

	def on_dir(self, dirpath):
		for file in os.listdir(dirpath):
			print(file)
			self.on_file(f"{dirpath}\\{file}")


if __name__ == "__main__":
	addr = f"{getcwd()}\\password_lists\\Most-Popular-Letter-Passes.txt"
	instant = SplitOrderFile()
	instant.on_dir(dirpath=f"{getcwd()}\\password_lists")
	# instant.on_file(file_addr=addr)
