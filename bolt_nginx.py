import os
import sys
import subprocess

PROXY_LISTEN_PORT = 8000
PROXY_LISTEN_NAME = 'default_server'
PROXY_LISTEN_URI = 'api'
PROJECT_LISTEN_PORT = 9000
NGINX_CONF_AVAILABLE_DIR = '/etc/nginx/sites-available'
NGINX_CONF_ENABLE_DIR = '/etc/nginx/sites-enabled'
NGINX_CONF_FILE = NGINX_CONF_AVAILABLE_DIR + '/around-{}'
NGINX_CONF_SYMLINK = NGINX_CONF_ENABLE_DIR + '/around-{}'

def make_conf_format(mode):
    NGINX_CONF_FORMAT = \
        "server {\n" + \
        "  listen {} {};\n".format(PROXY_LISTEN_PORT, PROXY_LISTEN_NAME) + \
        "  listen [::]:{} {};\n".format(PROXY_LISTEN_PORT, PROXY_LISTEN_NAME) + \
        "  location /{} {{\n".format(PROXY_LISTEN_URI) + \
        "    proxy_pass http://localhost:{};\n".format(PROJECT_LISTEN_PORT + mode) + \
        "    proxy_http_version 1.1;\n" + \
        "    proxy_set_header Upgrade $http_upgrade;\n" + \
        "    proxy_set_header Connection 'upgrade';\n" + \
        "    proxy_set_header Host $host;\n" + \
        "    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n" + \
        "    proxy_cache_bypass $http_upgrade;\n" + \
        "  }\n" + \
        "}"
    return NGINX_CONF_FORMAT

def make_conf_file(mode):
    if not os.geteuid() == 0:
        sys.exit('[Error] Must be run as superuser')

    if not type(mode) == int:
        return False

    confname = NGINX_CONF_FILE.format(mode)
    conffile = open(confname, 'w')
    conffile.write(make_conf_format(mode))
    conffile.close()

    old_mode = 1 - mode
    old_link = NGINX_CONF_SYMLINK.format(old_mode)
    if os.path.isfile(old_link):
        os.remove(old_link)

    conf = NGINX_CONF_FILE.format(mode)
    link = NGINX_CONF_SYMLINK.format(mode)
    if os.path.isfile(link):
        os.remove(link)

    os.symlink(conf, link)

def reload_nginx():
    if not os.geteuid() == 0:
        sys.exit('[Error] Permission denied: Need to run as Superuser')

    subprocess.call(['/etc/init.d/nginx', 'reload'])
