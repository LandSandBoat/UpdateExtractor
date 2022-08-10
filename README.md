# UpdateExtractor

`UpdateExtractor` is a tool to help extract useful and usable information for `LandSandBoat` servers from installed game clients. `POLUtils`'s `MassExtractor` extracts the relevant information for a given client install, but it is just a data dump. `UpdateExtractor` takes this data dump, sanitizes it, and modifies your server install in place (or provide easy copy/paste) so that you don't have to spend hours fixing shifting IDs or hunting down content changes.

It is primarily designed for use between nearby modern retail versions, but should work for extracting information from historical clients too.

## Requirements

- Python 3
- `xmltodict` installed through `pip`
- `POLUtils` installed

## Features

- Extract client version string for `version.conf`
- Extract data and update `globals/titles.lua` in place
- Extract data for `globals/status_effects.lua`
- Extract data and update `zones/<zone_name>/IDs.lua` text ID's in place, handling:
  - Formatting and spacing
  - Ordering
  - ID shifts

## TODO

- Extract and update in place:
  - `sql/items_*.sql`
  - `sql/mob_spawn_points.sql`
  - `sql/npc_list.sql`
  - Mob/NPC ID shifts in `zones/<zone_name>/IDs.lua` files

## Usage

1) Make sure the following files from `POLUtils` are copied into the root folder next to `update_extractor.py`:
    - `MassExtractor.exe`
    - `PlayOnline.Core.dll`
    - `PlayOnline.FFXI.dll`

2) Go into `config.py` and fill in your server install location. For example:

    ```py
    # Set this to your LSB root dir
    SERVER_DIR="C:/ffxi/server"
    ```

3) Run: `python update_extractor.py`

## Output

```txt
~>>/ffxi/UpdateExtractor/update_extractor.py
Looking for exes
Creating folder layout
Did not need to run MassExtractor.exe
Fetching installed client version
30210604_1
Generating out/scripts/globals/titles.lua
Generating out/scripts/globals/status_effects.lua
Generating out/sql/item_basic.sql
Generating out/scripts/zones/Phanauet_Channel/Text.lua (1)
Generating out/scripts/zones/Carpenters_Landing/Text.lua (2)

...

Generating out/scripts/zones/Dynamis-Windurst_[D]/Text.lua (296)
Generating out/scripts/zones/Dynamis-Jeuno_[D]/Text.lua (297)
Generating out/scripts/zones/Walk_of_Echoes_P1/Text.lua (298)
SKIPPING AHT URGHAN WHITEGATE PART 2!
Done
```
