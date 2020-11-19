import os
import shutil
import stat
import sys
import zipfile
from multiprocessing import freeze_support
from pathlib import Path
from subprocess import call

import cpuinfo


pwd = Path.cwd() / ".ChessContrib"


def get_engine_path():
    platform = sys.platform.replace("32", '')
    version = __get_engine_version()
    location = __DATA[platform][version]["file"]
    return (
        pwd / "engines" / "stockfish" / location
    )


def init():
    try:
        with open(get_engine_path(), 'rb') as fin:
            pass
    except FileNotFoundError:
        print("Downloading stockfish...")
        __create_dir(str(pwd))
        __download_stockfish()
        print("Downloaded stockfish")
    except PermissionError:
        pass


def __download_stockfish():
    version = __get_engine_version()
    platform = sys.platform.replace("32", '')
    link = __DATA[platform][version]["link"]
    call(["curl", "-o", "stockfish.zip", link])
    __unzip("stockfish.zip", str(pwd / "engines" / "stockfish"))
    os.remove("stockfish.zip")
    stockfish_executable = str(get_engine_path())
    if sys.platform != "win32":
        os.chmod(stockfish_executable, stat.S_IEXEC)


def __unzip(filepath: str, resultpath: str) -> None:
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(resultpath)



def __create_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        shutil.rmtree(path)
        os.mkdir(path)


# uses fancy multiprocessing, beware when compiling
def __get_engine_version():
    flags = cpuinfo.get_cpu_info()["flags"]
    if "bmi2" in flags:
        version = "bmi2"
    elif "popcnt" in flags:
        version = "popcnt"
    else:
        version = "64bit"
    return version


# Not in json file to package easier
__DATA = {
  "win": {
    "bmi2": {
      "link": "https://stockfishchess.org/files/stockfish_12_win_x64_bmi2.zip",
      "file": "stockfish_20090216_x64_bmi2.exe"
    },
    "popcnt": {
      "link": "https://stockfishchess.org/files/stockfish_12_win_x64_modern.zip",
      "file": "stockfish_20090216_x64_modern.exe"
    },
    "64bit": {
      "link": "https://stockfishchess.org/files/stockfish_12_win_x64.zip",
      "file": "stockfish_20090216_x64.exe"
    }
  },
  "linux": {
    "bmi2": {
      "link": "https://stockfishchess.org/files/stockfish_12_linux_x64_bmi2.zip",
      "file": "stockfish_20090216_x64_bmi2"
    },
    "popcnt": {
      "link": "https://stockfishchess.org/files/stockfish_12_linux_x64_modern.zip",
      "file": "stockfish_20090216_x64_modern"
    },
    "64bit": {
      "link": "https://stockfishchess.org/files/stockfish_12_linux_x64.zip",
      "file": "stockfish_20090216_x64"
    }
  },
  "darwin": {
    "bmi2": {
      "link": "https://stockfishchess.org/files/stockfish-11-mac.zip",
      "file": "stockfish-11-mac/Mac/stockfish-11-bmi2"
    },
    "popcnt": {
      "link": "https://stockfishchess.org/files/stockfish-11-mac.zip",
      "file": "stockfish-11-mac/Mac/stockfish-11-modern"
    },
    "64bit": {
      "link": "https://stockfishchess.org/files/stockfish-11-mac.zip",
      "file": "stockfish-11-mac/Mac/stockfish-11-64"
    }
  }
}
