import re

############################
# Utils
############################
def to_caps_string(str):
    str = str.upper()  # Upper case

    # Replace
    str = str.replace("...", "_")  # Replace ellipsis

    # Remove
    str = str.replace("'", "")  # Remove apostraphes
    str = str.replace(".", "")  # Remove periods
    str = str.replace("/", "")  # Remove forward slashes

    # Clean
    # Turn all other non-alphanumerics into underscores
    str = re.sub("[^0-9a-zA-Z]+", "_", str)
    str = str.lstrip("_")  # Strip leading underscores
    str = str.rstrip("_")  # Strip trailing underscores
    str = str.strip()  # Strip any leading or trailing whitespace

    return str

# https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-1.php
def int_to_roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def sanitize_zone_name(name):
    name = name.replace(' ', '_')
    name = name.replace('\'', '')
    name = name.replace('#', '')
    name = name.replace('_-_', '-')
    name = name.replace("[U]", "U")
    name = name.replace("-LegionA", "-Legion_A")
    name = name.replace("-LegionB", "-Legion_B")
    name = name.replace("Escha-", "Escha_")
    name = name.replace("Desuetia-Empyreal", "Desuetia_Empyreal")
    return name
