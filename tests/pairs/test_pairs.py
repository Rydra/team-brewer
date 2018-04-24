import math
from unittest.mock import MagicMock

from pairs import generate_matches, generate_matches_functional_version
from match import Match
from repositories import MatchRepository, PeopleRepository


def test_generate_a_list_of_users(namelist_data):
    even_name_list = namelist_data

    (
        _Scenario()
        .given_a_list_of_available_people(even_name_list)
        .when_I_generate_matches_for_all_the_people_in_the_name_list()
        .then_everyone_should_have_a_match()
        .then_the_matches_should_have_been_saved()
    )


def test_generate_a_list_of_users_odd(namelist_data):

    odd_name_list = namelist_data + ['Petunia']

    (
        _Scenario()
        .given_a_list_of_available_people(odd_name_list)
        .when_I_generate_matches_for_all_the_people_in_the_name_list()
        .then_everyone_should_have_a_match()
        .then_the_matches_should_have_been_saved()
    )


def test_generate_a_list_of_users_considering_the_history(namelist_data):
    matches = [
        Match('Francis', 'David'), Match('Mike', 'Edward'), Match('Jack', 'Francis'),
        Match('Jim', 'David'), Match('Russel', 'Jack'), Match('Jim', 'Mike')
    ]

    (
        _Scenario()
        .given_a_list_of_available_people(namelist_data)
        .given_a_history_of_previous_matches(matches)
        .when_I_generate_matches_for_all_the_people_in_the_name_list()
        .then_everyone_should_have_a_match()
        .then_there_should_not_have_any_repetition_with_previous_dates(matches)
    )


def test_generate_a_list_of_users_from_file(namelist_data):
    assert namelist_data == ['Francis', 'David', 'Mike', 'Jack', 'Russel', 'Jim']


class _Scenario:
    def __init__(self):
        self.people_repository = MagicMock()
        self.people_repository.all.return_value = []
        PeopleRepository.set_instance(self.people_repository)

        self.match_repository_mock = MagicMock()
        self.match_repository_mock.find_all_matches.return_value = []
        MatchRepository.set_instance(self.match_repository_mock)


    def given_a_list_of_available_people(self, names):
        self.people_repository.all.return_value = names
        self.names = names
        return self

    def given_a_history_of_previous_matches(self, matches):
        def find_matches(person):
            return [match for match in matches if match.is_present(person)]

        self.match_repository_mock.find_all_matches.side_effect = find_matches
        return self

    def when_I_generate_matches_for_all_the_people_in_the_name_list(self):
        self.matches = generate_matches()
        return self

    def when_I_generate_matches_for_all_the_people_in_the_name_list_functional(self):
        self.matches = generate_matches_functional_version()
        return self

    def then_everyone_should_have_a_match(self):
        assert len(self.matches) == math.ceil(len(self.names) / 2)
        for name in self.names:
            assert any(match for match in self.matches if match.is_present(name))

        return self

    def then_the_matches_should_have_been_saved(self):
        pass
        # for match in self.matches:
        #
        #     if match.is_present(REST_DAY):
        #         assert not self.match_repository.find(person1=match.person1, person2=match.person2)
        #     else:
        #         assert self.match_repository.find(person1=match.person1, person2=match.person2)

    def then_there_should_not_have_any_repetition_with_previous_dates(self, previous_matches):
        assert len(set(previous_matches) & set(self.matches)) == 0
        return self
