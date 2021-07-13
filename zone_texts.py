import xmltodict
import xml.etree.ElementTree as ET
import glob
import os
from config import *
from utils import *

############################
# Zone Text IDs
############################
def sanitize_pol_string(str):
    # Strange unicode non-angle brackets
    #str = str.replace("\u227a", "LT") # Less than
    #str = str.replace("\u227b", "GT") # Greater than
    #str = str.replace("\uff41", "WA") # Wide a
    #str = str.replace("\u03a9", "OM") # Omega

    # From Wren's regex
    #"/\n/"                                              => ' ',
    str = str.replace('\n', ' ')

    #"/".LT."Speaker Name".GT.")".WA."/U"               => '%',
    str = str.replace('\u227aSpeaker Name\u227b)\uff41', '%')

    #"/".LT."Possible Special Code: 1F".GT."[^".LT."]/U" => '',
    str = re.sub(r"\u227aPossible Special Code: 1F\u227b[^\u227a]", "", str)

    #"/".LT."/U"                                         => '~',
    str = str.replace('\u227a', '~')

    #"/".GT."/U"                                         => '~',
    str = str.replace('\u227b', '~')

    #"/".OM."/U"                                         => 'O',
    str = str.replace('\u03a9', 'O')

    #'/[^\x20-\x7E]/'                                    => '',
    str = re.sub(r"[^\x20-\x7E]", "", str) # Anything that isn't ASCII Space -> ASCII ~ (and all letters and nubmers in between)

    #"/~Numeric Parameter \d+~/U"                        => '#',
    str = re.sub(r"\~Numeric Parameter [0-9]+\~", "#", str)

    #"/~Possible Special Code: 05~[^~]+/U"               => '%',
    str = re.sub(r"\~Possible Special Code: 05\~[^\~]+", "%", str)

    #"/~Possible Special Code: 11~+/U"                   => '%',
    str = re.sub(r"\~Possible Special Code: 11\~+", "%", str)

    #"/~Possible Special Code: 01~\s~/U"                 => '~',
    str = re.sub(r"\~Possible Special Code: 01\~\s\~", "~", str)

    #"/~Possible Special Code: 01~~Player Name~/U"       => '%',
    str = re.sub(r"\~Possible Special Code: 01\~\~Player Name\~", "%", str)

    #"/~Player/Chocobo Parameter \d+~/U"                => '%',
    str = re.sub(r"\~Player/Chocobo Parameter [0-9]+\~", "%", str)

    #"/~Player Name~/U"                                  => '%',
    str = re.sub(r"\~Player Name\~", "%", str)

    #"/~Unknown Parameter (Type: A.) 0~/U"             => '#',
    str = re.sub(r"\~Unknown Parameter \(Type: A.*?\) 0\~", "#", str)

    #"/~.*~/U"                                           => '',
    str = re.sub(r"\~.*?\~", "", str)

    # Fix-ups
    # Trust messages
    str = str.replace("%Possible Special Code: 01Possible Special Code: 00~", "%!")

    # Tidy
    str = str.strip()

    return str

def sanitize_comment_string(str):
    # From Wren's regex
    #"<assault>"   => '%',
    str = str.replace("<assault>", "%")

    #"<item>"      => '%',
    str = str.replace("<item>", "%")

    #"<keyitem>"   => '%',
    str = str.replace("<keyitem>", "%")

    #"<name>"      => '%',
    str = str.replace("<name>", "%")

    #"<number>"    => '#',
    str = str.replace("<number>", "#")

    #"<space>"     => ' ',
    str = str.replace("<space>", " ")

    #"<timestamp>" => '#/#/# #:#:#'
    str = str.replace("<timestamp>", "#/#/# #:#:#")

    # Tidy
    str = str.strip()

    return str

def match_line(original_server_data, cleaned_comment_text):
    # Get all lines that contain the target comment text, and store the index too
    lines = []
    for index, item in enumerate(original_server_data):
        if "    mob =" in item:
            break
        cleaned_target_text = sanitize_comment_string(item)
        if cleaned_comment_text in cleaned_target_text:
            lines.append((index, cleaned_comment_text))

    # No results? Bail
    if len(lines) == 0:
        return None

    for entry in lines:
        index = entry[0]
        server_line = original_server_data[index]

        # Hack: We don't handle these debug lines very well
        if "--------" in server_line:
            continue

        # Hack: If the line doesn't have a comment to split on; bail
        split_line = server_line.split("-- ")
        if len(split_line) < 2:
            continue

        target_comment = sanitize_comment_string(split_line[1])
        if len(target_comment) == len(cleaned_comment_text):
            return index

    return None

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
    # Use area-names.xml to match zone names to zone numbers an create output folders
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

    # For each dialog table xml file
    handled_zones = []
    dialog_table_list = glob.glob('res/dialog-table-*.xml')
    for item in dialog_table_list:
        with open(item, 'r', encoding='utf-8') as file:
            # Sanitize name
            zone_num_str = item.replace('res\dialog-table-', '')
            zone_num_str = zone_num_str.replace('.xml', '')

            # TODO: Handle zone 50-2
            if zone_num_str == "50-2":
                print("SKIPPING AHT URGHAN WHITEGATE PART 2!")
                continue

            zone_num = int(zone_num_str)
            zone_name = areas[zone_num]

            # Skip obviously invalid or missing zones
            if zone_name == "unknown" or zone_name == "none":
                continue

            # Skip if there is any wrap-around or strangeness from missing zones
            if zone_name in handled_zones:
                continue

            # Parse as XML
            data = file.read()
            zone_tree = ET.fromstring(data)

            # Prepare filenames
            output_filename = 'out/scripts/zones/' + zone_name + "/Text.lua"
            raw_output_filename = output_filename + ".raw"
            server_filename = SERVER_DIR + "/scripts/zones/" + zone_name + "/IDs.lua"

            print(f"Generating {output_filename} ({zone_num})")
            with open(output_filename, 'w+') as out_file, open(raw_output_filename, 'w+') as raw_file, open(server_filename, 'r+') as server_file:
                # Populate data from server
                raw_server_data = server_file.read()
                server_data = raw_server_data.split("\n")
                output_list = []
                max_enum_length = 0
                max_index_length = 0
                duplicate_enums = {} # Track duplicate enums
                for entry in zone_tree:
                    # Index: The number
                    index = str(entry[0].text.strip())

                    # Comment: After the number
                    comment_text = entry[1].text
                    cleaned_comment_text = sanitize_pol_string(comment_text)
                    if len(cleaned_comment_text) <= 1:
                        continue

                    # Write raw output (good for debugging and lookup)
                    raw_file.write(f"{index} : {cleaned_comment_text}\n")

                    # Enum: Called and indexed by Lua function
                    # If comment text exists in the server IDs file
                    server_line_index = match_line(server_data, cleaned_comment_text)
                    if server_line_index != None:
                        # Use the original server strings for output
                        line = server_data[server_line_index]
                        original_line_parts = line.split("=")
                        enum_text = original_line_parts[0].strip()
                        original_comment = original_line_parts[1].split("-- ")[1]

                        # Try and de-dupe enum keys
                        count = duplicate_enums.get(enum_text, None)

                        if count is not None:
                            duplicate_enums[enum_text] = count + 1
                        else:
                            duplicate_enums[enum_text] = 1

                        count = duplicate_enums[enum_text]

                        if count > 1:
                            enum_text = f"{enum_text}_{count}"

                        # Another layer of sanity checking for de-dupes
                        if not enum_text in line:
                            continue

                        # Add to output list
                        output_list.append([enum_text, index, original_comment])
                        max_enum_length = max(max_enum_length, len(enum_text)) # For formatting later
                        max_index_length = max(max_index_length, len(index) + 1) # For formatting later

                # Build output string (indented like original files)
                out_string =  "    text =\n    {\n"
                for entry in output_list:
                    enum_text = f"        {entry[0].ljust(max_enum_length)}"
                    index_text_with_comma = f"{entry[1]},"
                    indented_index_text = f"{index_text_with_comma.ljust(max_index_length)}"
                    out_string = out_string + f"{enum_text} = {indented_index_text} -- {entry[2]}\n"
                out_string = out_string + "    },\n"

                # Write output file
                out_file.write(out_string)

                # Write to original files (only the text{...} table)
                new_server_data = re.sub(r"(    text =)(.|\n)*?(    \},\n)", out_string, raw_server_data)
                if new_server_data != raw_server_data:
                    server_file.seek(0)
                    server_file.truncate()
                    server_file.write(new_server_data)

                # Mark as done
                handled_zones.append(zone_name)
