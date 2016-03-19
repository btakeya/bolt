#!/usr/bin/python3

import os
import json

project_root = os.path.realpath('')
metafile = project_root + '/deploy.info'
BASE_PORT = 9000

class BoltMetadata(object):
    def __init__(self):
        self.mode = 0
        self.pid = 0
        self.port = 0

    def load_file(self, metafile):
        meta_file = open(metafile, 'r')
        meta = meta_file.read()
        meta_json = json.loads(meta)
        self.mode = meta_json['mode']
        self.pid = meta_json['pid']
        self.port = meta_json['port']
        meta_file.close()

    def save_file(self, metafile):
        meta_file = open(metafile, 'w')
        meta_dict = {'mode': self.mode, 'pid': self.pid, 'port': self.port}
        meta_str = json.dumps(meta_dict)
        meta_file.write(meta_str)
        meta_file.close()

    def run_server(self):
        return 0

    def toString(self):
        return 'BoltMetadata(mode: %d, pid: %d, port: %d' % (self.mode, self.pid, self.port)

def run():
    meta = BoltMetadata()
    meta.load_file(metafile)
    meta.save_file(metafile)

if __name__ == '__main__':
    run()
