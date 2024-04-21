"""
Alexander Burow

License: GPL3
"""

from time import perf_counter_ns
from hashlib import md5
import os
import sqlite3


class FileReader:
	def __init__(self, input_hash):
		self.hash_in = input_hash

		self.pass_found = False
		self.password = ""

	def read_file(self, file_addr):
		start = perf_counter_ns()
		with open(file_addr, 'r', encoding="utf-8") as word_list:
			for line in word_list:
				if md5(line.strip().encode()).hexdigest() == self.hash_in:
					self.password = line.strip()
					self.pass_found = True
					if __name__ == "__main__":
						print(
							f"password  |  {self.password}  |  found in {os.path.basename(file_addr)} in {perf_counter_ns() - start} ns")
					return self.password, perf_counter_ns() - start

	def read_db(self, db_addr):
		start = perf_counter_ns()
		connection = sqlite3.connect(database=db_addr)
		querier = connection.cursor()

		result = querier.execute("SELECT password FROM distinct_passwords")
		for password in result:
			if md5(password[0].encode()).hexdigest() == self.hash_in:
				self.password = password[0]
				self.pass_found = True
				if __name__ == "__main__":
					print(
						f"password  |  {self.password}  |  found in {os.path.basename(db_addr)} in {perf_counter_ns() - start} ns")
				return self.password, perf_counter_ns() - start
		return None, perf_counter_ns() - start

if __name__ == "__main__":
	file_addr = "/text lists/passwords.txt"
	db_addr = "D:\\OneDrive\\PycharmProjects\\!!Stand Alones\\hacking_stuff\\password_database\\password_database.db"

	pass_hash = md5(str(input(": ")).encode()).hexdigest()
	# print(FileReader(pass_hash).read_file(file_addr=file_addr), end="\r")
	print(FileReader(pass_hash).read_db(db_addr=db_addr), end="\r")
