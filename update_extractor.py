############################
#
# MIT License
#
# update_extractor.py
# Copyright (c) 2021 Zach Toogood
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
############################
#
# The following files from POLUtils should be in the directory next to this script
# when you run it (https://github.com/Windower/POLUtils):
# - MassExtractor.exe
# - PlayOnline.Core.dll
# - PlayOnline.FFXI.dll
#
############################

############################
# Python Imports
############################
import re
import xml.etree.ElementTree as ET
import os
import subprocess
import glob

############################
# pip Imports
############################
try:
    import xmltodict
except:
    print("Failed to import xmltodict, please install with `pip install xmltodict`")
    exit(-1)

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


############################
# Setup
############################
print("Looking for exes")
if not os.path.exists('./MassExtractor.exe') and not os.path.exists('./PlayOnline.Core.dll') and not os.path.exists('./PlayOnline.FFXI.dll'):
    print("Could not find one or all of: MassExtractor.exe, PlayOnline.Core.dll, PlayOnline.FFXI.dll")
    exit(-1)

print("Creating folder layout")
if not os.path.exists("out"):
    os.makedirs("out")

if not os.path.exists("out/conf"):
    os.makedirs("out/conf")

if not os.path.exists("out/conf/default"):
    os.makedirs("out/conf/default")

if not os.path.exists("out/scripts"):
    os.makedirs("out/scripts")

if not os.path.exists("out/scripts/globals"):
    os.makedirs("out/scripts/globals")

if not os.path.exists("out/scripts/zones"):
    os.makedirs("out/scripts/zones")

if not os.path.exists("out/sql"):
    os.makedirs("out/sql")

############################
# MassExtractor
############################
if not os.path.exists("res"):
    print("Running MassExtractor.exe -> ./res/")
    os.makedirs("res")
    subprocess.run(["MassExtractor.exe", "res"])
else:
    print("Did not need to run MassExtractor.exe")

############################
# Client Ver
############################
print("Fetching installed client version")
current_client_ver = ""
with open("""C:\Program Files (x86)\PlayOnline\SquareEnix\FINAL FANTASY XI\patch.cfg""", "r") as file:
    match_str = re.findall(r"\{(.*?)\}", file.read(),
                           re.MULTILINE | re.DOTALL)[0]
    split_list = re.split(" |/|\n", match_str)
    version_list = list(filter(lambda k: "_" in k, split_list))
    current_client_ver = version_list[-1]
    print(current_client_ver)

with open("out/conf/default/version.conf", "w") as file:
    file.write(f"CLIENT_VER: {current_client_ver}\n")

############################
# Titles
############################
print("Generating out/scripts/globals/titles.lua")
titles = {}
titles_xml = xmltodict.parse(ET.tostring(
    ET.parse("res/titles.xml").getroot(), encoding="unicode"))
longest_title_str = 0
for title in titles_xml['thing-list']['thing']:
    try:
        index = int(title['field'][0]['#text'])
        name = title['field'][1]['#text']
        longest_title_str = max(longest_title_str, len(name))
        if name != "0" and index != 0:
            titles[index] = name
    except:
        pass

with open("out/scripts/globals/titles.lua", "w") as file:
    file.write("xi.title =\n{\n")
    for key, value in titles.items():
        cleaned_title = to_caps_string(value)
        title_str = f"    {cleaned_title.ljust(longest_title_str - 1)}"
        index_str = str(int(key))
        utf8_comment = value.encode("utf-8")

        file.write(f"{title_str} = {index_str},\n")
        #file.write(f"{title_str} = {index_str}, -- {utf8_comment}\n")
    file.write("}\n")

############################
# Status Effects
############################
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

############################
# Items / Weapons / Armour etc.
############################

#     0 ->  4095 : items-general.xml
print("Generating out/sql/item_basic.sql")
item_basic = {}
item_basic_xml = xmltodict.parse(ET.tostring(
    ET.parse("res/items-general.xml").getroot(), encoding="unicode"))
for item in item_basic_xml['thing-list']['thing']:
    try:
        index = int(item['field'][0]['#text'])
        name = item['field'][6]['#text']
        #print(index, name)
    except:
        pass

#  4096 ->  8191 : items-usable.xml
#  8192 ->  8703 : items-puppet.xml
#  8704 -> 10239 : items-general2.xml
# 10240 -> 16383 : items-armor.xml
# 16384 -> 23039 : items-weapons.xml
# 23040 -> 28671 : items-armor2.xml
# 28672 -> 29695 : items-voucher-slip.xml
# 65535          : items-currency.xml

############################
# Zone Text IDs
############################
areas = {}
tree = ET.parse('res/area-names.xml')
areas_xml = xmltodict.parse(ET.tostring(tree.getroot(), encoding='unicode'))
for area in areas_xml['thing-list']['thing']:
    try:
        index = int(area['field'][0]['#text'])
        name = area['field'][1]['#text'].replace(' ', '_').replace(
            '\'', '').replace('#', '').replace('_-_', '-')

        # Make folders
        if not os.path.exists('out/scripts/zones/' + name):
            os.makedirs('out/scripts/zones/' + name)
    except:
        pass
    areas[index] = name

dialog_table_list = glob.glob('res/dialog-table-*.xml')
for item in dialog_table_list:
    with open(item, 'r', encoding='utf-8') as file:
        zone_num_str = item.replace(
            'res\dialog-table-', '').replace('.xml', '')
        zone_num = 0
        zone_name = ""
        if zone_num_str == "50-2":
            zone_num = 50
            zone_name = "Aht_Urhgan_Whitegate_2"
            if not os.path.exists('out/scripts/zones/' + zone_name):
                os.makedirs('out/scripts/zones/' + zone_name)
        else:
            zone_num = int(zone_num_str)
            zone_name = areas[zone_num]
        data = file.read()
        print(f"Generating Text.lua for {zone_name} ({zone_num})")

        # Strange unicode non-angle brackets
        data = re.sub(r'≺', '<', data)
        data = re.sub(r'≻', '>', data)

        # Substitutions
        data = re.sub(r'<(Numeric)[^>]*>', '[num]', data)
        data = re.sub(r'<Player Name>', '[player]', data)
        data = re.sub(r'<Possible Special Code: 01>', '[item]', data)
        data = re.sub(r'<Possible Special Code: 02>', '[player]', data)
        data = re.sub(r'<Possible Special Code: 03>', '[player]', data)
        data = re.sub(r'<Possible Special Code: 04>', '[player]', data)
        data = re.sub(r'<Possible Special Code: 05>.', '', data)

        # Removals
        data = re.sub(r'<Possible Special Code: 1F>.', '', data)
        data = re.sub(r'<Prompt>', '', data)
        data = re.sub(r'<Selection Dialog>', '', data)

        # Elements (this is bad, learn 2 regex)
        for element in ['Ice', 'Air', 'Earth', 'Thunder', 'Water', 'Light', 'Dark']:
            data = re.sub(r'<Element: ' + element + '>/*', element, data)

        # :(
        data = re.sub(r'Element: Ice>', '', data)
        data = re.sub(r'Element: Air>', '', data)
        data = data.replace('IceAirEarthThunderWaterLightDark', 'Element')
        data = data.replace('ThunderLightIceEarthWaterDark', '')
        data = data.replace('AirEarthThunderWaterLightDark', '')

        # Lists
        data = data.replace(
            'Fire/Ice/Wind/Earth/Thunder/Water/Light/Darkness', 'Element')
        data = data.replace(
            'Carbuncle/Fenrir/Ifrit/Titan/Leviathan/Garuda/Shiva/Ramuh/Diabolos', 'Avatar')

        # Multiple Choice
        # data = re.sub(r'\[[^\]]*]', '[...]', data)

        # Removable tags
        data = re.sub(
            r'<(Multiple|Unknown|BAD|Singular|Possible|Speaker|Set|Player|Item)[^>]*>', '', data)

        # Cleanup
        data = re.sub(r'\[/', '[', data)
        data = re.sub(r'\n</field>', '</field>', data)

        # ASCII-ify
        data = data.encode("ascii", "ignore").decode()

        # XML-ish output for debugging
        # with open('out/' + zone_name + ".text.xml", 'w') as out_file:
        #    out_file.write(data)

        # Parse as XML
        zone_tree = ET.fromstring(data)
        zone_tree_str_len = len(str(len(zone_tree)))

        with open('out/scripts/zones/' + zone_name + "/Text.lua", 'w') as out_file:
            out_file.write('local text =\n{\n')
            for entry in zone_tree:
                index = str(entry[0].text)
                text = str(entry[1].text).replace('\n', '')

                enum_text = text
                if len(text) >= 41:  # Remember the 4-space padding
                    enum_text = text[0:41]
                enum_text = enum_text.upper()
                enum_text = enum_text.replace(' ', '_')
                enum_text = re.sub(r'[^0-9a-zA-Z_]+', '', enum_text)

                part1 = '    ' + enum_text
                part2 = ' = ' + index + ','
                part3 = ' -- ' + text + '\n'

                out_file.write(part1.ljust(45) +
                               part2.ljust(4 + zone_tree_str_len) + part3)
            out_file.write('}\n')
            out_file.write('return text\n')

############################
# Entity IDs
############################

# Gather mob-list*.xml into a giant table of { id, name }.
# Go through and check that id and name still match what we have in SQL.
# If not, do a search/replace to try and update them

############################
# Misc
############################
