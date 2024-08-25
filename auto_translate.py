import binascii
import xmltodict
import xml.etree.ElementTree as ET
import glob
import os

from collections import OrderedDict
from config import *
from utils import *

class Item():
    itemid = 0
    en = ""
    jp = ""

def dump_table(autotranslate_table):
    output_filename = 'out/sql/item_translation_table.sql'

    header = '''-- /translate command table
-- Store as varbinary because of shift-jis shenanigans. English text will be transformed on load.
DROP TABLE IF EXISTS `item_translation_table`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `item_translation_table` (
  `itemId` smallint(5) unsigned NOT NULL,
  `englishText` varbinary(64) NOT NULL DEFAULT 0,
  `japaneseText` varbinary(64) NOT NULL DEFAULT 0,
  PRIMARY KEY (`itemId`)
) ENGINE=Aria TRANSACTIONAL=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci PACK_KEYS=1;

'''
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(header)

        for itemid in sorted(autotranslate_table.keys()):
            if not 'jp' in autotranslate_table[itemid] or not 'en' in autotranslate_table[itemid]:
                continue # No key, skip it.

            # Japanese text doesn't seem to use quotes, but will that always be true?
            en = autotranslate_table[itemid]['en'].replace("'", "\\'").replace("\"","\\\"")
            jp = autotranslate_table[itemid]['jp'].replace("'", "\\'").replace("\"","\\\"")

            file.write(u"INSERT INTO `item_translation_table` VALUES ({0}, '{1}', '{2}');\n".format(itemid, en, jp))

def auto_translate():
    # Yuck. polutils doesn't extract generalE2 to the same location.
    files_en = { "generalE", "../items-general2", "usableE",  "puppetE", "armorE", "armor2E", "weaponE", "slipE", "currencyE", }
    files_jp = { "generalJ", "general2J", "usableJ", "puppetJ", "armorJ", "armor2J", "weaponJ", "slipJ", "currencyJ"}

    en_items = {}
    for file in files_en:
         tree = ET.parse('res/resources/' + file + '.xml')
         xml = xmltodict.parse(ET.tostring(tree.getroot(), encoding='unicode'))
         for item in xml["thing-list"]["thing"]:
            parse_fields(en_items, item)

    jp_items = {}
    for file in files_jp:
         tree = ET.parse('res/resources/' + file + '.xml')
         xml = xmltodict.parse(ET.tostring(tree.getroot(), encoding='unicode'))
         for item in xml["thing-list"]["thing"]:
            parse_fields(jp_items, item)

    autotranslate_table = {}

    for item in en_items:
        if item in autotranslate_table:
            autotranslate_table[item]['en'] = en_items[item]['name']
        else:
            autotranslate_table[item] = {}
            autotranslate_table[item]['en'] = en_items[item]['name']

    for item in jp_items:
        if item in autotranslate_table:
            autotranslate_table[item]['jp'] = jp_items[item]['name']
        else:
            autotranslate_table[item] = {}
            autotranslate_table[item]['jp'] = jp_items[item]['name']

    for at in autotranslate_table:
        if not 'jp' in autotranslate_table[at]:
            print("Warning: Item id '{0}' named '{1}' not found in jp table. Please investigate for a real error".format(jp_items[at]['id'], jp_items[at]['name']))
            continue
        if not 'en' in autotranslate_table[at]:
            print("Warning: Item id '{0}' named '{1}' not found in en table. This may not be a real problem -- JP dats can sometimes contain extra data.".format(jp_items[at]['id'], jp_items[at]['name'].encode('utf-8')))
            continue

    dump_table(autotranslate_table)

def parse_fields(items, item):

    # no clue. sometimes item is "@type" or "field" strings.
    # check if "item" is a string type, do not parse.
    if isinstance(item, str):
        return

    if item["field"][6]["#text"] == ".":
        return

    items[int(item["field"][0]["#text"])] = {}
    try:
        for field in item["field"]:
            items[int(item["field"][0]["#text"])][field["@name"]] = field["#text"]
    except:
        pass

# Enable to test just this file
#auto_translate()
