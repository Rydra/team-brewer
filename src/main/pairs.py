import argparse
import datetime
import os
import random
from collections import defaultdict

from slackclient import SlackClient
# NOTE: THIS IS A FREAKING GRAPH!!
import re


def load_already_generated_pairs(lines):
    pairs = defaultdict(set)
    for line in lines:
        names = [x.strip() for x in line.split(',')]

        pairs[names[0]].add(names[1])

    return pairs


def have_already_met(mate1, mate2, already_generated_pairs):
    return mate1 in already_generated_pairs and mate2 in already_generated_pairs[mate1]


def pop_next_candidate(people_list, last_alone):
    if last_alone :
        mate1 = last_alone
        last_alone = None
        people_list.remove(mate1)
    else:
        i1 = random.randrange(0, len(people_list))
        mate1 = people_list.pop(i1)

    return mate1, last_alone


def generate_pairs(people, pairs_already_generated, last_alone, total_people):
    pairs = []
    lone_wolf = None

    def generate_pairs_rec(people_list, last_alone):
        if not people_list:
            return

        if len(people_list) == 1:
            # we have a lonely wolf here :D
            nonlocal lone_wolf
            lone_wolf = people_list.pop()
            mate = random.choice([p for p in total_people if p != lone_wolf])
            pairs.append((lone_wolf, mate))
            return

        else:
            # Prioritize the last alone
            mate1, last_alone = pop_next_candidate(people_list, last_alone)
            mate2 = pop_next_partner(mate1, people_list, pairs_already_generated)

            generated_pair = (mate1, mate2)
            pairs_already_generated[mate1].add(mate2)
            pairs_already_generated[mate2].add(mate1)

            pairs.append(generated_pair)

            generate_pairs_rec(people_list, last_alone)

    generate_pairs_rec(list(people), last_alone)
    return pairs, lone_wolf


def pop_next_partner(mate1, people_list, pairs_already_generated):
    found = False
    mate2 = None
    while not found:
        try:
            mate2 = next(mate for mate in people_list if not have_already_met(mate1, mate, pairs_already_generated))
            found = True
        except StopIteration:
            print(f'Could not find a mate without repetition for {mate1}. Resettings him')

            for other_mates in pairs_already_generated[mate1].copy():
                pairs_already_generated[other_mates].remove(mate1)

            del pairs_already_generated[mate1]

    people_list.remove(mate2)
    return mate2


def generate_pairs_for_speeddater(speed_dater, num_dates, people, pairs_already_generated):
    pairs = []
    people.remove(speed_dater)

    for _ in range(num_dates):

        mate2 = pop_next_partner(speed_dater, people, pairs_already_generated)

        generated_pair = (speed_dater, mate2)
        pairs_already_generated[speed_dater].add(mate2)
        pairs_already_generated[mate2].add(speed_dater)

        pairs.append(generated_pair)

    return pairs


def main():
    parser = argparse.ArgumentParser(description='Parse arguments for debugging purposes')
    parser.add_argument('inputfilename', help='the path to the list of names')
    parser.add_argument('outputfilename', help='the file to store the pairs that have been already generated')
    parser.add_argument('--speeddate', type=str, help='Prepare first a speed dating with this user')

    parsed_arguments = parser.parse_args()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    inputfilename = os.path.join(dname, parsed_arguments.inputfilename)
    outputfilename = os.path.join(dname, parsed_arguments.outputfilename)

    last_alone = None
    already_generated = defaultdict(set)

    with open(inputfilename, "r", encoding="utf-8") as inputfs:
        people = [x.strip() for x in inputfs.readlines() if x and not x.startswith('#')]

    if os.path.exists(outputfilename):
        with open(outputfilename, "r", encoding="utf-8") as outputfs:
            lines = [x.strip() for x in outputfs.readlines() if x]

            if lines and 'last_alone:' in lines[0]:
                last_alone = re.findall('last_alone:(.*)', lines.pop(0))[0].strip()

            already_generated = load_already_generated_pairs(lines)

    pairs = []

    # As pairs are being generated, people are removed from this queue
    people_queue = list(people)

    if parsed_arguments.speeddate:
        pairs_speeddate = generate_pairs_for_speeddater(parsed_arguments.speeddate, 3, people_queue, already_generated)
        pairs.extend(pairs_speeddate)

    pairs_2, lone_wolf = generate_pairs(people_queue,
                           already_generated,
                           last_alone if last_alone != parsed_arguments.speeddate else None,
                            people)

    pairs.extend(pairs_2)

    new_last_alone = None

    last_pair = pairs[-1]
    cool_mate = None
    if lone_wolf:
        new_last_alone = last_pair[0]
        cool_mate = last_pair[1]

    content = f"Hi buttoners, how's it going? These are the dates that have been arranged " \
              f"for this week (starting at {datetime.datetime.now().strftime('%Y-%m-%d')}) \n"
    for mate1, mate2 in pairs:
        content += f'{mate1} with {mate2}\n'

    content += '\n'

    # TODO: Instead of being alone, someone will have two dates
    if new_last_alone:
        content += f'{cool_mate}, since we are an odd number of people, we randomly matched you with {lone_wolf}, ' \
                   f'so you will have two dates this week :D'

    print(content)

    # Slack test
    # https://api.slack.com/methods/chat.postMessage#channels

    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    sc.api_call(
        "chat.postMessage",
        channel="#team-brewer",
        text=f"@everyone\n```{content}```",
        as_user=True
    )

    with open(outputfilename, "w", encoding="utf-8") as outputfs:
        if new_last_alone:
            outputfs.write(f'last_alone:{new_last_alone}\n')

        for mate1, mates in already_generated.items():
            for mate in mates:
                outputfs.write(f'{mate1},{mate}\n')


if __name__ == '__main__':
    main()
