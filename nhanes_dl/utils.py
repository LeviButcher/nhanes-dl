from typing import Callable
import pandas as pd
from os.path import exists


def makeDirectoryIfNotExists(directory: str) -> bool:
    import os

    try:
        os.mkdir(directory)
        return True

    except:
        return False


def readOrUpdateCache(cachePath: str, getDataframe: Callable[[], pd.DataFrame],
                      updateCache: bool = False) -> pd.DataFrame:
    if exists(cachePath) and not updateCache:
        print(f"{cachePath} - already exists")
        return pd.read_csv(cachePath, low_memory=False)

    else:
        res = getDataframe()
        res.to_csv(cachePath)
        return res
