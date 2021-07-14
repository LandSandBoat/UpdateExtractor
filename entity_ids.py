import xmltodict
import xml.etree.ElementTree as ET
import glob
import os
import re
from config import *
from utils import *

############################
# Entity IDs
############################
# Gather mob-list*.xml into a giant table of { id, name }.
# Go through and check that id and name still match what we have in SQL.
# If not, do a search/replace to try and update them

def entity_ids():
    # Collect zone information
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

    # Extract Client NPC id information (build extracted_npc_data dict)
    extracted_npc_data = {}
    handled_zones = []
    zone_ids = []
    dialog_table_list = glob.glob('res/mob-list-*.xml')
    for item in dialog_table_list:
        with open(item, 'r', encoding='utf-8') as file:
            # Sanitize name
            zone_num_str = item.replace('res\mob-list-', '')
            zone_num_str = zone_num_str.replace('.xml', '')

            # TODO: Handle zone 50-2
            if zone_num_str == "50-2":
                #print("SKIPPING AHT URGHAN WHITEGATE PART 2!")
                continue

            zone_num = int(zone_num_str)
            zone_name = areas[zone_num]

            # Skip obviously invalid or missing zones
            if zone_name.lower() == "unknown" or zone_name.lower() == "none":
                #print(f"Skipping zone name: unknown or none ({zone_num})")
                continue

            # Skip if there is any wrap-around or strangeness from missing zones
            if zone_name in handled_zones:
                #print(f"Skipping wrapped-around zone: {zone_num}")
                continue

            extracted_npc_data[zone_num] = []

            # Parse as XML
            data = file.read()
            zone_tree = ET.fromstring(data)

            # Prepare filenames
            raw_output_filename = 'out/scripts/zones/' + zone_name + "/NPC_IDs.txt"

            with open(raw_output_filename, 'w+') as out_file:
                for entry in zone_tree:
                    # Index: The number
                    index = str(entry[0].text.strip())
                    name  = str(entry[1].text.strip())
                    extracted_npc_data[zone_num].append((index, name))
                    out_file.write(f"{index}    {name}\n")

        # Mark as done
        handled_zones.append(zone_name)
        zone_ids.append(zone_num)

    # Extract Server Data (build server_zone_data dict)
    server_zone_data = {}
    for zone_id in zone_ids: #range(230, 231): #
        server_zone_data[zone_id] = []

        # Start looking at target file
        server_filename = SERVER_DIR + "/sql/npc_list.sql"
        sql_data = ""
        with open(server_filename, 'r') as server_file:
            sql_data = server_file.read()

        # Regex out all the entries between the current zone header, and the next one
        matches = re.findall(fr"(?<=\(Zone {zone_id})(.*?)(?=Zone [0-9]+\))", sql_data, re.DOTALL)
        if len(matches) == 0:
            print(f"Unable to match on regex for Zone {zone_id}\n")
            continue

        section = matches[0]
        for index, line in enumerate(section.split("\n")):

            # TODO: Handle startswith "-- NC: "

            # Ignore comments
            if line.startswith("-- "):
                continue

            # Ignore all non-insert statements
            if not "INSERT INTO" in line:
                continue

            # Extract out the id and the name
            line_data = line.split("(")
            line_data = line_data[1].split(",")
            server_id = line_data[0].replace("\'", "")
            server_name = line_data[1].replace("\'", "")
            server_zone_data[zone_id].append((server_id, server_name))

        # Start main shifting logic using zone_id, server_zone_data, and extracted_npc_data
        zone_name = areas[zone_id]

        server_data = server_zone_data[zone_id]
        extracted_client_data = extracted_npc_data[zone_id]

        # Bail on empty zones
        if len(server_data) == 0 or len(extracted_client_data) == 0:
            continue

        # Client index 0 is always: (0, none), so get rid of that
        extracted_client_data.pop(0)

        # NOTE: The starting index in a zone can shift too, don't rely on it!

        # Server Entries
        first_server_entry = server_data[0]
        last_server_entry  = server_data[-1]

        # Client Entries
        first_client_entry = extracted_client_data[0]
        last_client_entry  = extracted_client_data[-1]

        print(zone_id, zone_name, "starting id:", first_client_entry[0])

        #mismatch = False
        #for idx, client_entry in enumerate(extracted_client_data):
        #    server_entry = server_data[idx]
        #    if server_data[idx][1] != extracted_client_data[idx][1]:
        #        mismatch = True
        #        break
        #        #print("Mismatch: Server:", server_data[idx], ", Client:", extracted_client_data[idx])

        # Handle new entries
        #-- NC: INSERT INTO `npc_list` VALUES (17461595,'NOT_CAPTURED','     ',0,0.000,0.000,0.000,0,50,50,0,0,0,0,0,0x0000320000000000000000000000000000000000,0,NULL,0);

        # Collect list of shifts

        # Apply shifts to npc_list.sql

        # Hunt for those shifts in the server codebase and find/replace
        # - nm_spawn_points.sql

# Enable to test just this file
#entity_ids()
