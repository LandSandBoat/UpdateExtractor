
import xmltodict
import xml.etree.ElementTree as ET
from config import *
from utils import *

############################
# Key Items
############################
def keyitems():
    print("Generating out/scripts/globals/keyitems.lua")
    keyitems = {}
    longest_str = 0
    data = {}
    # Note: Requires keyitems.txt: a file generated from Ashita
    with open("keyitems.txt", "r", encoding='utf-8') as file:
        data = file.readlines()

    for line in data:
        line_data = line.split('-', 1)
        num = int(line_data[0].strip())
        name = to_caps_string(line_data[1])
        if len(name) > 1:
            longest_str = max(longest_str, len(name))
            keyitems[num] = name

    # Generate output string
    out_string = "xi.keyItem =\n{\n"
    for key, value in keyitems.items():
        cleaned_title = to_caps_string(value)
        title_str = f"    {cleaned_title.ljust(longest_str - 1)}"
        index_str = str(int(key))
        utf8_comment = value.encode("utf-8")

        out_string += f"{title_str} = {index_str},\n"
        #file.write(f"{title_str} = {index_str}, -- {utf8_comment}\n")
    out_string += "}\n"

    with open("out/scripts/globals/keyitems.lua", "w") as file:
        file.write(out_string)

# Enable to test just this file
#keyitems()
