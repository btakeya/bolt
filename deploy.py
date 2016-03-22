#!/usr/bin/python3

import os
import sys
import json
import subprocess
import shutil
import signal
import time

import bolt_nginx

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
        self.old_pid = 0
        self.port = 0

    def load_file(self, metafile):
        if not os.path.isfile(metafile):
            self.mode = 1
            self.pid = 0
            return

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
        self.mode = 1 - self.mode
        self.unpack()

    def unpack(self):
        DIST_DIR = '%s-%d' % (DEPLOY_DIR, self.mode)
        if os.path.isdir(DIST_DIR):
            shutil.rmtree(DIST_DIR)
        subprocess.call(['unzip', PROJECT_PACKAGE, '-d', DIST_DIR])

    def run_server(self):
        PROJECT_RUN_BIN = '%s/%s' % (get_project_running_basedir(self.mode), PROJECT_RUNNING_CMD)
        ARG_PORT = '-Dhttp.port=%d' % (BASE_PORT + self.mode)
        ARG_RUNMODE = '-Drun.mode=service'
        PROJECT_RUN_CMD = [PROJECT_RUN_BIN, ARG_PORT, ARG_RUNMODE]

        process = subprocess.Popen(PROJECT_RUN_CMD)
        self.old_pid = self.pid
        self.pid = process.pid

    def replace_server(self):
        # TODO: reload reverse proxy (old -> new)
        try:
            bolt_nginx.make_conf_file(self.mode)
            bolt_nginx.reload_nginx()
        except:
            print('Errors on reloading nginx: {}', sys.exc_info()[0])

        time.sleep(10)
        self.cleanup_old_server()

    def cleanup_old_server(self):
        target_pid = self.old_pid
        if target_pid == 0:
            return

        os.kill(target_pid, signal.SIGTERM)

    def toString(self):
        return 'BoltMetadata(mode: %d, pid: %d)' % (self.mode, self.pid)

def run():
    meta = BoltMetadata()
    meta.load_file(METAFILE)
    meta.prepare_server()
    meta.run_server()
    meta.replace_server()
    meta.save_file(METAFILE)

if __name__ == '__main__':
    run()
