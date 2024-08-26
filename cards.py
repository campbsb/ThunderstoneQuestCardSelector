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

    def __init__(self, data: Dict):
        self.name = data.get("Name")
        self.keywords = data.get("Keywords", [])
        self.combos = data.get("Combos", [])

    def is_cleric(self) -> bool:
        return "Cleric" in self.keywords

    def is_fighter(self) -> bool:
        return "Fighter" in self.keywords

    def is_rogue(self) -> bool:
        return "Rogue" in self.keywords

    def is_wizard(self) -> bool:
        return "Wizard" in self.keywords

class CardSets():
    heroes: List[Card]
    marketplace: List[Card]

    def __init__(self):
        self.heroes = []
        self.marketplace = []

    def import_set(self, data: Dict):
        for card in data["Heroes"]:
            self.heroes.append(Card(card))

    def select_diverse_heroes(self) -> List[Card]:
        heroes_to_return = []
        required_classes = set('Cleric', 'Fighter', 'Rogue', 'Wizard')
        heroes = self.heroes.copy()
        random.shuffle(heroes)
        for hero in heroes:
            found_required = False if required_classes else True
            for hero_class in required_classes:
                if hero_class in hero.keywords:
                    found_required = True
                    required_classes.remove(hero_class)
                else:
                    print(f"Failed to find {hero_class} in {hero}")

            if found_required:
                print(f"Found hero {hero}")
                heroes_to_return.append(hero)

            if len(heroes_to_return) == 4:
                return heroes_to_return

        raise ValueError("Failed to find 4 appropriate heroes!")


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

    def get_selected_card_sets(self, selected_quests) -> CardSets:
        card_sets = CardSets()
        for card_set_data in self.card_sets():
            if self.set_name(card_set_data) in selected_quests:
                card_sets.import_set(card_set_data)

        return card_sets
