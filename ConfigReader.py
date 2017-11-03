#!/home/tops/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import sys


class ConfigReader:
    def __init__(self, cfg_file=None):
        self.conf = None
        current_path = sys.path[0]
        self.file_path = current_path + "/conf.cfg"
        if cfg_file is not None:
            if not cfg_file.startswith("/"):
                raise IOError("The config file path must be absolute.")
            else:
                self.file_path = cfg_file

    def get(self, key):
        if self.conf is None:
            return self.read_conf().get(key)
        return self.conf.get(key)

    def read_conf(self):
        cf = ConfigParser.ConfigParser()
        conf = {}
        cf.read(self.file_path)
        secs = cf.sections()
        for sec in secs:
            items = cf.items(sec)
            for (key, value) in items:
                conf[key] = value
        self.conf = conf
        return conf

    def write_conf(self, conf):
        cf = ConfigParser.ConfigParser()
        for (key, value) in conf.items():
            sec_name = key[0:key.index("_")]
            if sec_name not in cf.sections():
                cf.add_section(sec_name)
            cf.set(sec_name, key, value)
        with open(self.file_path, "w") as fp:
            cf.write(fp)


if __name__ == '__main__':
    cr = ConfigReader()
    print cr.read_conf()
