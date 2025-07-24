import json

class A:
    def __init__(self, config_file):
        with open(config_file) as f:
            config = json.load(f)
        self.flag = config.get('flag')
        self.time = config.get('time')
        self.attr3 = config.get('attr3')
