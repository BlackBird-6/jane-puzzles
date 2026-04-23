# Scan found words for CAN-related and DIGIT-related words

# CAN-related: things that are cans, come in cans, types of cans, 
# can materials, can brands, etc.
CAN_RELATED = {
    # Direct synonyms / types of cans
    "TIN", "CANISTER", "CONTAINER", "CANNISTER", "CANTEEN",
    "AEROSOL", "VESSEL", "RECEPTACLE", "CYLINDER",
    # Things that come in cans / can-words
    "SODA", "BEER", "SOUP", "TUNA", "SPAM", "BEANS", "CORN",
    "PAINT", "SPRAY", "VARNISH", "LACQUER", "PRIMER",
    "COLA", "PEPSI", "COKE", "FANTA",
    # Can materials
    "ALUMINUM", "ALUMINIUM", "STEEL", "METAL",
    # Can parts
    "LID", "TAB", "RING", "PULL", "SEAL", "LABEL",
    # Can actions  
    "OPEN", "OPENER", "PRESERVE", "PRESERVED", "CANNED", "CANNING",
    # Can-adjacent
    "JAR", "BOTTLE", "JUG", "FLASK", "PAIL", "BUCKET",
    "GARBAGE", "TRASH", "RUBBISH", "DUSTBIN", "WASTEBASKET",
    # Misc
    "CANNERY", "CANAPE", "CANAL", "CANARY", "CANCEL", "CANCER",
    "CANDID", "CANDLE", "CANDY", "CANE", "CANINE", "CANNON",
    "CANOE", "CANON", "CANOPY", "CANT", "CANTO", "CANTON",
    "CANVAS", "CANYON", "PELICAN", "TOUCAN", "PECAN", "CANTOR",
    "CANDOR", "CANDIDATE", "CANDELABRA", "CANTALOUPE",
    "CANTATA", "CANTEEN", "CANTER", "CANTINA", "CANTANKEROUS",
    "CANTICLE", "CANTILEVER", "SCAN", "SCANT", "SCANDAL",
    # WD-40, oil can, etc.
    "OIL", "GREASE", "LUBRICANT",
    "WATERING", "GASOLINE", "GAS", "FUEL",
    "SARDINE", "SARDINES", "ANCHOVY", "ANCHOVIES",
    "CONDENSED", "EVAPORATED",
    "PRINGLES",
    "CANUCK", "TOUCAN",
}

# DIGIT-related: things that are digits, types of digits, 
# digit synonyms, finger/toe related
DIGIT_RELATED = {
    # Numerical
    "BINARY", "HEXADECIMAL", "DECIMAL", "OCTAL",
    "NUMBER", "NUMERAL", "INTEGER", "FIGURE",
    "BIT", "BYTE", "NIBBLE",
    # Body digits
    "FINGER", "THUMB", "INDEX", "MIDDLE", "RING", "PINKY", "PINKIE",
    "TOE", "HALLUX", "PHALANX", "PHALANGES",
    "HAND", "FOOT",
    # Digit-adjacent
    "NAIL", "KNUCKLE", "CUTICLE", "HANGNAIL",
    "FINGERPRINT", "FINGERTIP", "FINGERNAIL",
    "TOENAIL", "TOEHOLD",
    "DIGITAL", "DIGITIZE", "PRESTIDIGITATION",
    # Number words
    "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE",
    "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
    # Base/radix
    "BASE", "RADIX", "PLACE",
    "POINTER", "POINT",
}

with open('found words.txt', 'r', encoding='utf-8', errors='ignore') as f:
    found_words = [w.strip().upper() for w in f.readlines() if w.strip()]

print(f"Total found words: {len(found_words)}")
print()

# Method 1: exact match against known sets
print("=== EXACT MATCHES (CAN-related) ===")
can_exact = [w for w in found_words if w in CAN_RELATED]
for w in sorted(set(can_exact)):
    print(f"  {w}")

print()
print("=== EXACT MATCHES (DIGIT-related) ===")
digit_exact = [w for w in found_words if w in DIGIT_RELATED]
for w in sorted(set(digit_exact)):
    print(f"  {w}")

print()

# # Method 2: words containing "CAN" as substring
# print("=== WORDS CONTAINING 'CAN' ===")
# can_substr = [w for w in found_words if "CAN" in w]
# for w in sorted(set(can_substr)):
#     print(f"  {w}")

# print()

# Method 3: words containing "DIGIT" or "FINGER" or "THUMB" etc as substring
print("=== WORDS CONTAINING DIGIT-RELATED SUBSTRINGS ===")
digit_substrs = ["DIGIT", "FINGER", "THUMB", "PHAL", "KNUCK", "NAIL", "HEXADEC", "BINAR", "OCTAL"]
digit_substr = []
for w in found_words:
    for sub in digit_substrs:
        if sub in w:
            digit_substr.append(w)
            break
for w in sorted(set(digit_substr)):
    print(f"  {w}")

print()

# # Method 4: words containing "TIN" as substring (tin can)
# print("=== WORDS CONTAINING 'TIN' ===")
# tin_substr = sorted(set(w for w in found_words if "TIN" in w))
# for w in tin_substr:
#     print(f"  {w}")

# print()

# # Method 5: words starting with CAN
# print("=== WORDS STARTING WITH 'CAN' ===")
# can_start = sorted(set(w for w in found_words if w.startswith("CAN")))
# for w in can_start:
#     print(f"  {w}")
