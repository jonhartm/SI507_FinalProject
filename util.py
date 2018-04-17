import json
import time

def CleanJSONString(s):
    i = {}
    s = s.replace("\"", "'")
    i['id'] = GetString(s, "id", False)
    i['name'] = GetString(s, "name")
    if "'job': " in s: i['job'] = GetString(s, "job")
    return i

# lifted from https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
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

class Timer():
    def Start(self):
        self.start = time.time()

    def Stop(self):
        self.end = time.time()
        self.elapsed = self.end-self.start

    def __str__(self):
        return str(self.elapsed)+"ms"
