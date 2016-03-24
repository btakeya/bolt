#!/usr/bin/python3

import os
import sys
import json
import subprocess
import shutil
import signal
import time

from webserver import bolt_nginx

PROJECT_ROOT = os.path.realpath('')
METAFILE = PROJECT_ROOT + '/deploy.info'
BASE_PORT = 9000
PROJECT_PACKAGE_FILENAME = 'aroundplay-1.0-SNAPSHOT.zip'
PROJECT_PACKAGE_NAME = PROJECT_PACKAGE_FILENAME[0:PROJECT_PACKAGE_FILENAME.rfind('.zip')] # aroundplay-1.0-SNAPSHOT
PROJECT_PACKAGE_FULLPATH = 'package/{}'.format(PROJECT_PACKAGE_FILENAME)
DEPLOY_DIR = 'deploy/deploy-{}'
PROJECT_RUNNING_CMD = 'bin/aroundplay'

def get_project_running_basedir(mode):
    if type(mode) != int:
        print('mode must be integer type')
        return false

    PROJECT_RUNNING_BASEDIR = DEPLOY_DIR.format(mode) + '/' + PROJECT_PACKAGE_NAME
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
        self.extract_package()

    def extract_package(self):
        DIST_DIR = DEPLOY_DIR.format(self.mode)
        PROJECT_EXTRACT_CMD = 'unzip {} -d {}'.format(PROJECT_PACKAGE_FULLPATH, DIST_DIR)
        if os.path.isdir(DIST_DIR):
            shutil.rmtree(DIST_DIR)
        subprocess.call(PROJECT_EXTRACT_CMD.split())

    def run_server(self):
        PROJECT_RUN_CMD = \
                '{}/{} -Dhttp.port={} -Drun.mode=service' \
                .format(get_project_running_basedir(self.mode), PROJECT_RUNNING_CMD, (BASE_PORT + self.mode))

        process = subprocess.Popen(PROJECT_RUN_CMD.split())
        self.old_pid = self.pid # to kill
        self.pid = process.pid  # just run now

    def replace_server(self):
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
        return 'BoltMetadata(mode: {}, pid: {})'.format(self.mode, self.pid)

def run():
    meta = BoltMetadata()
    meta.load_file(METAFILE)
    meta.prepare_server()
    meta.run_server()
    meta.replace_server()
    meta.save_file(METAFILE)

if __name__ == '__main__':
    run()
