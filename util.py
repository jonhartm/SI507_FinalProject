def CleanJSONString(s):
    # specific replaces
    s = s.replace(" O'", " O") # eg. O'donnelly
    s = s.replace("'s", "s") # eg. Judge's clerk

    s = s.replace('None', '"None"') # remove instances of None that are not in quotes

    if '""' in s:
        print(s)
        input()

    # this is dumb and I should use regex but I'm stuck on that road and need to keep going
    while '"' in s:
        pre, val = s.split('"')[0:2]
        post = '"'.join(s.split('"')[2:])
        if "'" in val:
            pre2, val2, post2 = val.split("'")[0:3]
            val = "{}({}){}".format(pre2, val2, post2)
        s = "{}`{}`{}".format(pre, val, post)

    s = s.replace("'", "\"") # python wants double quoted strings
    s = s.replace("`", "\"") # we used the alt single quote above. replace those with double quotes
    return s
