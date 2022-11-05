import xmltodict
import xml.etree.ElementTree as ET
from utils import *

def parse_fields(items, item):
    if item["field"][6]["#text"] == ".":
        return

    items[int(item["field"][0]["#text"])] = {}
    try:
        for field in item['field']:
            items[int(item["field"][0]["#text"])][field["@name"]] = field["#text"]
    except:
        pass

def write_warning(file):
    file.write("-- WARNING: These entries are flawwed and are not suitable for direct copy/paste into\n")
    file.write("--        : their respetive server files. You should inspect them closely before use!\n\n")

############################
# Items / Weapons / Armour etc.
############################
def items():
    items = {}

    #     0 ->  4095 : items-general.xml
    print("Parsing: items-general.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-general.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    #  4096 ->  8191 : items-usable.xml
    print("Parsing: items-usable.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-usable.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    #  8192 ->  8703 : items-puppet.xml
    print("Parsing: items-puppet.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-puppet.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    #  8704 -> 10239 : items-general2.xml
    print("Parsing: items-general2.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-general2.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    # 10240 -> 16383 : items-armor.xml
    print("Parsing: items-armor.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-armor.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    # 16384 -> 23039 : items-weapons.xml
    print("Parsing: items-weapons.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-weapons.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    # 23040 -> 28671 : items-armor2.xml
    print("Parsing: items-armor2.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-armor2.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    # 28672 -> 29695 : items-voucher-slip.xml
    print("Parsing: items-voucher-slip.xml")
    item_basic_xml = xmltodict.parse(ET.tostring(
        ET.parse("res/items-voucher-slip.xml").getroot(), encoding="unicode"))
    for item in item_basic_xml['thing-list']['thing']:
        parse_fields(items, item)

    # 65535          : items-currency.xml
    # TODO

    ##########

    print("Writing: out/sql/item_basic.sql")
    with open("out/sql/item_basic.sql", "w", encoding='utf-8') as file:
        write_warning(file)
        # INSERT INTO `item_basic` VALUES (16641,0,'brass_axe','brass_axe',1,2084,5,0,312);
        #
        # `itemid` smallint(5) unsigned NOT NULL,
        # `subid` smallint(4) unsigned NOT NULL DEFAULT 0,
        # `name` tinytext NOT NULL,
        # `sortname` tinytext NOT NULL,
        # `stackSize` tinyint(2) unsigned NOT NULL DEFAULT 1,
        # `flags` smallint(5) unsigned NOT NULL DEFAULT 0,
        # `aH` tinyint(2) unsigned NOT NULL DEFAULT 99,
        # `NoSale` tinyint(1) unsigned NOT NULL DEFAULT 0,
        # `BaseSell` int(10) unsigned NOT NULL DEFAULT 0,
        for item in items.values():
            type = int(item["type"], 16)
            id = int(item["id"])
            san_name = item["name"].lower().replace(" ", "_").replace("'", "")

            stack_size = int(item["stack-size"])

            sql_str = f"INSERT INTO `item_basic` VALUES ({id},0,'{san_name}','{san_name}',{stack_size},0,0,0,0);"
            file.write(f"{sql_str}\n")

        file.write("\n")

    print("Writing: out/sql/item_equipment.sql")
    with open("out/sql/item_equipment.sql", "w", encoding='utf-8') as file:
        write_warning(file)
        # INSERT INTO `item_equipment` VALUES (16641,'brass_axe',8,0,2098561,77,0,0,3,0,0);
        #
        # `itemId` smallint(5) unsigned NOT NULL DEFAULT 0,
        # `name` tinytext DEFAULT NULL,
        # `level` tinyint(3) unsigned NOT NULL DEFAULT 0,
        # `ilevel` tinyint(3) unsigned NOT NULL DEFAULT 0,
        # `jobs` int(10) unsigned NOT NULL DEFAULT 0,
        # `MId` smallint(3) unsigned NOT NULL DEFAULT 0,
        # `shieldSize` tinyint(1) unsigned NOT NULL DEFAULT 0,
        # `scriptType` smallint(5) unsigned NOT NULL DEFAULT 0,
        # `slot` smallint(5) unsigned NOT NULL DEFAULT 0,
        # `rslot` smallint(5) unsigned NOT NULL DEFAULT 0,
        # `su_level` tinyint(3) unsigned NOT NULL DEFAULT 0,

        # {'id': '21770', 'flags': 'F840', 'stack-size': '1', 'type': '0004',
        # 'resource-id': '10599', 'valid-targets': '0000', 'name': 'Helgoland',
        # 'description': 'DMG:1 Delay:504', 'log-name-singular': 'Helgoland',
        # 'log-name-plural': 'Helgolands', 'level': '1', 'iLevel': '0',
        # 'slots': '0001', 'races': '01FE', 'jobs': '007FFFFE', 'superior-level': '0',
        # 'damage': '1', 'delay': '504', 'dps': '12', 'skill': '06', 'jug-size': '0',
        # 'max-charges': '0', 'casting-time': '0', 'use-delay': '0', 'reuse-delay': '0'}

        for item in items.values():
            type = int(item["type"], 16)
            if type != 5:
                continue

            id = int(item["id"])
            san_name = item["name"].lower().replace(" ", "_").replace("'", "")

            try:
                level = int(item["level"])
                iLevel = int(item["iLevel"])
                jobs   = int(item["jobs"], 16)
                mId    = 0
                shieldSize = 0
                slots = int(item["slots"])
                rslot = 0
                su_level = 0

                sql_str = f"INSERT INTO `item_equipment` VALUES ({id},'{san_name}',{level},{iLevel},{jobs},{mId},{shieldSize},{slots},{rslot},{su_level}); -- TODO: capture model from retail"
                file.write(f"{sql_str}\n")
            except:
                print(f"Could not write: {san_name} (id: {id}, type: {type})")

    print("Writing: out/sql/item_furnishing.sql")
    with open("out/sql/item_furnishing.sql", "w", encoding='utf-8') as file:
        write_warning(file)
        # INSERT INTO `item_furnishing` VALUES (1, 'pile_of_chocobo_bedding', 1, 520, 8, 2);
        #
        # `itemid` smallint(5) unsigned NOT NULL,
        # `name` text NOT NULL,
        # `storage` tinyint(3) unsigned NOT NULL DEFAULT '0',
        # `moghancement` smallint(4) unsigned NOT NULL DEFAULT '0',
        # `element` tinyint(3) unsigned NOT NULL DEFAULT '0',
        # `aura` tinyint(3) unsigned NOT NULL DEFAULT '0',
        for item in items.values():
            type = int(item["type"], 16)
            if type != 10:
                continue
        file.write("\n")

    print("Writing: out/sql/item_usable.sql")
    with open("out/sql/item_usable.sql", "w", encoding='utf-8') as file:
        write_warning(file)
        # INSERT INTO `item_usable` VALUES (4096,'fire_crystal',1,0,0,0,0,0,0,0);
        #
        # `itemid` smallint   (5) unsigned NOT NULL,
        # `name` text NOT NULL,
        # `validTargets` smallint(3) unsigned NOT NULL DEFAULT '0',
        # `activation` tinyint(3) unsigned NOT NULL DEFAULT '0',
        # `animation` smallint(4) unsigned NOT NULL DEFAULT '0',
        # `animationTime` tinyint(3) unsigned NOT NULL DEFAULT '0',
        # `maxCharges` tinyint(3) unsigned NOT NULL DEFAULT '0',
        # `useDelay` tinyint(3) unsigned NOT NULL DEFAULT '0',
        # `reuseDelay` int(10) unsigned NOT NULL DEFAULT '0',
        # `aoe` tinyint(1) unsigned NOT NULL DEFAULT '0',
        for item in items.values():
            pass
        file.write("\n")

    print("Writing: out/sql/item_weapon.sql")
    with open("out/sql/item_weapon.sql", "w", encoding='utf-8') as file:
        write_warning(file)
        # INSERT INTO `item_weapon` VALUES (16641,'brass_axe',5,0,0,0,0,2,1,276,12,0);
        #
        # `itemId` smallint(5) unsigned NOT NULL DEFAULT '0',
        # `name` text,
        # `skill` tinyint(2) unsigned NOT NULL DEFAULT '0',
        # `subskill` tinyint(2) NOT NULL DEFAULT '0',
        # `ilvl_skill` smallint(3) NOT NULL DEFAULT '0',
        # `ilvl_parry` smallint(3) NOT NULL DEFAULT '0',
        # `ilvl_macc` smallint(3) NOT NULL DEFAULT '0',
        # `dmgType` int(10) unsigned NOT NULL DEFAULT '0',
        # `hit` tinyint(1) unsigned NOT NULL DEFAULT '1',
        # `delay` int(10) NOT NULL DEFAULT '0',
        # `dmg` int(10) unsigned NOT NULL DEFAULT '0',
        # `unlock_points` smallint(5) NOT NULL DEFAULT '0',
        for item in items.values():
            type = int(item["type"], 16)
            if type != 4:
                continue

            id = int(item["id"])
            san_name = item["name"].lower().replace(" ", "_").replace("'", "")

            try:
                skill = int(item["skill"], 16)
                sub_skill = 0
                ilvl_skill = 0
                ilvl_parry = 0
                ilvl_macc = 0
                dmgType = 1
                hit = 1
                delay = int(item["delay"])
                dmg = int(item["damage"])
                unlock_points = 0
                description = ascii(item["description"]).replace("\\n", " ").replace("'", "")

                sql_str = f"INSERT INTO `item_weapon` VALUES ({id},'{san_name}',{skill},{sub_skill},{ilvl_skill},{ilvl_parry},{ilvl_macc},{dmgType},{hit},{delay},{dmg},{unlock_points}); -- {description}"
                file.write(f"{sql_str}\n")
            except:
                sql_str = f"INSERT INTO `item_weapon` VALUES ({id},'{san_name}',0,0,0,0,0,0,1,240,0,0); -- TODO: failed to read data"
                file.write(f"{sql_str}\n")

# Enable to test just this file
# items()
