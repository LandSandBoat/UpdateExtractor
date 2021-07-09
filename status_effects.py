import xmltodict
import xml.etree.ElementTree as ET
from utils import *

############################
# Status Effects
############################
def status_effects():
    print("Generating out/scripts/globals/status_effects.lua")
    status_effects = {}
    status_effects_count = {}  # for tracking BOOST vs BOOST_II etc.
    status_effects_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/status-names.xml").getroot(), encoding="unicode"))
    longest_status_str = 0
    for status_effect in status_effects_xml['thing-list']['thing']:
        try:
            index = int(status_effect['field'][0]['#text'])
            name = status_effect['field'][1]['#text']

            longest_status_str = max(longest_status_str, len(name))
            caps_name = to_caps_string(name)

            # Exceptions and removals
            if index >= 24 and index <= 27:  # ST
                continue
            if index >= 224 and index <= 226:  # ST
                continue
            if index >= 372 and index <= 374:  # I, II, III
                continue

            # Renames
            if (index >= 539 and index <= 567) or index == 580:
                caps_name = "GEO_" + caps_name
            if caps_name == "CRITICAL_HIT_EVASION_DOWN":
                caps_name = "CRIT_HIT_EVASION_DOWN"

            if not caps_name in status_effects_count:
                status_effects_count[caps_name] = 1
            elif caps_name == "NONE":
                status_effects[index] = caps_name
            else:
                count = status_effects_count[caps_name]
                next_count = count + 1
                status_effects_count[caps_name] = next_count

                roman_count = int_to_roman(next_count)
                caps_name = f"{caps_name}_{roman_count}"

            status_effects[index] = caps_name
        except:
            pass

    # Swap ENCUMBRANCE_I and ENCUMBRANCE_II
    status_effects[177] = "ENCUMBRANCE_II"
    status_effects[259] = "ENCUMBRANCE_I"

    # Go back and upgrade anything with tiers to have a numeral _I after the first entry
    for key, value in status_effects.items():
        count = status_effects_count.get(value, None)
        if count is not None:
            if count > 1:
                # Exceptions
                if value == "HASTE":
                    continue
                if value == "BOOST":
                    continue
                if key >= 80 and key <= 86:
                    continue
                if value == "COSTUME":
                    continue
                if key >= 178 and key <= 185:
                    continue
                if value == "FLURRY":
                    continue
                if value == "FINISHING_MOVE":
                    continue

                status_effects[key] = f"{value}_I"

    with open("out/scripts/globals/status_effects.lua", "w") as file:
        file.write(
            "-- For copy/pasting into the start of xi.effects in globals/status.lua\n")
        none_count = 0
        for key, value in status_effects.items():
            cleaned_status = to_caps_string(value)
            if value == "NONE":
                if none_count > 0:
                    status_str = f"    -- {cleaned_status.ljust(longest_status_str - 1)}"
                else:
                    status_str = f"    {cleaned_status.ljust(longest_status_str - 1)}"
                none_count = none_count + 1
            else:
                status_str = f"    {cleaned_status.ljust(longest_status_str - 1)}"

            file.write(f"{status_str} = {key},\n")
