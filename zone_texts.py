import xmltodict
import xml.etree.ElementTree as ET
import glob
import os
from config import *
from utils import *

############################
# Zone Text IDs
############################
def lines_that_contains(string, substring):
    return [line for line in string.split('\n') if substring in line]

def get_max_str(lst):
    return max(lst, key=len)

def sanitize_string(str):
    # Strange unicode non-angle brackets
    str = str.replace("≺", "<")
    str = str.replace("≻", ">")

    # Substitutions 1
    str = str.replace("<Numeric Parameter 0>", "<number>")
    str = str.replace("<Numeric Parameter 1>", "<number>")
    str = str.replace("<Numeric Parameter 2>", "<number>")
    str = str.replace("<Numeric Parameter 3>", "<number>")
    str = str.replace("<Possible Special Code: 01>", "<item>")

    # Removals
    str = str.replace("<Prompt>", "")
    str = str.replace("<BAD CHAR: 80>.", ". ")
    str = str.replace("<BAD CHAR: 8280>", "")
    str = str.replace("<BAD CHAR: 80>", "")
    str = str.replace("<Possible Special Code: 00>", "")
    str = str.replace("<Possible Special Code: 05>#", "")
    str = str.replace("<Possible Special Code: 05>%", "")
    str = str.replace("<Possible Special Code: 1F>y", "")
    str = str.replace("<Possible Special Code: 1F>", "")
    str = str.replace("<Unknown Parameter (Type: 80) 1>", "")
    str = str.replace("<Singular/Plural Choice (Parameter 0)>", "")
    str = str.replace("<Singular/Plural Choice (Parameter 1)>", "")
    str = str.replace("<Multiple Choice (Parameter 1)>", "")
    str = str.replace("<Multiple Choice (Parameter 33)>", "")
    str = str.replace("<Unknown Parameter (Type: 34) 1>", "")
    str = str.replace("<Possible Special Code: 05>$", "")
    str = str.replace("<Possible Special Code: 05>8", "")

    # Substitutions 2
    str = str.replace("<item><Possible Special Code: 05>3", "<keyitem>")
    str = str.replace("<item><item><item>", "<item>")

    # ASCII-ify
    str = str.encode("ascii", "ignore").decode()

    # Tidy
    str = str.replace('\n', '')
    str = str.strip()

    # Fix-ups
    # TODO: Replace with regex: 2 chars on each side of a period
    str = str.replace("<number> points!You", "<number> points! You")
    str = str.replace("<item>. ..Davoi", "<item>...Davoi")
    str = str.replace("You retrieve <item>  from the porter moogle's care.", "You retrieve <item> from the porter moogle's care.")
    str = str.replace("<item><Player Name>!Objective:", "<assault>! Objective:")

    return str

def sanitize_zone_name(name):
    name = name.replace(' ', '_')
    name = name.replace('\'', '')
    name = name.replace('#', '')
    name = name.replace('_-_', '-')
    name = name.replace("[U]", "U")
    name = name.replace("-LegionA", "-Legion_A")
    name = name.replace("-LegionB", "-Legion_B")
    name = name.replace("[P1]", "P1")
    name = name.replace("[P2]", "P2")
    name = name.replace("Escha-", "Escha_")
    name = name.replace("Desuetia-Empyreal", "Desuetia_Empyreal")
    return name

def zone_texts():
    areas = {}
    tree = ET.parse('res/area-names.xml')
    areas_xml = xmltodict.parse(ET.tostring(tree.getroot(), encoding='unicode'))
    for area in areas_xml['thing-list']['thing']:
        try:
            index = int(area['field'][0]['#text'])
            name = area['field'][1]['#text']
            name = sanitize_zone_name(name)

            # Make folders
            if not os.path.exists('out/scripts/zones/' + name):
                os.makedirs('out/scripts/zones/' + name)
        except:
            pass
        areas[index] = name

    dialog_table_list = glob.glob('res/dialog-table-*.xml')
    for item in dialog_table_list:
        with open(item, 'r', encoding='utf-8') as file:
            zone_num_str = item.replace('res\dialog-table-', '')
            zone_num_str = zone_num_str.replace('.xml', '')

            # TODO: Handle zone 50-2
            if zone_num_str == "50-2":
                print("SKIPPING AHT URGHAN WHITEGATE PART 2!")
                continue

            zone_num = int(zone_num_str)
            zone_name = areas[zone_num]

            if zone_name == "unknown" or zone_name == "none":
                continue

            # Parse as XML
            data = file.read()
            zone_tree = ET.fromstring(data)

            # Prepare filenames
            output_filename = 'out/scripts/zones/' + zone_name + "/Text.lua"
            raw_output_filename = output_filename + ".raw"
            server_filename = SERVER_DIR + "/scripts/zones/" + zone_name + "/IDs.lua"

            print(f"Generating {output_filename} ({zone_num})")
            with open(output_filename, 'w') as out_file, open(raw_output_filename, 'w') as raw_file, open(server_filename, 'r') as in_file:
                server_data = in_file.read()
                output_list = []
                max_enum_length = 0
                duplicate_enums = {} # Track duplicate enums
                for entry in zone_tree:
                    # Index: The number
                    index = str(entry[0].text.strip())

                    # Comment: After the number
                    comment_text = sanitize_string(entry[1].text)
                    raw_file.write(f"{index} : {comment_text}\n")

                    # Block some junk
                    if comment_text == '<number>':
                        continue
                    if comment_text == '<item>':
                        continue
                    if len(comment_text) <= 3:
                        continue

                    # Enum: Called and indexed by Lua function
                    # If comment text exists in the server IDs file
                    lines = lines_that_contains(server_data, comment_text)
                    if len(lines) > 0:
                        # Match on the longest line in lines, to try for a better match
                        longest_line = get_max_str(lines)
                        enum_text = longest_line.split("=")[0].strip() # Collect the enum name

                        # Try and de-dupe enum keys
                        count = duplicate_enums.get(enum_text, None)
                        if count is not None:
                            duplicate_enums[enum_text] = count + 1
                        else:
                            duplicate_enums[enum_text] = 1

                        if duplicate_enums[enum_text] > 1:
                            enum_text = f"{enum_text}_{duplicate_enums[enum_text]}"

                        # Add to output list
                        output_list.append([enum_text, index, comment_text])
                        max_enum_length = max(max_enum_length, len(enum_text)) # For formatting later

                # Write output file
                out_file.write("text =\n{\n")
                for entry in output_list:
                    enum_text = f"    {entry[0].ljust(max_enum_length)}"
                    out_file.write(f"{enum_text} = {entry[1]}, -- {entry[2]}\n")
                out_file.write("}\n")
