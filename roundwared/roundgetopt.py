import getopt
import sys
import re

def getopts (options):

	optargs = {}
	opttype = {}
	validopts = ["help"]

	for o in options:
		if len(o) == 1:
			name = o[0]
			optargs[name] = False
			validopts.append(name)
		elif len(o) in (2,3):
			name = o[0]
			type = o[1]
			validopts.append(name+"=")
			opttype[name] = type
			if len(o) == 3:
				default = o[2]
				optargs[name] = default
		else:
			print "Invalid opt argument: ", o
			sys.exit(2)

	try:
		opts, args = getopt.getopt(sys.argv[1:], "", validopts)
	except getopt.GetoptError, err:
		print str(err)
		usage(validopts)
		sys.exit(2)

	regexp = re.compile('^--')

	for o, a in opts:
		if o == "--help":
			usage()
			sys.exit()
		else:
			p = regexp.sub('', o)
			if p in opttype.keys():
				optargs[p] = opttype[p](a)
			else:
				optargs[p] = True

	return optargs

def usage (validopts):
	print "Invalid arguments. A better error message should be written for this"
	sys.exit(2)
