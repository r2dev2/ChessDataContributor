from typing import *
from pathlib import Path
import os

import requests


HEADERS = {"user-agent": "chess-contributing-app"}

def grep(search: str, contents: Iterable) -> Generator[str, None, None]:
    for s in contents:
        if search in s:
            yield s

def getAllNames() -> Set[str]:
    fenurl = "https://github.com/r2dev2bb8/ChessData/tree/master/fens"
    r = requests.get(fenurl, HEADERS)
    rawnames = grep("</a", grep(".txt", r.content.decode().split('>')))
    return {name[:-3] for name in rawnames}

def getTakenNames() -> Set[str]:
    readmeurl = "https://raw.githubusercontent.com/r2dev2bb8/ChessData/master/README.md"
    r = requests.get(readmeurl, HEADERS)
    rawnames = grep(".txt", r.content.decode().split('\n'))
    return {s.split('|')[2].strip() for s in rawnames}

def getAvailableNames() -> Set[str]:
    allnames = getAllNames()
    taken = getTakenNames()
    return {name for name in allnames if name not in taken}

def createDir(name: str) -> None:
    try:
        os.mkdir(name)
    except FileExistsError:
        pass

def downloadName(name: str) -> None:
    createDir("data")
    fenurl = "https://raw.githubusercontent.com/r2dev2bb8/ChessData/master/fens/"
    r = requests.get(fenurl + name, HEADERS)
    with open(str(Path(os.getcwd()) /  "data" / name), 'w+') as fout:
        fout.write(r.content.decode())

def main():
    names = list(getAvailableNames())
    names.sort()
    print(names)

if __name__ == "__main__":
    main()
