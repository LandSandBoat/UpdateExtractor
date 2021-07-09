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
    str = str.replace("\u227a", "<") # Less than
    str = str.replace("\u227b", ">") # More than
    str = str.replace("\uff41", "") # Wide a
    str = str.replace("\u03a9", "") # Omega

    # Substitutions 1
    str = re.sub(r"<Numeric Parameter [0-9A-F]+>", "<number>", str)
    #str = re.sub(r"<Player/Chocobo Parameter [0-9A-F]+>", "<player>", str)
    str = str.replace("<Possible Special Code: 01><Possible Special Code: 05>3", "<keyitem>")
    #str = str.replace("<Possible Special Code: 01><Possible Special Code: 05>6", "<item>")
    #str = str.replace("<Possible Special Code: 01><Possible Special Code: 05>8", "<item>")
    #str = str.replace("<Possible Special Code: 01><Possible Special Code: 05>#", "<item>")
    str = str.replace("<Unknown Parameter (Type: 80) 1><item>", "<keyitem>")

    str = str.replace("<Possible Special Code: 18><Possible Special Code: 01>", "<player>")
    str = str.replace("<Possible Special Code: 18><Possible Special Code: 02>", "<player>")
    str = str.replace("<Possible Special Code: 18><Possible Special Code: 03>", "<player>")
    str = str.replace("<Possible Special Code: 18><Possible Special Code: 04>", "<player>")
    str = str.replace("<Possible Special Code: 18><Possible Special Code: 05>", "<player>")
    str = str.replace("<Selection Dialog>", "")

    # Specific Removals
    str = str.replace("<Multiple Choice (Player Gender)>", "")
    str = str.replace("<Possible Special Code: 00>", "")
    str = str.replace("<Speaker Name>)", "")
    str = str.replace("<Possible Special Code: 1F>{", "")
    str = str.replace("<Possible Special Code: 1F>y", "")
    str = str.replace("<Possible Special Code: 1F>", "")
    str = str.replace("<Selection Dialog>", "")

    str = re.sub(r"<BAD CHAR: [0-9A-F]+>", "", str)
    str = re.sub(r"<Singular/Plural Choice \(Parameter [0-9A-F]+\)>", "", str)
    str = re.sub(r"<Multiple Choice \(Parameter [0-9A-F]+\)>", "", str)
    str = re.sub(r"<Unknown Parameter \(Type: [0-9A-F]+\) [0-9A-F]+>", "", str)

    # Substitutions 2
    #str = str.replace("<Possible Special Code: 05>8", "<item>")
    #str = str.replace("<Possible Special Code: 05>$", "<item>")
    #str = str.replace("<Possible Special Code: 05>#", "<item>")
    #str = str.replace("<Possible Special Code: 05>%", "<item>")
    #str = str.replace("<Possible Special Code: 05>6", "<item>")

    # Generic Removals
    str = str.replace("<Prompt>", "")
    #str = re.sub(r"<Possible Special Code: [0-9A-F]+>", "", str)

    # ASCII-ify
    str = str.encode("ascii", "ignore").decode()

    # Tidy
    str = str.replace('\n', '')
    str = str.strip()

    # Fix-ups
    # VOODOO: Replace "." with ". ", but only if its followed by 2 letters.
    str = re.sub(r"\.(?=[A-Za-z]{1})", ". ", str)
    str = re.sub(r"\!(?=[A-Za-z]{1})", "! ", str)
    str = re.sub(r"\?(?=[A-Za-z]{1})", "? ", str)

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
                        #longest_line = get_max_str(lines)
                        longest_line = lines[0]
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
