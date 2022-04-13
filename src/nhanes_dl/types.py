from enum import IntEnum
from typing import Tuple, List,  NewType, Callable
import pandas as pd


class ContinuousNHANES(IntEnum):
    """
        Represents the different Datasets of Continuous NHANES
    """
    First = 1999
    Second = 2001
    Third = 2003
    Fourth = 2005
    Fifth = 2007
    Sixth = 2009
    Seventh = 2011
    Eighth = 2013
    Ninth = 2015
    Tenth = 2017
    Eleveth = 2019
    Twelfth = 2021


Codebook = NewType('Codebook', pd.DataFrame)
Mortality = NewType('Mortality', pd.DataFrame)
LinkedDataset = NewType('LinkedDataset', pd.DataFrame)
Downloader = Callable[[str], pd.DataFrame]


def allSets() -> List[ContinuousNHANES]:
    return [x for x in ContinuousNHANES]


def codebookURL(set: ContinuousNHANES, codebookName: str) -> str:
    (s, e) = getStartEndYear(set)
    return f"https://wwwn.cdc.gov/Nchs/Nhanes/{s}-{e}/{codebookName}.XPT"


def mortalityURL(set: ContinuousNHANES) -> str:
    (s, e) = getStartEndYear(set)
    return f"https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/NHANES_{s}_{e}_MORT_2015_PUBLIC.dat"


def allYears() -> List[Tuple[int, int]]:
    return [getStartEndYear(x) for x in allSets()]


def getStartEndYear(c: ContinuousNHANES) -> Tuple[int, int]:
    y = c.value
    return (y, y + 1)


def getCodebookNames(c: ContinuousNHANES) -> List[str]:
    return [""]


def joinCodebooks(codebooks: List[Codebook]) -> Codebook:
    return Codebook(pd.concat(codebooks, axis=1))


def appendCodebooks(codebooks: List[Codebook]) -> Codebook:
    # Some codebooks may have repeat columns, have to remove them in order to append codebooks safely
    nodups = [x.loc[:, ~x.columns.duplicated()] for x in codebooks]

    return Codebook(pd.concat(nodups))


def appendMortalities(mortalities: List[Mortality]) -> Mortality:
    return Mortality(pd.concat(mortalities))


def linkCodebookWithMortality(code: Codebook, mort: Mortality) -> Codebook:

    # mortality has a record for every person BUT the codebook does not
    # This is why a outer join is necessary
    return Codebook(code.join(mort, how="outer"))
