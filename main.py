"""
Alexander Burow

License: GPL3
"""

from read import FileReader  # needs hash
from bruteforce import Bruteforce  # needs hash, processes, threads, min/max length
from util import convert_time

from time import perf_counter_ns
from hashlib import md5
import os


class PasswordBreaker:
	def __init__(self, hash_input, num_processes, num_threads, min_length, max_length):
		self.hash_input = hash_input
		self.num_processes = num_processes
		self.num_threads = num_threads
		self.min_length = min_length
		self.max_length = max_length

		self.db_addr = f"{os.getcwd()}\\password_database\\password_database.db"

	def start_reader(self):
		init = FileReader(input_hash=self.hash_input)
		return init.read_db(db_addr=self.db_addr)

	def start_brute(self):
		init = Bruteforce(input_hash=self.hash_input, min_len=self.min_length, max_len=self.max_length,
						  threads=self.num_threads, processes=self.num_processes)
		return init.queue_thread()

	def run(self):
		start = perf_counter_ns()
		password, _ = self.start_reader()
		if password is not None:
			if __name__ == '__main__':
				print(f"password: {password}, total duration: {convert_time(perf_counter_ns() - start)}")
			return password
		if __name__ == '__main__':
			print(f"Database exhausted... starting bruteforce")
		password, _ = self.start_brute()
		if __name__ == '__main__':
			print(f"password: {password}, total duration: {convert_time(perf_counter_ns() - start)}")
		return password


if __name__ == '__main__':
	pass_hash = md5(str(input(": ")).encode()).hexdigest()
	PasswordBreaker(hash_input=pass_hash, num_processes=10, num_threads=5, min_length=3, max_length=6).run()
