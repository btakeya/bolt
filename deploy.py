#!/usr/bin/python3

import os
import json
import subprocess
import shutil

PROJECT_ROOT = os.path.realpath('')
METAFILE = PROJECT_ROOT + '/deploy.info'
BASE_PORT = 9000
PROJECT_NAME = 'aroundplay'
PROJECT_VERSION = '1.0-SNAPSHOT'
PROJECT_TARGET = 'package/%s-%s' % (PROJECT_NAME, PROJECT_VERSION)
PROJECT_PACKAGE = '%s.zip' % (PROJECT_TARGET)
DEPLOY_BASEDIR = 'deploy'
DEPLOY_DIR = '%s/deploy' % (DEPLOY_BASEDIR)
PROJECT_RUNNING_CMD = 'bin/aroundplay'

def get_project_running_basedir(mode):
    if type(mode) != int:
        print('mode must be integer type')
        return false
    PROJECT_RUNNING_BASEDIR = '%s-%d/%s-%s' % (DEPLOY_DIR, mode, PROJECT_NAME, PROJECT_VERSION)
    return PROJECT_RUNNING_BASEDIR

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
        meta_file.close()

    def save_file(self, metafile):
        meta_file = open(metafile, 'w')
        meta_dict = {'mode': self.mode, 'pid': self.pid}
        meta_str = json.dumps(meta_dict)
        meta_file.write(meta_str)
        meta_file.close()

    def prepare_server(self):
        self.unpack()

    def unpack(self):
        DIST_DIR = '%s-%d' % (DEPLOY_DIR, self.mode)
        if os.path.isdir(DIST_DIR):
            shutil.rmtree(DIST_DIR)
        subprocess.call(['unzip', PROJECT_PACKAGE, '-d', DIST_DIR])

    def run_server(self):
        DEPLOY_RUN_COMMAND = '%s/%s' % (get_project_running_basedir(self.mode), PROJECT_RUNNING_CMD)
#        subprocess.call([DEPLOY_RUN_COMMAND, '-Dhttp.port=%d' % (BASE_PORT + self.mode)])
        os.system(DEPLOY_RUN_COMMAND + ' -Dhttp.port=%d' % (BASE_PORT + self.mode) + '&')

    def cleanup_old_server(self):
        #TODO
        pass

    def toString(self):
        return 'BoltMetadata(mode: %d, pid: %d)' % (self.mode, self.pid)

def run():
    meta = BoltMetadata()
    meta.load_file(METAFILE)
    meta.mode = 1 - meta.mode
    meta.prepare_server()
    meta.run_server()
    meta.cleanup_old_server()
    meta.save_file(METAFILE)

if __name__ == '__main__':
    run()
