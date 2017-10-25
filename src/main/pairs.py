import argparse
import datetime
import os
import random
from collections import defaultdict

import itertools
from heapq import heappush, heappop

from slackclient import SlackClient
# NOTE: THIS IS A FREAKING GRAPH!!
import re

import requests


class PriorityQueue:
    REMOVED = '<removed-task>'  # placeholder for a removed task

    def __init__(self):

        self.pq = []  # list of entries arranged in a heap
        self.item_finder = {}  # mapping of tasks to entries
        self.counter = itertools.count()  # unique sequence count

    def add(self, item):
        'Add a new task or update the priority of an existing task'
        priority = 0
        if item in self.item_finder:
            priority, _, _ = self.item_finder[item]
            priority += 1
            self.remove(item)
        count = next(self.counter)
        entry = [priority, count, item]
        self.item_finder[item] = entry
        heappush(self.pq, entry)

    def remove(self, item):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.item_finder.pop(item)
        entry[-1] = self.REMOVED

    def pop(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, item = heappop(self.pq)
            if item is not self.REMOVED:
                del self.item_finder[item]
                return item

        raise KeyError('pop from an empty priority queue')


def load_already_generated_pairs(lines):
    pairs = defaultdict(set)
    pq = PriorityQueue()

    for line in lines:
        names = [x.strip() for x in line.split(',')]

        pairs[names[0]].add(names[1])
        pq.add(names[0])

    person_with_least_dates = pq.pop()
    return pairs, person_with_least_dates


def have_already_met(mate1, mate2, already_generated_pairs):
    return mate1 in already_generated_pairs and mate2 in already_generated_pairs[mate1]


def pop_next_candidate(people_list):
    i1 = random.randrange(0, len(people_list))
    mate1 = people_list.pop(i1)

    return mate1


def generate_pairs(people, pairs_already_generated, person_with_least_dates):
    pairs2 = []

    def pop_next_partner(mate1, people_list):
        found = False
        mate2 = None
        while not found:
            try:
                mate2 = next(mate for mate in people_list if not have_already_met(mate1, mate, pairs_already_generated))
                found = True
            except StopIteration:
                print(f'Could not find a mate without repetition for {mate1}. Resettings him')

                for other_mates in pairs_already_generated[mate1]:
                    pairs_already_generated[other_mates].remove(mate1)

                del pairs_already_generated[mate1]

        people_list.remove(mate2)
        return mate2

    def generate_pairs_rec(people_list):
        if not people_list:
            return

        if len(people_list) == 1:
            # We've got a lone wolf :D. Pair him with
            pairs2.append((people_list.pop(), person_with_least_dates))

        else:
            # Prioritize the last alone
            mate1 = pop_next_candidate(people_list)
            mate2 = pop_next_partner(mate1, people_list)

            generated_pair = (mate1, mate2)
            pairs_already_generated[mate1].add(mate2)
            pairs_already_generated[mate2].add(mate1)

            pairs2.append(generated_pair)

            generate_pairs_rec(people_list)

    generate_pairs_rec(list(people))
    return pairs2


def send_text_to_slack(text):
    slack_token = os.environ["SLACK_API_TOKEN"]
    sc = SlackClient(slack_token)

    sc.api_call(
        "chat.postMessage",
        channel="@rydra",  # "#team-brewer",
        text=f"@everyone\n```{text}```",
        as_user=True
    )


def main():
    parser = argparse.ArgumentParser(description='Parse arguments for debugging purposes')
    parser.add_argument('inputfilename', help='the path to the list of names')
    parser.add_argument('outputfilename', help='the file to store the pairs that have been already generated')

    parsed_arguments = parser.parse_args()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    inputfilename = os.path.join(dname, parsed_arguments.inputfilename)
    outputfilename = os.path.join(dname, parsed_arguments.outputfilename)

    with open(inputfilename, "r", encoding="utf-8") as inputfs:
        people = [x.strip() for x in inputfs.readlines() if x and not x.startswith('#')]

    already_generated = defaultdict(set)
    person_with_least_dates = random.choice(people)

    if os.path.exists(outputfilename):
        with open(outputfilename, "r", encoding="utf-8") as outputfs:
            lines = [x.strip() for x in outputfs.readlines() if x]
            already_generated, person_with_least_dates = load_already_generated_pairs(lines)

    with open(outputfilename, "w", encoding="utf-8") as outputfs:

        pairs = generate_pairs(people, already_generated, person_with_least_dates)

        content = f"Hi buttoners, how's it going? These are the dates that have been arranged for this week " \
                  f"(starting at {datetime.datetime.now().strftime('%Y-%m-%d')}) \n"
        for mate1, mate2 in pairs:
            content += f'{mate1} with {mate2}\n'

        content += '\n'

        # TODO: Instead of being alone, someone will have two dates
        if len(people) % 2 == 1:
            content += f'{person_with_least_dates}, since we are an odd number of people, ' \
                       f'you will have two dates this week :D'

        print(content)

        # Slack test
        # https://api.slack.com/methods/chat.postMessage#channels
        send_text_to_slack(content)

        for mate1, mates in already_generated.items():
            for mate in mates:
                outputfs.write(f'{mate1},{mate}\n')


if __name__ == '__main__':
    main()
