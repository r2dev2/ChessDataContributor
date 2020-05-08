import os

def create(path):
    open(path, 'w+').close()

def delete(path):
    os.remove(path)
