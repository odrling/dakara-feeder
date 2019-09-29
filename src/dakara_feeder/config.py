from dakara_base.resources_manager import get_file

CONFIG_FILE = "config.yaml"


def dump_config():
    # get the file
    origin = get_file("dakara_feeder.resources", CONFIG_FILE)
    destination = CONFIG_FILE

    # copy file
    origin.copyfile(destination)
