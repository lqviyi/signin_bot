import json
from os.path import isfile

is_init = False

config_dic = {}
common = {}
admin = {}

def init_config():
    global config_dic
    global common
    global admin


    global is_init
    if is_init:
        return
    is_init = True

    if isfile(r"./config/config.json"):
        with open("./config/config.json", 'r', encoding='utf-8') as f:
            config_dic = json.loads(f.read())
    if config_dic['common'] is not None:
        common = config_dic['common']
        admin = config_dic['admin']



init_config()


