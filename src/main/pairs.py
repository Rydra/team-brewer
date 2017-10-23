import argparse
import os
import random
from collections import defaultdict

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
    if last_alone:
        mate1 = last_alone
        last_alone = None
        people_list.remove(mate1)
    else:
        i1 = random.randrange(0, len(people_list))
        mate1 = people_list.pop(i1)

    return mate1, last_alone


def generate_pairs(people, pairs_already_generated, last_alone):
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

    def generate_pairs_rec(people_list, last_alone):
        if not people_list:
            return

        if len(people_list) == 1:
            pairs2.append((people_list.pop(),))

        else:
            # Prioritize the last alone
            mate1, last_alone = pop_next_candidate(people_list, last_alone)
            mate2 = pop_next_partner(mate1, people_list)

            generated_pair = (mate1, mate2)
            pairs_already_generated[mate1].add(mate2)
            pairs_already_generated[mate2].add(mate1)

            pairs2.append(generated_pair)

            generate_pairs_rec(people_list, last_alone)

    generate_pairs_rec(list(people), last_alone)
    return pairs2


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parse arguments for debugging purposes')
    parser.add_argument('inputfilename', help='the path to the list of names')
    parser.add_argument('outputfilename', help='the file to store the pairs that have been already generated')

    parsed_arguments = parser.parse_args()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    inputfilename = os.path.join(dname, parsed_arguments.inputfilename)
    outputfilename = os.path.join(dname, parsed_arguments.outputfilename)

    pairs = []
    last_alone = None
    already_generated = defaultdict(set)

    if os.path.exists(outputfilename):
        with open(outputfilename, "r", encoding="utf-8") as outputfs:
            lines = [x.strip() for x in outputfs.readlines() if x]

            if lines and 'last_alone:' in lines[0]:
                last_alone = re.findall('last_alone:(.*)', lines.pop(0))[0].strip()

            already_generated = load_already_generated_pairs(lines)

    with open(inputfilename, "r", encoding="utf-8") as inputfs, open(outputfilename, "w", encoding="utf-8") as outputfs:

        pairs = generate_pairs((x.strip() for x in inputfs.readlines() if x), already_generated, last_alone)

        new_last_alone = None
        last_pair = pairs[-1]
        if len(last_pair) == 1:
            new_last_alone = last_pair[0]
            pairs.remove(last_pair)

        content = 'Today should have a breakfast together:\n'
        for mate1, mate2 in pairs:
            content += f'{mate1} with {mate2}\n'

        content += '\n'

        if new_last_alone:
            content += f'{new_last_alone}, you will rest for today, next day you will have a date for sure :D'

        print(content)

        if new_last_alone:
            outputfs.write(f'last_alone:{new_last_alone}\n')

        for mate1, mates in already_generated.items():
            for mate in mates:
                outputfs.write(f'{mate1},{mate}\n')
