from datetime import timedelta
import re
hhmmss_re = re.compile(r'(\d{1,2}):(\d{1,2}):(\d{1,2})', re.IGNORECASE)


class hhmmss(object):

	def __init__(self, ss, mm=0, hh=0):
		'seonds could be float'
		assert 0<=ss
		assert isinstance(mm, int) and 0<=mm
		assert isinstance(hh, int) and 0<=hh
		self._seconds = hh*3600 + mm*60 + ss

	@property
	def hours(self):
		return int(self._seconds // 3600)

	@property
	def minutes(self):
		k = self._seconds % 3600
		return int(k // 60)

	@property
	def seconds(self):
		return self._seconds % 60

	@property
	def total_seconds(self):
		return self._seconds

	def __add__(self, a):
		if isinstance(a, int) or isinstance(a, float):
			a = hhmmss(a)
		assert isinstance(a, hhmmss)
		return hhmmss(self._seconds + a.total_seconds)

	def __sub__(self, a):
		if isinstance(a, int) or isinstance(a, float):
			a = hhmmss(a)
		assert isinstance(a, hhmmss)
		return hhmmss(self._seconds - a.total_seconds)

	def __str__(self):
		return '{hh}:{mm}:{ss}'.format(hh=self.hours, mm=self.minutes, ss=self.seconds)

def numeric(s):
		if isinstance(s, int) or isinstance(s, float):
			return s
		return float(s) if '.' in s else int(s)

def from_string(hms):
	pt = list(map(numeric, hms.split(':')))
	if len(pt) == 2:
		pt = [0] + pt
	assert len(pt) == 3
	return hhmmss(pt[2], mm=pt[1], hh=pt[0])


def hhmmss_seconds(hms):
	return from_string(hms).total_seconds


def seconds_hhmmss(s):
	return str(hhmmss(numeric(s)))


if __name__ == '__main__':
	import six
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('hms')
	arg = parser.parse_args()

	six.print_(hhmmss_seconds(arg.hms))
