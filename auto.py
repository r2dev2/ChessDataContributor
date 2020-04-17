import os
import smtplib
import stat
import sys
import zipfile
from email.message import EmailMessage
from multiprocessing import Process
from pathlib import Path
from subprocess import call, check_output
from typing import *

import evalfen
from getFile import createDir, downloadName, getAvailableNames
from send import sendFile, sendNotification

STOCKFISH_DOWNLOAD = {
    "win32": "https://stockfishchess.org/files/stockfish-11-win.zip",
    "linux": "https://stockfishchess.org/files/stockfish-11-linux.zip",
    "linux32": "https://stockfishchess.org/files/stockfish-11-linux.zip",
    "darwin": "https://stockfishchess.org/files/stockfish-11-mac.zip"
}

STOCKFISH_LOCATION = {
    "win32": r"stockfish\stockfish-11-win\Windows\stockfish_20011801_x64_bmi2.exe",
    "linux": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_bmi2",
    "linux32": "stockfish/stockfish-11-linux/Linux/stockfish_20011801_x64_bmi2",
    "darwin": "stockfish/stockfish-11-mac/Mac/stockfish-11-"
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
    toadd = "bmi2"
    if sys.platform == "darwin" and \
        '-3' in check_output(["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"]).decode():
        toadd = "modern"
    return Path(os.getcwd()) / (STOCKFISH_LOCATION[sys.platform] + toadd)


def promptStockfish() -> Path:
    needsfish = "stockfish" not in os.listdir()
    if needsfish:
        print("Downloading stockfish")
        downloadStockfish()
    return findStockfish()

def getNumberThreads() -> int:
   return os.cpu_count()

def progressBar(percentage: float) -> str:
    numpound = round(percentage*10)
    numdash = 10-numpound
    return '[' + numpound*'#' + numdash*'-' + ']\t' + "%.2f" % (percentage*100) + "%"

def countOutput(count: int, length: int) -> None:
    print(progressBar(count/length), end='\r', flush=True)

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
    finallines = evalfen.lineCount(source)
    countOut = lambda c: countOutput(c, finallines)

    evalargs = (source, dest, 22, threads, amountlines, pathToStockfish, countOut)
    evaluate = Process(target=evalfen.main, args=evalargs)
    evaluate.start()

    print("Control c to quit")
    try:
        evaluate.join()
        print(dest)
        sendFile(promptName(), dest)
    except KeyboardInterrupt:
        evaluate.terminate()

    print("Done for now")


if __name__ == "__main__":
    main()
