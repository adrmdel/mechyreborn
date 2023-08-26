import re
import datetime

import pymongo.errors
from dateutil.relativedelta import *

time_regex = r'(?:(\d+)y)?(?:(\d+)mo)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?'


def reminder(ctx, query, database):
    target_date, message = query.split(' ', 1)
    result = list(re.findall(time_regex, target_date)[0])
    for x in range(len(result)):
        result[x] = int(result[x]) if result[x].isnumeric() else 0
    now = datetime.datetime.now()
    then = now + relativedelta(years=int(result[0]),
                               months=int(result[1]),
                               days=int(result[2]),
                               hours=int(result[3]),
                               minutes=int(result[4]))
    try:
        if now == then:
            raise ValueError
        database.insert_one(document={
            "author": ctx.author.mention,
            "chan_id": ctx.channel.id,
            "date": then,
            "message": message
        })
        return 'Done!'
    except pymongo.errors.OperationFailure:
        return 'I cannot reach the database. Please try again later.'
    except ValueError:
        return 'You have formatted the request incorrectly.'


def check_and_clear_reminders(database):
    cursor = database.find({"date": {"$lte": datetime.datetime.now()}})
    result = []
    for entry in cursor:
        result.append(entry)
        database.delete_one(entry)
    return result
