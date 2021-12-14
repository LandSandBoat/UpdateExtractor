############################
#
# MIT License
#
# update_extractor.py
# Copyright (c) 2021 Zach Toogood
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
############################
#
# The following files from POLUtils should be in the directory next to this script
# when you run it (https://github.com/Windower/POLUtils):
# - MassExtractor.exe
# - PlayOnline.Core.dll
# - PlayOnline.FFXI.dll
#
############################

############################
# Python Imports
############################
import re
import xml.etree.ElementTree as ET
import os
import subprocess
import glob

############################
# pip Imports
############################
try:
    import xmltodict
except:
    print("Failed to import xmltodict, please install with `pip install xmltodict`")
    exit(-1)

############################
# own Imports
############################
from utils import *
from config import *
from client_ver import *
from titles import *
from status_effects import *
from items import *
from zone_texts import *
from entity_ids import *
from misc import *

############################
# Config
############################
check_config()

############################
# Setup
############################
print("Looking for exes")
if not os.path.exists('./MassExtractor.exe') and not os.path.exists('./PlayOnline.Core.dll') and not os.path.exists('./PlayOnline.FFXI.dll'):
    print("Could not find one or all of: MassExtractor.exe, PlayOnline.Core.dll, PlayOnline.FFXI.dll")
    exit(-1)

print("Creating folder layout")
if not os.path.exists("out"):
    os.makedirs("out")

if not os.path.exists("out/conf"):
    os.makedirs("out/conf")

if not os.path.exists("out/conf/default"):
    os.makedirs("out/conf/default")

if not os.path.exists("out/scripts"):
    os.makedirs("out/scripts")

if not os.path.exists("out/scripts/globals"):
    os.makedirs("out/scripts/globals")

if not os.path.exists("out/scripts/zones"):
    os.makedirs("out/scripts/zones")

if not os.path.exists("out/sql"):
    os.makedirs("out/sql")

############################
# MassExtractor
############################
if not os.path.exists("res"):
    print("Running MassExtractor.exe -> ./res/")
    os.makedirs("res")
    subprocess.run(["MassExtractor.exe", "res"])
else:
    print("Did not need to run MassExtractor.exe")

############################
# Extract Stages
############################
client_ver()
titles()
status_effects()
items()
zone_texts()
#entity_ids()
#misc()

print("Done")
