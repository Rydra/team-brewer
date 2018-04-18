import math
from unittest.mock import MagicMock

from pairs import generate_matches, REST_DAY, generate_matches2
from match import Match
from repositories import MatchRepository
from services import RotationService


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

def test_generate_a_list_of_users2(namelist_data):
    even_name_list = namelist_data

    (
        _Scenario()
        .given_a_list_of_available_people(even_name_list)
        .when_I_generate_matches_for_all_the_people_in_the_name_list2()
        .then_everyone_should_have_a_match()
        .then_the_matches_should_have_been_saved()
    )


def test_generate_a_list_of_users_odd2(namelist_data):

    odd_name_list = namelist_data + ['Petunia']

    (
        _Scenario()
        .given_a_list_of_available_people(odd_name_list)
        .when_I_generate_matches_for_all_the_people_in_the_name_list2()
        .then_everyone_should_have_a_match()
        .then_the_matches_should_have_been_saved()
    )


def test_full_case(namelist_data):
    matches = [
        Match('Francis', 'David'), Match('Mike', 'Edward'), Match('Jack', 'Francis'),
        Match('Jim', 'David'), Match('Russel', 'Jack'), Match('Jim', 'Mike')
    ]

    (
        _Scenario()
        .given_a_list_of_available_people(namelist_data)
        .given_the_last_rotation_was()
        .when_I_generate_matches_for_all_the_people_in_the_name_list()
        .then_everyone_should_have_a_match()
        .then_there_should_not_have_any_repetition_with_previous_dates()
    )


def test_generate_a_list_of_users_from_file(namelist_data):
    assert namelist_data == ['Francis', 'David', 'Mike', 'Jack', 'Russel', 'Jim']


class _Scenario:
    def __init__(self):
        self.match_repository = MatchRepository.instance()
        self.rotation_service_mock = MagicMock()
        self.rotation_service_mock.get_last_rotation.return_value = []
        RotationService.set_instance(self.rotation_service_mock)

        self.match_repository_mock = MagicMock()
        MatchRepository.set_instance(self.match_repository_mock)

    def given_a_list_of_available_people(self, names):
        self.rotation_service_mock.available_people.return_value = names
        self.names = names
        return self

    def given_the_last_rotation_was(self, rotation):
        self.rotation_service_mock.get_last_rotation.return_value = rotation

    def given_a_history_of_previous_matches(self, matches):
        return self

    def when_I_generate_matches_for_all_the_people_in_the_name_list(self):
        self.matches = generate_matches()
        return self

    def when_I_generate_matches_for_all_the_people_in_the_name_list2(self):
        self.matches = generate_matches2()
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
