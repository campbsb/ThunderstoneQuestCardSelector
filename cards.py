import os
import random
from dataclasses import dataclass, field
from typing import Dict, List

import yaml

class Card():
    name: str
    keywords: List[str]
    combos: List[str] = field(default_factory=list)
    matches = 0

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return (self.name < other.name)

    def __gt__(self, other):
        return (self.name > other.name)

    def __eq__(self, other):
        return (self.name == other.name)

    def __init__(self, data: Dict):
        self.name = data.get("Name")
        self.keywords = data.get("Keywords", [])
        self.combos = data.get("Combo", [])

    def is_cleric(self) -> bool:
        return "Cleric" in self.keywords

    def is_fighter(self) -> bool:
        return "Fighter" in self.keywords

    def is_rogue(self) -> bool:
        return "Rogue" in self.keywords

    def is_wizard(self) -> bool:
        return "Wizard" in self.keywords

class CardSets():

    def __init__(self, debug=False):
        self.debug = debug
        self.all_heroes: List[Card] = []
        self.all_marketplace: List[Card] = []
        self.selected_heroes: List[Card] = []
        self.selected_marketplace_cards: List[Card] = []
        self.marketplace_slots = {
            "Item": {"Max": 2, "Used": 0},
            "Spell": {"Max": 2, "Used": 0},
            "Weapon": {"Max": 2, "Used": 0},
            "ANY": {"Max": 2, "Used": 0},
        }

    def import_set(self, data: Dict):
        for card in data["Heroes"]:
            self.all_heroes.append(Card(card))

        for card in data["Marketplace"]:
            self.all_marketplace.append(Card(card))

    def select_diverse_heroes(self) -> List[Card]:
        self.selected_heroes = []
        all_classes = set(['Cleric', 'Fighter', 'Rogue', 'Wizard'])
        required_classes = all_classes.copy()
        heroes = self.all_heroes.copy()
        random.shuffle(heroes)
        for hero in heroes:
            found_required = False if required_classes else True
            for hero_class in all_classes:
                if hero_class in hero.keywords and hero_class in required_classes:
                    found_required = True
                    required_classes.remove(hero_class)

            if found_required:
                self.selected_heroes.append(hero)

            if len(self.selected_heroes) == 4:
                self.selected_heroes.sort()
                return self.selected_heroes

        raise ValueError("Failed to find 4 appropriate heroes!")

    def select_marketplace_cards(self) -> List[Card]:
        if not self.selected_heroes:
            raise Exception("You must select heroes first!")

        random.shuffle(self.all_marketplace)

        for match_count in [1, 2]:
            self._select_cards_matching_heroes(match_count)

        self._select_remaining_cards()
        self._validate_selected_cards()

        for hero in self.selected_heroes:
            self._debug_msg(f"Hero {hero.name} has {hero.matches} combo matches")

        self.selected_marketplace_cards.sort()
        return self.selected_marketplace_cards

    def _select_remaining_cards(self) -> None:
        for card in self.all_marketplace:
            if self._can_slot(card) and card not in self.selected_marketplace_cards:
                self._add_marketplace_card_to_selection(card)

    def _add_marketplace_card_to_selection(self, card):
        self._increment_matches(self.selected_heroes, card)
        self._increment_card_counts(card)
        self.selected_marketplace_cards.append(card)

    def _select_cards_matching_heroes(self, match_count):
        for hero in self.selected_heroes:
            if hero.matches >= match_count:
                continue

            for card in self.all_marketplace:
                if card in self.selected_marketplace_cards or not self._can_slot(card):
                    continue

                if self.is_combo(hero, card):
                    self._add_marketplace_card_to_selection(card)
                    break

    def _can_slot(self, card) -> bool:
        if self.marketplace_slots["ANY"]["Used"] < self.marketplace_slots["ANY"]["Max"]:
            return True

        # All the Any slots are used up...
        for keyword in self.marketplace_slots.keys():
            if keyword in card.keywords:
                if self.marketplace_slots[keyword]["Used"] < self.marketplace_slots[keyword]["Max"]:
                    return True

        return False

    def is_combo(self, hero: Card, card: Card) -> bool:
        for keyword in hero.combos:
            if keyword in card.keywords:
                return True

        for keyword in card.combos:
            if keyword in hero.keywords:
                return True

        return False

    def _increment_matches(self, heroes: List[Card], card: Card) -> None:
        for hero in heroes:
            if self.is_combo(hero, card):
                hero.matches += 1

    def _increment_card_counts(self, card):
        # All the Any slots are used up...
        for keyword in self.marketplace_slots.keys():
            if keyword in card.keywords:
                if self.marketplace_slots[keyword]["Used"] < self.marketplace_slots[keyword]["Max"]:
                    self.marketplace_slots[keyword]["Used"] += 1
                else:
                    self.marketplace_slots["ANY"]["Used"] += 1
                return

        raise Exception(f"Failed to find marketplace keyword for card {card.name}")

    def _debug_msg(self, message: str) -> None:
        if self.debug:
            print(message)

    def _validate_selected_cards(self):
        if len(self.selected_marketplace_cards) != 8:
            raise Exception(f"We should have 8 cards, but have {len(self.selected_marketplace_cards)} - {repr(self.selected_marketplace_cards)}!")

        for keyword in self.marketplace_slots.keys():
            if self.marketplace_slots[keyword]["Used"] != self.marketplace_slots[keyword]["Max"]:
                raise Exception(f"We have {self.marketplace_slots[keyword]["Used"]} {keyword} cards, and not {self.marketplace_slots[keyword]["Max"]}!")

class Cards():
    def card_sets(self) -> Dict:
        resource_dir = os.path.dirname(__file__) + "/Resources"
        with open(f"{resource_dir}/cards.yaml") as fh:
            return yaml.safe_load(fh)

    def quest_number_and_name_list(self) -> list:
        return [self.set_name(v) for v in self.card_sets()]

    def set_name(self, card_set):
        quest_name = card_set["Quest"]
        if "Number" in card_set:
            quest_name = f"{card_set["Number"]} {card_set["Quest"]}"
        return quest_name

    def get_selected_card_sets(self, selected_quests, debug=False) -> CardSets:
        card_sets = CardSets(debug=debug)
        for card_set_data in self.card_sets():
            if self.set_name(card_set_data) in selected_quests:
                card_sets.import_set(card_set_data)

        return card_sets
