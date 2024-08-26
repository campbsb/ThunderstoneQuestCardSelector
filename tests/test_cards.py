import pytest
from cards import Cards

@pytest.fixture()
def cards():
    return Cards()

def test_quest_number_and_name_list(cards):
    assert "1 A Mirror in the Dark" in cards.quest_number_and_name_list()

def test_get_heroes(cards):
    card_sets = cards.get_selected_card_sets(["1 A Mirror in the Dark"])
    heroes = card_sets.select_diverse_heroes()
    assert [v for v in heroes if v.is_cleric()]
    assert [v for v in heroes if v.is_fighter()]
    assert [v for v in heroes if v.is_rogue()]
    assert [v for v in heroes if v.is_wizard()]
