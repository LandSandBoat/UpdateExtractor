# Set this to your DSP/TPZ/LSB root dir
SERVER_DIR="C:/ffxi/server"

############################
# User Config
############################
def check_config():
    if SERVER_DIR == "":
        print("config.py: Please populate SERVER_DIR with your server dir")
        exit(-1)
