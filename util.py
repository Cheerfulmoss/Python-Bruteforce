"""
Alexander Burow

License: GPL3
"""

import pandas as pd


def convert_time(time, units="ns"):
	return pd.to_timedelta(arg=time, unit=units)


if __name__ == "__main__":
	print("bleh")
