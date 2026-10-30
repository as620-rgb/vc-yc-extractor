"""read_directory: a page of cards from the snapshot."""

import re

from .checks import result

MAX_LIMIT = 20
BATCH = re.compile(r"(Winter|Summer) \d{4}")


def verify_input(value):
    if value.offset < 0:
        return result(False, "offset must be 0 or more")
    if not 1 <= value.limit <= MAX_LIMIT:
        return result(False, f"limit must be 1 to {MAX_LIMIT}")
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    cards = output_value.cards
    expected = max(0, min(input_value.limit, output_value.total - input_value.offset))
    if output_value.offset != input_value.offset or len(cards) != expected:
        return result(False, f"expected {expected} cards from offset {input_value.offset}, got {len(cards)}")
    positions = [card.position for card in cards]
    if positions != list(range(input_value.offset, input_value.offset + len(cards))):
        return result(False, f"card positions are not consecutive from the offset: {positions}")
    for card in cards:
        if not card.slug or not card.name or not card.pills or not BATCH.fullmatch(card.pills[0]):
            return result(False, f"card {card.position} lacks a slug, a name or a leading batch pill")
    return result(True, f"{len(cards)} cards read")
