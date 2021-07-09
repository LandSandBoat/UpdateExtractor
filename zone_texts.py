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
    str = str.replace("<Singular/Plural Choice (Parameter 1)>", "")
    str = str.replace("<Multiple Choice (Parameter 1)>", "")
    str = str.replace("<Unknown Parameter (Type: 34) 1>", "")

    # Substitutions 2
    str = str.replace("<item><Possible Special Code: 05>3", "<keyitem>")

    # ASCII-ify
    str = str.encode("ascii", "ignore").decode()

    # Tidy
    str = str.replace('\n', '')
    str = str.strip()

    # Fix-ups
    str = str.replace("<number> points!You", "<number> points! You")
    str = str.replace("<item>. ..Davoi", "<item>...Davoi")

    return str

def zone_texts():
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
    lookup = {}
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

            if zone_name == "unknown" or zone_name == "none":
                continue

            # Parse as XML
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
                for entry in zone_tree:
                    # Index: The number
                    index = str(entry[0].text)

                    # Comment: After the number
                    comment_text = sanitize_string(entry[1].text)
                    raw_file.write(f"{index} : {comment_text}\n")

                    if comment_text == '<number>':
                        continue

                    if len(comment_text) <= 3:
                        continue

                    # Enum: Called and indexed by Lua function
                    # If the comment text is
                    lines = lines_that_contains(server_data, comment_text)

                    seen_enum_count = {}
                    if len(lines) > 0:
                        line = lines[0].split("=")[0]
                        enum_text = line.strip()
                        max_enum_length = max(max_enum_length, len(enum_text))
                        output_list.append([enum_text, index, comment_text])

                out_file.write("text =\n{\n")
                for entry in output_list:
                    enum_text = f"    {entry[0].ljust(max_enum_length)}"
                    out_file.write(f"{enum_text} = {entry[1]}, -- {entry[2]}\n")
                out_file.write("}\n")
