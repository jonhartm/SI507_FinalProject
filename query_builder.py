# params: columns - a list of strings that determine which colums are returned in the query
#         table - a string for the name of the table to pull data from
#         joins - an array of plain Join statements as strings
#         filter - a two or three element array formated either ["columnName","value"] or ["columnName", "boolOperator", "value"]
#                  the last item in the list can be either a string or a number
#         order_by - a list of columns to order the data by
#         limit - a list to determine how many tuples should be returned
#                 must be in the format ["top"|"bottom", int]

def selectQueryBuilder(columns, table, joins=None, group_by=None, filter=None, order_by=None, limit=None):
    query = "SELECT " + ', '.join(columns) + " FROM " + table + " "
    if joins is not None:
        query += " ".join(joins) + " "
    if group_by is not None:
        query += 'GROUP BY {} '.format(group_by)
    if filter is not None:
        # "LIKE" rather than "=" so case doesn't matter
        if group_by is None:
            query += 'WHERE ' + selectQueryBuilder_filterParse(filter)
        else:
            query += 'HAVING ' + selectQueryBuilder_filterParse(filter)
    if order_by is not None:
        query += "ORDER BY " + ','.join(order_by) + " "
    if limit is not None:
        if limit[0] == "top":
            query += "DESC "
        query += "LIMIT " + str(limit[1 ])
    return query.strip()

def selectQueryBuilder_filterParse(filter):
    # if the filter is multi-part, recurse through it
    for i in range(len(filter)):
        if (isinstance(filter[i], list)):
            filter[i] = selectQueryBuilder_filterParse(filter[i])
    # if we weren't given a boolean operator, assume it's "LIKE"
    if len(filter) == 2:
        filter.insert(1, "LIKE")
    # if we don't have three elements at this point, something is wrong
    if len(filter) != 3:
        raise ValueError("filter must be either a 2 or 3 element list")
    # if we have a string as the value, put quotes around it
    # but check to make sure the second half isn't something we've already parsed
    if isinstance(filter[2], str) and not any(x in filter[2] for x in ["LIKE", "<", ">", "=", "NULL"]):
        filter[2] = '"'+filter[2]+'"'
    else: # otherwise, convert it to a string with no quotes
        filter[2] = str(filter[2])
    return " ".join(filter) + " "
