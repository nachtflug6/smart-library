from enum import Enum


class RelationshipType(str, Enum):
    # --- Ownership / containment ---
    BELONGS_TO = "belongs_to"          # child → document
    PART_OF = "part_of"                # generic containment

    # --- Structural / semantic ---
    UNDER_HEADING = "under_heading"    # text → heading
    FOLLOWS = "follows"                # heading → heading OR text → text
    PRECEDES = "precedes"              # inverse of follows

    # --- Layout ---
    APPEARS_ON = "appears_on"          # text → page

    # --- Reference / semantics ---
    REFERENCES = "references"          # text → text / term / document
    MENTIONS = "mentions"              # text → term

    # --- Provenance / derivation ---
    DERIVED_FROM = "derived_from"      # entity → entity
