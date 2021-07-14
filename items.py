import xmltodict
import xml.etree.ElementTree as ET
from utils import *

############################
# Items / Weapons / Armour etc.
############################
def items():
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

    with open("out/sql/item_basic.sql", "w") as file:
        file.write("\n")

    with open("out/sql/item_equipment.sql", "w") as file:
        file.write("\n")

    with open("out/sql/item_furnishing.sql", "w") as file:
        file.write("\n")

    with open("out/sql/item_usable.sql", "w") as file:
        file.write("\n")

    with open("out/sql/item_weapon.sql", "w") as file:
        file.write("\n")

# Enable to test just this file
#items()
