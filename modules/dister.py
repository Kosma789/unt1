import os

def run(**args):

    print "mod"
    files = os.listdir(".")

    return str(files)