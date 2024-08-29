import pytest
from src.cards import Cards, SelectedCards, CardSets


@pytest.fixture()
def cards():
    return Cards()


@pytest.fixture()
def card_sets(cards):
    return cards.get_selected_card_sets(["1 A Mirror in the Dark"])


@pytest.fixture()
def selected_cards():
    return SelectedCards()


def test_quest_number_and_name_list(cards):
    assert "1 A Mirror in the Dark" in cards.quest_number_and_name_list()


def test_diverse_heroes(card_sets, selected_cards):
    card_sets.select_diverse_heroes(selected_cards)
    assert [v for v in selected_cards.heroes if v.is_cleric()]
    assert [v for v in selected_cards.heroes if v.is_fighter()]
    assert [v for v in selected_cards.heroes if v.is_rogue()]
    assert [v for v in selected_cards.heroes if v.is_wizard()]


def test_select_marketplace_cards(card_sets, selected_cards):
    card_sets.select_diverse_heroes(selected_cards)
    card_sets.select_marketplace_cards(selected_cards)
    assert len(selected_cards.market) == 8


def test_shuffle_and_sort__copied_cards_go_to_the_end(card_sets: CardSets):
    copy1 = card_sets.all_marketplace[0].copy()
    card_sets._shuffle_and_sort(card_sets.all_marketplace)
    assert card_sets.all_marketplace[0] != copy1
    assert card_sets.all_marketplace[-1] == copy1

    # Now copy another card twice. Having more copies, this should
    # now be the final card, and the single copy card being the
    # penultimate card.
    copy2 = card_sets.all_marketplace[0].copy()
    card_sets.all_marketplace[0].copy()
    card_sets._shuffle_and_sort(card_sets.all_marketplace)
    assert card_sets.all_marketplace[-1] == copy2
    assert card_sets.all_marketplace[-2] == copy1
