import random
import re

main_regex = r'([+-]?)(\d+)d(\d+)(?:t(\d+)|e(\d+)|x(\d+))*|([+-]\d+)| (.+$)'
cod_regex = r'(\d+)co[f]?d(\d+|r)? ?(.+$)?'
exalted_regex = r'(\d+)ex(\d+)?([+-](?:\d+))? ?(.+$)?'
paragons_regex = r'(\d+)para ?(.+$)?'

'''
I need to keep this in my head properly because regex is a labyrinthine monster which I have delved too deeply within.

.Group 1[0]: Modifier - Whether to subtract or add the total.
.Group 2[1]: Number - Number of dice to roll in a given step.
.Group 3[2]: Sides - The maximum number that can be rolled on a given die.
.Group 4[3]: Target Number - If present, sets a target number for a given roll to either meet or exceed.
Will cut off all further existing steps except for the comment, and return a count of successes instead of a sum.
.Group 5[4]: Explosion Number - If present, sets a target number for a given roll to then explode
Resultant explosions will either conditionally increment the count if the result is a count of successes,
or be added to the result if the result is a sum. <-- TBA when it matters
.Group 6[5]: Double Number - If present, sets a target number for a given roll to grant two successes.
.Group 7[6]: Flat Modifier - A flat number to add/subtract to a roll result. No above groups should be matched.
Should also be ignored if group 4 was ever matched during the whole process.
.Group 8[7]: Comment - Catches all other content to pass as an identifying string. No above groups should be matched.
'''

list_results = []
notable_rolls = []
current_mode = {'target': -1, 'explosion': -1, 'double': -1}


def check_alias(query):
    cod_roll = re.findall(cod_regex, query)
    exalted_roll = re.findall(exalted_regex, query)
    paragons_roll = re.findall(paragons_regex, query)
    if len(cod_roll) > 0:  # cofd rules
        result = cod_roll[0]
        if result[1] == 'r':
            return '{}d10t8e100001{}'.format(
                result[0],
                ' ' + result[2] if result[2] != '' else '')
        return '{}d10t8e{}{}'.format(
            result[0],
            result[1] if result[1].isnumeric() else '10' if result[1] != 'r' else '-2',
            ' '+result[2] if result[2] != '' else '')
    elif len(exalted_roll) > 0:  # exalted rules
        result = exalted_roll[0]
        return '{}d10t7x{}{}{}'.format(
            result[0],
            result[1] if result[1].isnumeric() else '10',
            result[2] if result[2] != '' else '',
            ' '+result[3] if len(result[3]) > 0 else '')
    elif len(paragons_roll) > 0: #prowlers and paragons rules
        result = paragons_roll[0]
        return '{}d6t4x6{}'.format(
            result[0],
            ' ' + result[1] if result[1] != '' else '')
    return query


def do_roll(number, sides):
    results = list(map(lambda x: random.randint(1, sides), range(number)))
    list_results.append(results)


def find_successes():
    list_of_results = list_results[-1] if len(list_results) > 0 else list_results
    list_of_successes = [i for i in list_of_results if i >= current_mode['target']]
    notable_rolls.append(list_of_successes)


def process_step(num, sides):
    do_roll(num, sides)
    if current_mode['target'] != -1:
        find_successes()
        if current_mode['explosion'] == 1001:
            do_roll(num - len(notable_rolls[-1]), sides)
            find_successes()
        if current_mode['explosion'] != -1 and len(notable_rolls[-1]) > 0:
            while True:
                list_of_explosions = [i for i in notable_rolls[-1] if i >= current_mode['explosion']]
                if len(list_of_explosions) == 0:
                    break
                do_roll(len(list_of_explosions), sides)
                find_successes()


def clean_up():
    list_results.clear()
    notable_rolls.clear()
    current_mode['target'] = -1
    current_mode['explosion'] = -1
    current_mode['double'] = -1


def count_successes():
    list_of_successes = [x for sublist in notable_rolls for x in sublist]
    if current_mode['double'] != -1:
        return len(list_of_successes) + len([x for x in list_of_successes if x >= current_mode['double']])
    else:
        return len(list_of_successes)


def format_result(final_tally, comment):
    if comment != '':
        return '*{}* -- {} -> **{}**'.format(comment, list_results if len(list_results) > 1 else list_results[0], final_tally)
    else:
        return '{} -> **{}**'.format(list_results if len(list_results) > 1 else list_results[0], final_tally)


def pre_format_count_of_successes(count, modifier):
    result = str(count + modifier)
    if modifier < 0:
        if count == modifier * -1:
            return 'Success! Meets difficulty!'
        elif count < modifier * -1:
            return 'Failure!'
        else:
            return 'Success! {} over!'.format(result)
    else:
        return result + ' successes!'


def roll(query):
    try:
        running_total = 0
        rolls = re.findall(main_regex, check_alias(query))
        comment = ''
        for sub_roll in rolls:
            if sub_roll[3].isnumeric():
                current_mode['target'] = int(sub_roll[3]) if current_mode['target'] == -1 else current_mode['target']
            if sub_roll[4].isnumeric():
                current_mode['explosion'] = int(sub_roll[4]) if current_mode['explosion'] == -1 else current_mode['explosion']
            if sub_roll[5].isnumeric():
                current_mode['double'] = int(sub_roll[5]) if current_mode['double'] == -1 else current_mode['double']
            if sub_roll[6] != '':  # flat mod
                running_total += int(sub_roll[6])
            elif sub_roll[1] != '':
                process_step(int(sub_roll[1]), int(sub_roll[2]))
                if current_mode['target'] == -1:
                    running_total += sum(list_results[-1])*-1 if sub_roll[0] == '-' else sum(list_results[-1])
            if sub_roll[7] != '':
                if running_total == 0 and len(list_results) == 0:
                    raise ValueError
                comment = sub_roll[7]
                continue
        if current_mode['target'] != -1:
            count_of_successes = count_successes()
            to_format = pre_format_count_of_successes(count_of_successes, running_total)
            final_result = format_result(to_format, comment)
        else:
            final_result = format_result(running_total, comment)
        clean_up()
        return final_result
    except (ValueError, IndexError):
        clean_up()
        return ValueError
    except Exception as e:
        print(e)
        clean_up()
        print(query)
        print('Something has gone wrong with the above command.')
        return 'Something has gone wrong.'
