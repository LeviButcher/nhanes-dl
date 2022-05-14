from typing import Set, List
import pandas as pd
from urllib.error import HTTPError
from nhanes_dl.types import ContinuousNHANES, appendCodebooks, appendMortalities, \
    codebookURL, Codebook, Mortality, getAllCodebookDescriptions, joinCodebooks, \
    linkCodebookWithMortality, mortalityURL, \
    CodebookDownload, DownloadException, getYearsCodebookDescriptions


# Kinda think I should convert the return types to eithers...
# This would allow for better error handling and more explicit type signatures
# BUT then I insert functional dependencies into the python library... probably not a good idea

def downloadCodebook(year: ContinuousNHANES, codebook: str) -> Codebook:
    """
    Downloads a NHANSE codebook from the CDC website.
    Throws a DownloadException if the download fails, doesn't have a SEQN, or repeats SEQN multiple times
    """
    url = codebookURL(year, codebook)
    print(year, codebook)

    try:
        return Codebook(pd.read_sas(url, index="SEQN"))
    except HTTPError:
        raise DownloadException(
            f"Failed to download {codebook} for {year}\n{url}")
    except KeyError:
        raise DownloadException(f"No SEQN index - {url}")
    except Exception:
        raise DownloadException(f"Repeating SEQN rows - {url}")


def downloadCodebooks(cd: CodebookDownload) -> Codebook:
    # Should throw an exception whenever something fails to download
    """
    Return all CodeBooks within specified for the NHANES year
    """
    res = [downloadCodebook(cd.year, c) for c in cd.codebooks]

    return joinCodebooks(res)


def downloadAllCodebooksForYear(c: ContinuousNHANES) -> Codebook:
    """
    returns dataframe of all codebook data for a nhanes year
    """
    def handleDownloadCodebook(year: ContinuousNHANES, codebook: str) -> List[Codebook]:
        try:
            return [downloadCodebook(year, codebook)]
        except Exception:
            return []

    # desc = getYearsCodebookDescriptions(c)
    # # res = [y for (_, x) in desc.iterrows()
    # #        for y in handleDownloadCodebook(c, x.dataFile) if not y.empty]

    # # Gotta Change return types to denote failure
    # # NOTE: DATA IS TO LARGE TO MERGE TOGETHER
    # res = None
    # for (_, x) in desc.iterrows():
    #     y = handleDownloadCodebook(c, x.dataFile)
    #     if res is None and len(y) != 0:
    #         res = y[0]
    #     elif res is not None and len(y) != 0:
    #         code = y[0]
    #         print(f"res: {res.shape}")
    #         print(f"code: {code.shape}")

    #         allCols = res.columns.append(code.columns)
    #         cols = allCols.duplicated()[len(res.columns):]
    #         noDups = code.loc[:, ~cols]
    #         res = res.join(noDups, how="outer")

    return Codebook(pd.DataFrame())


def downloadAllCodebooks() -> Codebook:
    raise Exception("Not implemented yet")


def downloadCodebooksForYears(c: Set[CodebookDownload]) -> Codebook:
    """
    returns dataframe of appended codebook data for all CodebookDownloads
    """
    res = [downloadCodebooks(x) for x in c]

    return Codebook(appendCodebooks(res))


mortality_colspecs = [(1, 14), (15, 15), (16, 16), (17, 19), (20, 20),
                      (21, 21), (22, 22), (23, 26), (27, 34), (35, 42), (43, 45), (46, 48)]

mortality_widths = [e - (s-1) for s, e in mortality_colspecs]


def toUpperCase(xs: List[str]):
    return list(map(lambda l: l.upper(), xs))


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

    try:
        data = pd.read_fwf(url, widths=mortality_widths)
        data.columns = mortality_colnames
        return data.assign(SEQN=data.PUBLICID).drop(columns=drop_columns).apply(
            lambda x: pd.to_numeric(x, errors="coerce")).set_index("SEQN")
    except HTTPError:
        raise DownloadException(
            f"Failed to download mortality data for {year}\n{url}")


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
