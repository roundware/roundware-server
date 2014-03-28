#***********************************************************************************#

# ROUNDWARE
# a contributory, location-aware media platform

# Copyright (C) 2008-2014 Halsey Solutions, LLC
# with contributions from:
# Mike MacHenry, Ben McAllister, Jule Slootbeek and Halsey Burgund (halseyburgund.com)
# http://roundware.org | contact@roundware.org

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

#***********************************************************************************#


import getopt
import sys
import re


def getopts(options):

    optargs = {}
    opttype = {}
    validopts = ["help"]

    for o in options:
        if len(o) == 1:
            name = o[0]
            optargs[name] = False
            validopts.append(name)
        elif len(o) in (2, 3):
            name = o[0]
            type = o[1]
            validopts.append(name + "=")
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


def usage(validopts):
    print "Invalid arguments. A better error message should be written for this"
    sys.exit(2)
