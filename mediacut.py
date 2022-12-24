from hhmmss import hhmmss
import six
from cmd import Cmd
from hhmmss import from_string
import subprocess
import traceback
import os.path


class keyframe_command(object):

	def __init__(self, filename):
		self.filename = filename

	@property
	def args(self):
		return ['ffprobe', '-loglevel', 'error', '-show_frames', '-select_streams', 'v', '-skip_frame', 'nokey', '-show_entries', 'frame=pts_time', '-of', 'csv=print_section=0', self.filename, '-read_intervals']

	def get_keyframes(self, hms):
		try:
			hms1 = hms - 20
		except AssertionError:
			hms1 = hhmmss(0)
		hms2 = hms + 20
		pm = str(hms1)+'%'+str(hms2)
		args = self.args + [pm]
		six.print_(' '.join(args))
		ret = subprocess.check_output(args).decode('ascii')
		ret = ret.splitlines(False)
		ret = [r.partition(',')[0] for r in ret if len(r) > 0]
		return list(map(float, ret))


class cut_command(object):

	def __init__(self, infile, outfile):
		assert infile and outfile
		self.infile = infile
		self.outfile = outfile

	@property
	def args(self):
		return ['ffmpeg', '-hide_banner', '-i', self.infile, '-c', 'copy']

	def run_cut(self, t_ss, t_to):
		t_args = []
		if t_ss:
			t_ss = from_string(t_ss)
			t_args += ['-ss', str(t_ss)]
		if t_to:
			t_to = from_string(t_to)
			t_args += ['-to', str(t_to)]
		args = self.args + t_args + [self.outfile]
		six.print_(' '.join(args))
		subprocess.check_call(args)


class mediacut_shell(Cmd):

	def __init__(self, infile, outfile=None):
		self.infile = infile
		self.outfile = outfile
		Cmd.__init__(self)

	def emptyline(self):
		pass

	def default(self, line):
		args = line.split()
		try:
			if len(args) == 1:
				t = from_string(line)
				keys = keyframe_command(self.infile).get_keyframes(t)
				adj = find_adjcent_keyframe(keys, t.total_seconds)
				six.print_('timestamp', t.total_seconds)
				six.print_(adj[0])
				six.print_(adj[1])
			else:
				t_ss = None
				t_to = None
				if len(args) == 2:
					assert args[0] in ['ss', 'to']
					if args[0] == 'ss':
						t_ss = args[1]
					else:
						t_to = args[1]
				elif len(args) == 4:
					assert args[0] == 'ss' and args[2] == 'to'
					t_ss = args[1]
					t_to = args[3]
				else:
					raise ValueError('input error')
				assert t_ss or t_to
				cut_command(self.infile, self.outfile).run_cut(t_ss, t_to)
		except:
			traceback.print_exc()
		six.print_()

	def do_EOF(self, line):
		return True


def find_adjcent_keyframe(keys, t):
	n = len(keys)
	if n < 2:
		return keys
	else:
		for i in range(n-1):
			p = keys[i]
			q = keys[i+1]
			if p <= t and q >= t:
				return (p, q)

usage = '''
to seek keyframes, command line requires 'infile' parameter only
to cut media, 'outfile' parameter is also required

After entered interactive command line

a) to seek keyframes
enter the single timestamp
output would be:
timestamp in seconds
prev keyframe in seconds
next keframe in seconds

b) to cut media
command examples
   > ss 0:10
   > ss 0:10 to 0:15
   > to 0:15

ctrl+z to exit
'''

import argparse
if __name__ == '__main__':

	parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=usage)
	parser.add_argument('infile')
	parser.add_argument('outfile', nargs='?', default=None)
	arg = parser.parse_args()

	infile = arg.infile

	c = mediacut_shell(infile, arg.outfile)
	c.prompt = 'mediecut {infile}> '.format(infile=os.path.basename(infile))
	c.cmdloop()


