from jinja2 import UndefinedError
from nhanes_dl.types import ContinuousNHANES, appendCodebooks, appendMortalities, codebookURL, Codebook, Mortality, joinCodebooks, linkCodebookWithMortality, mortalityURL
import pandas as pd
from typing import Set


# Might be good to make this into a tuple
class CodebookDownload:
    year: ContinuousNHANES
    codebooks: Set[str]

    def __init__(self, year: ContinuousNHANES, *codebooks: str):
        self.year = year
        self.codebooks = set(codebooks)


# Every download function could take in a downloader to make testsing easier


def downloadCodebook(year: ContinuousNHANES, codebook: str) -> Codebook:
    url = codebookURL(year, codebook)
    print(url)
    return Codebook(pd.read_sas(url, index="SEQN"))


def downloadCodebooks(cd: CodebookDownload) -> Codebook:
    # Throw an exception whenever something fails to download
    """
    Return all CodeBooks within specified for the NHANES year
    """
    res = [downloadCodebook(cd.year, c) for c in cd.codebooks]

    return joinCodebooks(res)


def downloadAllCodebooks(c: ContinuousNHANES) -> Codebook:
    # Might have problem here with activity data and getting all codebook names
    """
    returns dataframe of all codebook data for a nhanes year
    """
    raise UndefinedError("Not implemented yet")


def downloadCodebooksForYears(c: Set[CodebookDownload]) -> Codebook:
    """
    returns dataframe of appended codebook data for all CodebookDownloads
    """
    res = [downloadCodebooks(x) for x in c]

    return Codebook(appendCodebooks(res))


mortality_colspecs = [(1, 14), (15, 15), (16, 16), (17, 19), (20, 20),
                      (21, 21), (22, 22), (23, 26), (27, 34), (35, 42), (43, 45), (46, 48)]

mortality_widths = [e - (s-1) for s, e in mortality_colspecs]


def toUpperCase(l):
    return list(map(lambda l: l.upper(), l))


mortality_colnames = toUpperCase(["publicid",
                                  "eligstat",
                                  "mortstat",
                                  "ucod_leading",
                                  "diabetes",
                                  "hyperten",
                                  "dodqtr",
                                  "dodyear",
                                  "wgt_new",
                                  "sa_wgt_new",
                                  "permth_int",
                                  "permth_exm"
                                  ])

drop_columns = toUpperCase(["publicid",
                            "dodqtr",
                            "dodyear",
                            "wgt_new",
                            "sa_wgt_new"])


def downloadMortality(year: ContinuousNHANES) -> Mortality:
    """
    returns dataframe of the ContinuousNHANES mortality data
    """

    url = mortalityURL(year)
    data = pd.read_fwf(url, widths=mortality_widths)
    data.columns = mortality_colnames
    return data.assign(SEQN=data.PUBLICID).drop(columns=drop_columns).apply(
        lambda x: pd.to_numeric(x, errors="coerce")).set_index("SEQN")


def downloadMortalityForYears(years: Set[ContinuousNHANES]) -> Mortality:
    """
    returns dataframe of the ContinuousNHANES mortality data of the years passed in
    """
    res = [downloadMortality(x) for x in years]
    return appendMortalities(res)


def downloadCodebookWithMortality(year: ContinuousNHANES, codebook: str) -> Codebook:
    """

    """
    book = downloadCodebook(year, codebook)
    mort = downloadMortality(year)

    return linkCodebookWithMortality(book, mort)


def downloadCodebooksWithMortality(c: CodebookDownload) -> Codebook:
    """
    returns dataframe of the ContinuousNHANES mortality data of the years passed in
    """
    book = downloadCodebooks(c)
    mort = downloadMortality(c.year)

    return linkCodebookWithMortality(book, mort)


def downloadCodebooksWithMortalityForYears(c: Set[CodebookDownload]) -> Codebook:
    """
    returns dataframe of the ContinuousNHANES mortality data of the years passed in
    """
    years = {x.year for x in c}
    book = downloadCodebooksForYears(c)
    mort = downloadMortalityForYears(years)

    return linkCodebookWithMortality(book, mort)
