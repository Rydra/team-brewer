import argparse
import datetime
import os

from match import Match
from notifications import SlackNotifier
from repositories import MatchRepository, PeopleRepository

REST_DAY = 'day_off'


def generate_matches_functional_version():
    available_people = set(PeopleRepository.instance().all())
    available_people = available_people | {REST_DAY} if len(available_people) % 2 else available_people

    def generate_matches_rec(available_people, found_matches):
        if not available_people:
            return found_matches

        person = available_people.pop()
        previous_matches = MatchRepository.instance().find_all_matches(person)
        already_met_people = set(
            match.person1 if match.person1 != person else match.person2 for match in previous_matches)
        candidates = set(available_people - already_met_people)

        if not candidates:
            match = _find_match_with_partner_not_in_history(found_matches, already_met_people)
            if not match:
                return generate_matches_rec(available_people, found_matches)

            found_matches.remove(match)
            new_partner, next_candidate = (
            match.person1, match.person2) if match.person1 not in already_met_people else (match.person2, match.person1)

            return generate_matches_rec(available_people | next_candidate, found_matches + [Match(person, new_partner)])

        else:
            partner = candidates.pop()
            return generate_matches_rec(available_people - {partner}, found_matches + [Match(person, partner)])

    return generate_matches_rec(available_people, [])


def generate_matches():
    # Given the list of available people, the information of the last rotation
    # and the history of matches... Try to find a way to plan dates without
    # repeating them
    date = datetime.datetime.now()

    available_people = set(PeopleRepository.instance().all())
    if len(available_people) % 2 == 1:
        available_people.add(REST_DAY)

    matches = []
    while len(available_people) > 0:
        person = available_people.pop()

        already_met_people = _find_already_met_partners(person)
        candidates = set(available_people - already_met_people)

        if not candidates:
            match = _find_match_with_partner_not_in_history(matches, already_met_people, available_people)
            if not match:
                continue

            matches.remove(match)

            new_partner, next_candidate = (match.person1, match.person2) if match.person1 not in already_met_people else (match.person2, match.person1)
            matches.append(Match(person, new_partner, date))
            available_people.add(next_candidate)
        else:
            partner = candidates.pop()
            matches.append(Match(person, partner, date))
            available_people.remove(partner)

    # Store the dates
    match_repository = MatchRepository.instance()
    for match in matches:
        if not match.is_present(REST_DAY):
            match_repository.save(match)

    return matches


def _find_already_met_partners(person):
    previous_matches = MatchRepository.instance().find_all_matches(person)
    return set(match.person1 if match.person1 != person else match.person2 for match in previous_matches)


def _find_match_with_partner_not_in_history(matches, already_met_people, available_people):
    def is_candidate(person):
        """
        A candidate is a person that is not in the history of already met people, but can match
        with someone in the list of available people
        """
        if person in already_met_people:
            return False

        partners = _find_already_met_partners(person)
        if len(available_people - partners) > 0:
            return True

    for match in matches:
        if is_candidate(match.person1) or is_candidate(match.person2):
            # Check if one of the people in this match has
            return match

    return None


def _generate_matches_message(matches):
    content = f"Hi buttoners, how's it going? These are the dates that have been arranged " \
              f"for this week (starting at {datetime.datetime.now().strftime('%Y-%m-%d')}) \n"

    for match in matches:
        content += f'{match.person1} with {match.person2}\n'

    content += '\n'

    return content


def execute():
    # notifier = SlackNotifier()
    matches = generate_matches()
    # notifier.notify(generate_matches_message(matches))

    print(_generate_matches_message(matches))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse arguments for debugging purposes')
    parser.add_argument('inputfilename', help='the path to the list of names')
    parser.add_argument('outputfilename', help='the file to store the pairs that have been already generated')
    parser.add_argument('--speeddater', type=str, help='Prepare this person for some speed dates')

    parsed_arguments = parser.parse_args()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)

    inputfilename = os.path.join(dname, parsed_arguments.inputfilename)
    outputfilename = os.path.join(dname, parsed_arguments.outputfilename)

    MatchRepository.instance().init(outputfilename)
    PeopleRepository.instance().init(inputfilename)

    execute()
