import glob
import os
import stat
from distutils.core import setup
from distutils.extension import Extension

setup(
    name        = "Roundware Server",
    version     = "2.0",
    description = 'Roundware Server',
    author      = 'Mike MacHenry, Ben McAllister, Halsey Burgund, Bryan Wilson',
    author_email    = 'contact@roundware.org',
    url     = 'http://roundware.sourceforge.net',
    license     = 'LGPL',
    scripts     = glob.glob('bin/*'),
)
