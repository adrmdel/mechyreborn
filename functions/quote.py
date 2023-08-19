import datetime
import random

import pymongo
from discord.ext.commands import Context

sort_method = [('date', pymongo.ASCENDING), ('id', pymongo.ASCENDING)]


def format(json, chosen_index, result_count):
    date = json['date'].strftime('%Y-%b-%d')
    return '[{}] {}: <{}/{}> {}'.format(date, json['author'], chosen_index, result_count, json['text'])


def quote(ctx: Context, query, database):
    print(query)
    if type(query) is str and query.startswith('add'):
        print('try adding')
        try:
            _, author, text = query.split(' ', 2)
            print(text)
            database.insert_one(document={
                "serv_id": str(ctx.guild.id),
                "chan_id": str(ctx.channel.id),
                'author': author.lower(),
                "text": text,
                "date": datetime.datetime.now()
            })
        except ValueError:
            return 'You have formatted the request incorrectly.'
        except Exception:
            return 'Something has gone wrong. Please try again later.'
        return 'Done!'
    try:
        # Specific by Author
        author, index = query.split(' ')
        index = int(index) - 1
        filter_by_author = {"serv_id": str(ctx.guild.id), "author": author.lower()}
        result_count = database.count_documents(filter_by_author)
        result = database.find(filter_by_author).sort(sort_method)[index]
        return format(result, index + 1, result_count)
    except (ValueError, AttributeError):
        pass
    except IndexError:
        return 'This person does not have that many quotes.'
    try:
        # Specific without Author
        filter_without_author = {"serv_id": str(ctx.guild.id)}
        index = int(query) - 1
        result_count = database.count_documents(filter_without_author)
        if result_count < index:
            raise IndexError
        result = database.find(filter_without_author).sort(sort_method)[index]
        return format(result, index + 1, result_count)
    except (ValueError, AttributeError, TypeError):
        pass
    except IndexError:
        return 'This server does not have that many quotes.'
    try:
        # Random by Author
        filter_by_author = {"serv_id": str(ctx.guild.id), "author": query.lower()}
        result_count = database.count_documents(filter_by_author)
        if result_count == 0:
            raise IndexError
        index = random.randint(0, result_count - 1)
        result = database.find(filter_by_author).sort(sort_method)[index]
        return format(result, index + 1, result_count)
    except (ValueError, AttributeError):
        pass
    except IndexError:
        return 'This person does not have any quotes.'
    #  Fully Random
    filter_without_author = {"serv_id": str(ctx.guild.id)}
    result_count = database.count_documents(filter_without_author)
    index = random.randint(0, result_count - 1)
    result = database.find(filter_without_author).sort(sort_method)[index]
    return format(result, index + 1, result_count)
