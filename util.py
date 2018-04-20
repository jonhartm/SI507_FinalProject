#-------------------------------------------------------------------------------
# UTIL.PY
# Tiny Utility functions that might be useful for other projects
#-------------------------------------------------------------------------------

import json
import time

# can't load single quoted strings to json directly, so we'll parse them here
def CleanJSONString(s):
    i = {}
    s = s.replace("\"", "'")
    i['id'] = GetString(s, "id", False)
    i['name'] = GetString(s, "name")
    if "'job': " in s: i['job'] = GetString(s, "job")
    return i

# lifted from https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
# gets the string that exists between the first and last
# since I know what this string will look like ('key':'value') I can hardcode those
def GetString(s, key, is_string=True):
    if is_string:
        first = "'" + key + "': '"
        last = "', "
    else:
        first = "'" + key + "': "
        last = ", "
    start = s.index( first ) + len( first )
    end = s.index( last, start )
    return s[start:end]

# try to parse a string to an int.
# returns None if it failed
def tryParseInt(s):
    try:
        return (int(s))
    except Exception:
        return None

# class for starting and stopping a timer, then reporting the elapsed time
class Timer():
    def Start(self):
        self.start = time.time()

    def Stop(self):
        self.end = time.time()
        self.elapsed = self.end-self.start

    def __str__(self):
        return '{:.3}s'.format(self.elapsed)
