import sys

if sys.version_info.major == 3:
    basestring = (str, bytes)
else:
    basestring = basestring
