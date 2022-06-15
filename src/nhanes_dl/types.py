from enum import IntEnum
from typing import Tuple, List,  NewType, Callable, Set
import pandas as pd


class ContinuousNHANES(IntEnum):
    """
        Represents the different Datasets of Continuous NHANES
    """
    # First = 1999
    # Second = 2001
    # Third = 2003
    Fourth = 2005
    Fifth = 2007
    Sixth = 2009
    Seventh = 2011
    Eighth = 2013
    Ninth = 2015
    Tenth = 2017
    # Eleventh = 2019
    # Twelfth = 2021


Codebook = NewType('Codebook', pd.DataFrame)
Mortality = NewType('Mortality', pd.DataFrame)
LinkedDataset = NewType('LinkedDataset', pd.DataFrame)
Downloader = Callable[[str], pd.DataFrame]
CodebookDescription = NewType('CodebookDescription', pd.DataFrame)


def codebooks(year: ContinuousNHANES) -> List[str]:
    """
    Returns all valid codebooks for a Continuous NHANES year
    (Only returns codebooks that are safe to join together. i.e not the activity data)
    """
    # How Can I make this work?

    # OPTIONS
    # 1. Hand Type it out :/
    # 2. Use the scraper data to query csv file and return all

    return [""]


commonCodebooks = []
firstYearCodebooks = []


def allContinuousNHANES() -> Set[ContinuousNHANES]:
    return set([x for x in ContinuousNHANES])


def codebookURL(year: ContinuousNHANES, codebookName: str) -> str:
    (s, e) = getStartEndYear(year)
    return f"https://wwwn.cdc.gov/Nchs/Nhanes/{s}-{e}/{codebookName}.XPT"


def mortalityURL(year: ContinuousNHANES) -> str:
    (s, e) = getStartEndYear(year)
    return f"https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/NHANES_{s}_{e}_MORT_2019_PUBLIC.dat"


def allYears() -> List[Tuple[int, int]]:
    return [getStartEndYear(x) for x in allContinuousNHANES()]


def getStartEndYear(c: ContinuousNHANES) -> Tuple[int, int]:
    y = c.value
    return (y, y + 1)


def getCodebookNames(c: ContinuousNHANES) -> List[str]:
    return [""]


def joinCodebooks(codebooks: List[Codebook]) -> Codebook:
    # Can overrun memory when large dataframes are passed in
    # If you use join directly with huge lists

    return Codebook(pd.concat(codebooks, axis=1))
    # x = codebooks[0]
    # for y in codebooks[1:]:
    #     # Have to remove any columns that may be repeated in y
    #     allCols = x.columns.append(y.columns)
    #     cols = allCols.duplicated()[len(x.columns):]
    #     noDups = y.loc[:, ~cols]
    #     x = x.join(noDups, how="outer")

    # return x  # type: ignore


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


class CodebookDownload:
    year: ContinuousNHANES
    codebooks: Set[str]

    def __init__(self, year: ContinuousNHANES, *codebooks: str):
        self.year = year
        self.codebooks = set(codebooks)


class DownloadException(Exception):
    pass


def getYearsCodebookDescriptions(year: ContinuousNHANES) -> CodebookDescription:
    desc = getAllCodebookDescriptions()
    (s, e) = getStartEndYear(year)
    inYear = (desc.startYear == s) & (desc.endYear == e)
    return CodebookDescription(desc.loc[inYear, :])


def getAllCodebookDescriptions() -> CodebookDescription:
    url = "https://raw.githubusercontent.com/LeviButcher/nhanes-scraper/master/results/nhanes_codebooks.csv"
    # Removes any duplicate rows, if any exist
    res = pd.read_csv(url).drop_duplicates(
        subset=["startYear", "endYear", "dataFile"])

    return CodebookDescription(res)
