import re

############################
# Client Ver
############################
def client_ver():
    print("Fetching installed client version")
    current_client_ver = ""
    with open("""C:\Program Files (x86)\PlayOnline\SquareEnix\FINAL FANTASY XI\patch.cfg""", "r") as file:
        match_str = re.findall(r"\{(.*?)\}", file.read(),
                            re.MULTILINE | re.DOTALL)[0]
        split_list = re.split(" |/|\n", match_str)
        version_list = list(filter(lambda k: "_" in k, split_list))
        current_client_ver = version_list[-1]
        print(current_client_ver)

    with open("out/conf/default/version.conf", "w") as file:
        file.write(f"CLIENT_VER: {current_client_ver}\n")
