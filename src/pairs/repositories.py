import datetime

from common import singleton
from match import Match


@singleton
class MatchRepository:
    def __init__(self):
        self._stored_matches = []
        self._history_file_path = None

    def init(self, history_file_path):
        self._history_file_path = history_file_path

        with open(self._history_file_path, "r", encoding='utf-8') as fs:
            matches = [line.split(',')
                       for line in fs.readlines() if line]
            for match in matches:
                person1, person2, date = match
                self._stored_matches.append(Match(person1.strip(), person2.strip(), datetime.datetime.strptime(date.strip(), "%d-%m-%Y")))

    def save(self, match):
        with open(self._history_file_path, "a") as fs:
            fs.write(f'{match.person1}, {match.person2}, {match.date.strftime("%d-%m-%Y")}\n')

    def find(self, person1, person2):
        return next((match for match in self._stored_matches if match.is_present(person1) and match.is_present(person2)), None)

    def find_all_matches(self, person):
        return [match for match in self._stored_matches if match.is_present(person)]


@singleton
class PeopleRepository:
    def __init__(self):
        self._people_file_path = None

    def init(self, people_file_path):
        self._people_file_path = people_file_path

    def all(self):
        with open(self._people_file_path, 'r', encoding="utf-8") as fs:
            people = [x.strip() for x in fs.readlines() if x and not x.startswith('#')]

        return people
