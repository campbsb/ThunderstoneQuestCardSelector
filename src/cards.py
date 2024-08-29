from dataclasses import dataclass, field
import os
import random
from typing import Dict, List
import yaml

class Card():

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
        self.level = data.get("Level", 0)
        self.matches = 0
        self.copies_taken = 0

    def copy(self):
        self.copies_taken += 1
        return Card({
            "Name": self.name,
            "Keywords": self.keywords,
            "Combo": self.combos,
            "Level": self.level,
        })

    __copy__ = copy

    def is_cleric(self) -> bool:
        return "Cleric" in self.keywords

    def is_fighter(self) -> bool:
        return "Fighter" in self.keywords

    def is_rogue(self) -> bool:
        return "Rogue" in self.keywords

    def is_wizard(self) -> bool:
        return "Wizard" in self.keywords

    def combos_with(self, card) -> bool:
        """ Return true if this card works well in combination with the specified card """
        for keyword in self.combos:
            if keyword in card.keywords:
                return True

        for keyword in card.combos:
            if keyword in self.keywords:
                return True

        return False

class InsufficientCardsError(Exception):
    """ Raised should we fail to find 4 heroes, 8 marketplace cards, or 3 monsters.
    Don't really care so much about rooms or guardian.
    """
    pass


@dataclass
class SelectedCards():
    """ Class to store selected cards.
    Market cards should be added with add_marketplace_card method, monsters with add_monster.
    Others directly added/set.
    """
    guardian: str = ""
    heroes: List[Card] = field(default_factory=list)
    market: List[Card] = field(default_factory=list)
    monsters: List[Card] = field(default_factory=list)
    rooms: List[Card] = field(default_factory=list)

    @property
    def heroes_csv(self):
        return ", ".join([i.name for i in self.heroes])

    @property
    def market_csv(self):
        return ", ".join([i.name for i in self.market])

    @property
    def monsters_csv(self):
        return ", ".join([i.name for i in self.monsters])

    @property
    def rooms_csv(self):
        return ", ".join([i.name for i in self.rooms])

    @property
    def combo_match_count(self):
        return sum([i.matches for i in self.heroes])

    def __post_init__(self):
        self.marketplace_slots = {
            "Item": {"Max": 2, "Used": 0},
            "Spell": {"Max": 2, "Used": 0},
            "Weapon": {"Max": 2, "Used": 0},
            "ANY": {"Max": 2, "Used": 0},
        }

    def can_slot_market_card(self, card: Card) -> bool:
        """ Check to see if we can slot the given marketplace card.
        It must be a new card, and we must either have an 'ANY' slot
        free, or the slot for the card type (Weapon/Item/Spell)"""
        if card in self.market:
            return False

        if self.marketplace_slots["ANY"]["Used"] < self.marketplace_slots["ANY"]["Max"]:
            return True

        for keyword in self.marketplace_slots.keys():
            if keyword in card.keywords:
                if self.marketplace_slots[keyword]["Used"] < self.marketplace_slots[keyword]["Max"]:
                    return True

        return False

    def can_slot_room(self, room: Card) -> bool:
        """ Check to see if we can slot the given dungeon room card
        Return false if we've already got it, or if we already have 2 rooms of the same level.
        """
        room_count = sum(1 for i in self.rooms if i.level == room.level)
        return (room_count < 2 and room not in self.rooms)

    def can_slot_monster(self, monster: Card) -> bool:
        """ Check to see if we can slot the given monster card
        Return false if we've already got it, or if we already have a monster of the same level.
        """
        monster_count = sum(1 for i in self.monsters if i.level == monster.level)
        return (monster_count == 0 and monster not in self.monsters)

    def add_marketplace_card(self, card: Card) -> None:
        self._increment_hero_matches(card)
        self._increment_market_slot_counts(card)
        self.market.append(card)
        self.market.sort()

    def _increment_hero_matches(self, card: Card) -> None:
        for hero in self.heroes:
            if hero.combos_with(card):
                hero.matches += 1

    def _increment_market_slot_counts(self, card) -> None:
        for keyword in self.marketplace_slots.keys():
            if keyword in card.keywords:
                if self.marketplace_slots[keyword]["Used"] < self.marketplace_slots[keyword]["Max"]:
                    self.marketplace_slots[keyword]["Used"] += 1
                else:
                    self.marketplace_slots["ANY"]["Used"] += 1
                return

        # Could be an Ally. Must use up 'ANY' slot.
        self.marketplace_slots["ANY"]["Used"] += 1

    def validate_selected_cards(self) -> None:
        """Check our selection of cards.
        We want 8 marketplace cards of appropriate sorts, 4 heroes, and
        3 monsters. Don't care so much about rooms or the guardian.
        :raises InsufficientCardsError: If we detect an error.
        """
        for check_name, check_list, required in (
                ("market", self.market, 8), ("hero", self.heroes, 4), ("monster", self.monsters, 3)
        ):
            if len(check_list) != required:
                raise InsufficientCardsError(f"We should have {required} {check_name} cards, but have {len(check_list)} - {repr(check_list)}!")

        for keyword in self.marketplace_slots.keys():
            if self.marketplace_slots[keyword]["Used"] != self.marketplace_slots[keyword]["Max"]:
                raise InsufficientCardsError(f"We have {self.marketplace_slots[keyword]["Used"]} {keyword} cards, and not {self.marketplace_slots[keyword]["Max"]}!")

        monster_levels = sum([v.level for v in self.monsters])
        if monster_levels != 6:
            raise InsufficientCardsError(f"Failed to select level 1, 2, and 3 monsters! Selected: {repr(self.monsters)}")

    def add_monster(self, monster: Card):
        self._increment_hero_matches(monster)
        self.monsters.append(monster)
        self.monsters.sort()


class CardSets():
    ALL_CLASSES = {'Cleric', 'Fighter', 'Rogue', 'Wizard'}

    def __init__(self, debug=False):
        self.debug = debug
        self.all_heroes: List[Card] = []
        self.all_marketplace: List[Card] = []
        self.guardians: List[Card] = []
        self.monsters: List[Card] = []
        self.rooms: List[Card] = []

    def import_set(self, data: Dict):
        for card in data.get("Heroes", []):
            self.all_heroes.append(Card(card))

        for card in data.get("Marketplace", []):
            self.all_marketplace.append(Card(card))

        for card in data.get("Guardians", []):
            self.guardians.append(Card(card))

        for card in data.get("Dungeon Rooms", []):
            self.rooms.append(Card(card))

        for card in data.get("Monsters", []):
            self.monsters.append(Card(card))

        self._debug_msg(f"Imported {data.get("Quest", "Unknown")}, total market: {len(self.all_marketplace)}")

    def _shuffle_and_sort(self, cards: List[Card]):
        """ Shuffle the cards in the list, then sort them such that previously used cards go to the end """
        random.shuffle(cards)
        cards.sort(key=lambda c: c.copies_taken)

    def select_cards(self, diverse_heroes=True, combos_per_hero=1) -> SelectedCards:
        if not self.all_heroes:
            raise InsufficientCardsError("We don't have any heroes to select from. Have you selected at least one Quest?")

        selected_cards = SelectedCards()
        self.select_diverse_heroes(selected_cards)
        self.select_marketplace_cards(selected_cards, combos_per_hero=combos_per_hero)
        self.select_guardian(selected_cards)
        self.select_rooms(selected_cards)
        self.select_monsters(selected_cards, combos_per_hero=combos_per_hero)
        selected_cards.validate_selected_cards()
        return selected_cards

    def select_diverse_heroes(self, selected: SelectedCards) -> None:
        return self.select_heroes(selected, self.ALL_CLASSES)

    def select_random_heroes(self, selected: SelectedCards) -> None:
        return self.select_heroes(selected, set())

    def select_heroes(self, selected: SelectedCards, required_classes: set) -> None:
        required_classes = required_classes.copy()
        self._shuffle_and_sort(self.all_heroes)
        for hero in self.all_heroes:
            if not required_classes:
                break

            found_required = False
            for hero_class in self.ALL_CLASSES:
                if hero_class in hero.keywords and hero_class in required_classes:
                    found_required = True
                    required_classes.remove(hero_class)

            if found_required:
                selected.heroes.append(hero.copy())

        # Got all required classes. Now fill up in case we had some dual class
        for hero in self.all_heroes:
            if len(selected.heroes) == 4:
                selected.heroes.sort()
                self._debug_msg("Selected 4 heroes")
                return

            if hero not in selected.heroes:
                selected.heroes.append(hero.copy())

        raise InsufficientCardsError(f"Failed to find 4 appropriate heroes! Missing {", ".join(required_classes)}")

    def select_marketplace_cards(self, selected: SelectedCards, combos_per_hero=1) -> None:
        self._shuffle_and_sort(self.all_marketplace)
        self._debug_msg(f"Selecting from Marketplace of length {len(self.all_marketplace)}")

        for match_count in range(combos_per_hero):
            self._select_cards_matching_heroes(selected, match_count)

        self._select_remaining_cards(selected)
        for hero in selected.heroes:
            self._debug_msg(f"Hero {hero.name} has {hero.matches} combo matches")

    def _select_remaining_cards(self, selected: SelectedCards) -> None:
        for card in self.all_marketplace:
            if selected.can_slot_market_card(card):
                selected.add_marketplace_card(card.copy())

    def _select_cards_matching_heroes(self, selected: SelectedCards, match_count: int):
        for hero in selected.heroes:
            if hero.matches >= match_count:
                continue

            for card in self.all_marketplace:
                if selected.can_slot_market_card(card) and hero.combos_with(card):
                    selected.add_marketplace_card(card.copy())
                    break

    def select_guardian(self, selected: SelectedCards) -> None:
        """ Set a random guardian in the SelectedCards object """
        if self.guardians:
            self._shuffle_and_sort(self.guardians)
            selected.guardian = self.guardians[0].copy()
        else:
            self._debug_msg("No guardians to select from!")

    def select_rooms(self, selected: SelectedCards) -> None:
        """ Set random rooms in the SelectedCards object """
        self._shuffle_and_sort(self.rooms)
        for room in self.rooms:
            if selected.can_slot_room(room):
                selected.rooms.append(room.copy())
                if len(selected.rooms) > 5:
                    return

    def select_monsters(self, selected: SelectedCards, combos_per_hero=1) -> None:
        """ Set random monsters in the SelectedCards object """
        self._shuffle_and_sort(self.monsters)

        # Go for matches first...
        if combos_per_hero:
            for hero in selected.heroes:
                for monster in self.monsters:
                    if hero.combos_with(monster) and selected.can_slot_monster(monster):
                        selected.add_monster(monster.copy())
                        break

        # Now fill up...
        for monster in self.monsters:
            if len(selected.monsters) > 2:
                break
            if selected.can_slot_monster(monster):
                selected.add_monster(monster.copy())

    def _debug_msg(self, message: str) -> None:
        if self.debug:
            print(message)


class Cards():
    def card_sets(self) -> Dict:
        resource_dir = os.path.dirname(__file__) + "/resources"
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
