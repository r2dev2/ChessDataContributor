import os
import smtplib
import stat
import sys
import zipfile
from email.message import EmailMessage
from multiprocessing import Process, freeze_support, Pool
from pathlib import Path
from subprocess import call, check_output
from typing import *

import cpuinfo

import evalfen
from getFile import createDir, downloadName, getAvailableNames, clearDir
from send import sendFile, sendNotification

STOCKFISH_DOWNLOAD = {
    "win32": "https://stockfishchess.org/files/stockfish-11-win.zip",
    "linux": "https://stockfishchess.org/files/stockfish-11-linux.zip",
    "linux32": "https://stockfishchess.org/files/stockfish-11-linux.zip",
    "darwin": "https://stockfishchess.org/files/stockfish-11-mac.zip"
}

STOCKFISH_LOCATION = {
    "win32": r"stockfish\stockfish-11-win\Windows\stockfish_20011801_x64{}.exe",
    "linux": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_{}",
    "linux32": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_{}",
    "darwin": "stockfish/stockfish-11-mac/Mac/stockfish-11-{}"
}

def promptName() -> str:
    return input("What is your name or github username? ")


def unzip(filepath: str, resultpath: str) -> None:
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(resultpath)


def promptNames(names: List[str]) -> str:
    for i, name in enumerate(names):
        print(i, name, sep='\t')
    uin = int(input("Which number? "))
    return names[uin]


def promptDownload() -> bool:
    uin = input("Do you need to download any other dataset?(y)es/(n)o ")
    return 'y' in uin


def downloadStockfish() -> None:
    link = STOCKFISH_DOWNLOAD[sys.platform]
    call(["curl", "-o", "stockfish.zip", link])
    unzip("stockfish.zip", "stockfish/")
    stockfishexecutable = str(findStockfish())
    if sys.platform != "win32":
        os.chmod(stockfishexecutable, stat.S_IEXEC)
    os.remove("stockfish.zip")

def promptNameChoice() -> Tuple[str]:
    available = os.listdir("data")
    for i, name in enumerate(available):
        print(i, name, sep='\t')
    uin = input("Which would you like to start on? ")
    try:
        uin = available[int(uin)]
    except ValueError:
        pass
    return str(Path(os.getcwd()) / "data" / uin), uin

def findStockfish() -> Path:
    toadd = "_bmi2" if sys.platform != "darwin" else "bmi2"
    info = cpuinfo.get_cpu_info()["brand"]
    if '-2' in info:
        toadd = ''
    if '-3' in info:
        toadd = "_modern" if sys.platform != "darwin" else "modern"
    return Path(os.getcwd()) / (STOCKFISH_LOCATION[sys.platform]).format(toadd)


def promptStockfish() -> Path:
    needsfish = "stockfish" not in os.listdir()
    if needsfish:
        print("Downloading stockfish")
        downloadStockfish()
    return findStockfish()

def getNumberThreads() -> int:
   return os.cpu_count()

def promptThreads() -> int:
    numthreads = getNumberThreads()
    userthreads = 0
    print(f"You have {numthreads} threads available.")
    while not 1 <= userthreads <= numthreads:
        try:
            userthreads = int(input("How many threads would you like to use? "))
        except ValueError:
            pass
    return userthreads

def main() -> None:
    createDir("dest")
    createDir("data")
    clearDir("cache")
    if promptDownload():
        names = list(getAvailableNames())
        names.sort()
        name = promptNames(names)
        downloadName(name)
        sendNotification(promptName(), name)
    pathToStockfish = str(promptStockfish())
    threads = promptThreads()
    source, name = promptNameChoice()
    dest = str(Path(os.getcwd()) / "dest" / name)

    amountlines = evalfen.lineCount(dest)

    evalargs = (source, dest, 22, threads, amountlines, pathToStockfish)
    evaluate = Process(target=evalfen.main, args=evalargs)
    evaluate.start()

    print("Control c to quit")
    print("Don't be intimidated by the wall of errors :)")
    try:
        evaluate.join()
        sendFile(promptName(), dest)
    except KeyboardInterrupt:
        evaluate.terminate()

    print("Done for now")


if __name__ == "__main__":
    if sys.platform == "win32":
        freeze_support()
    main()
