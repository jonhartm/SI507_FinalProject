import json

def CleanJSONString(s):
    i = {}
    s = s.replace("\"", "'")
    i['id'] = GetString(s, "id", False)
    i['name'] = GetString(s, "name")
    if "'job': " in s: i['job'] = GetString(s, "job")

    try:
        print(i)
    except Exception as e:
        pass

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

# def CleanJSONString(s):
#     if "'job': " in s:
#         s = "{'job': " + s.split("'job': ")[1]
#     else:
#         s = "{'name': " + s.split("'name': ")[1]
#
#     s = s.replace(" O'", " O`") # eg. O'donnelly
#     s = s.replace(" L'", " L`") # eg. L'Estrange
#     s = s.replace(" D'", " D`") # eg. D'Onofrio
#     s = s.replace("'", "\"") # json wants double quotes
#     s = s.replace('None', '"None"') # json doesn't like None
#     return json.loads(s)

# def CleanJSONString(s):
#     # specific replaces
#     print("in:")
#     print(s)
#
#     # this is dumb and I should use regex but I'm stuck on that road and need to keep going
#     while '"' in s:
#         # input(s)
#         pre, val = s.split('"')[0:2]
#         post = '"'.join(s.split('"')[2:])
#         if "'" in val:
#             splits = val.split("'")
#             if len(splits) == 3:
#                 pre2, val2, post2 = val.split("'")[0:3]
#                 val = "{}({}){}".format(pre2, val2, post2)
#             else:
#                 val = val.replace("'", "`")
#         s = "{}|{}|{}".format(pre, val, post)
#
#     print("first replace:")
#     print(s)
#
#     s = s.replace(" O'", " O") # eg. O'donnelly
#     s = s.replace("'s", "s") # eg. Judge's clerk
#     s = s.replace('None', '"None"') # remove instances of None that are not in quotes
#     s = s.replace("'", "\"") # python wants double quoted strings
#     s = s.replace("|", "\"") # replace placeholders with double quotes
#     s = s.replace('""', "\"") # pull out double-double quotes
#     print("ready for json:")
#     input(s)
#     return json.loads(s)
