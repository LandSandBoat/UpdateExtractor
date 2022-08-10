import re
from config import *

############################
# Client Ver
############################
def client_ver():
    current_client_ver = ""
    new_client_str = ""
    with open("""C:\Program Files (x86)\PlayOnline\SquareEnix\FINAL FANTASY XI\patch.cfg""", "r") as file:
        match_str = re.findall(r"\{(.*?)\}", file.read(),
                            re.MULTILINE | re.DOTALL)[0]
        split_list = re.split(" |/|\n", match_str)
        version_list = list(filter(lambda k: "_" in k, split_list))
        current_client_ver = version_list[-1]
        new_client_str = f"CLIENT_VER: {current_client_ver}"
        print(new_client_str)

    with open("out/conf/default/version.conf", "w+") as file:
        file.write(new_client_str)

    # with open(SERVER_DIR + "/conf/default/version.conf", 'r+') as server_file:
    #     raw_server_data = server_file.read()
    #     new_server_data = re.sub(r"CLIENT_VER: .*\n", new_client_str + '\n', raw_server_data)
    #     server_file.seek(0)
    #     server_file.truncate()
    #     server_file.write(new_server_data)
