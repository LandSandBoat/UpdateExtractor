
import xmltodict
import xml.etree.ElementTree as ET
from config import *
from utils import *

############################
# Titles
############################
def titles():
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

    # Generate output string
    out_string = "xi.title =\n{\n"
    for key, value in titles.items():
        cleaned_title = to_caps_string(value)
        title_str = f"    {cleaned_title.ljust(longest_title_str - 1)}"
        index_str = str(int(key))
        utf8_comment = value.encode("utf-8")

        out_string += f"{title_str} = {index_str},\n"
        #file.write(f"{title_str} = {index_str}, -- {utf8_comment}\n")
    out_string += "}\n"

    with open("out/scripts/globals/titles.lua", "w") as file:
        file.write(out_string)

    server_filename = SERVER_DIR + "/scripts/globals/titles.lua"
    with open(server_filename, 'r+') as server_file:
        raw_server_data = server_file.read()
        # Write to original files (only the text{...} table)
        new_server_data = re.sub(r"(xi.title)(.|\n)*?(\}\n)", out_string, raw_server_data)
        if new_server_data != raw_server_data:
            server_file.seek(0)
            server_file.truncate()
            server_file.write(new_server_data)
