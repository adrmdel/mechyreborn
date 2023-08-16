def quote(ctx, query, database):
    split_query = query.split(' ')
    if split_query[0] == 'add':
        return 'ah'