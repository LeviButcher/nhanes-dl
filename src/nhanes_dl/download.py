from typing import Set, List
import pandas as pd
from urllib.error import HTTPError
from nhanes_dl.types import ContinuousNHANES, appendCodebooks, appendMortalities, \
    codebookURL, Codebook, Mortality, joinCodebooks, \
    linkCodebookWithMortality, mortalityURL, \
    CodebookDownload, DownloadException, getYearsCodebookDescriptions, allContinuousNHANES


# Kinda think I should convert the return types to eithers...
# This would allow for better error handling and more explicit type signatures
# BUT then I insert functional dependencies into the python library... probably not a good idea

def toUpperCase(xs: List[str]):
    return list(map(lambda l: l.upper(), xs))


mortalityColumnSpecs = [(1, 14), (15, 15), (16, 16),
                        (17, 19), (20, 20), (21, 21),
                        (22, 22), (23, 26), (27, 34),
                        (35, 42), (43, 45), (46, 48)]

mortalityWidths = [e - (s-1) for s, e in mortalityColumnSpecs]


allMortalityColumns = toUpperCase(["publicid", "eligstat", "mortstat", "ucod_leading", "diabetes",
                                   "hyperten", "dodqtr", "dodyear", "wgt_new", "sa_wgt_new", "permth_int", "permth_exm"
                                   ])

toDropColumns = toUpperCase(
    ["publicid", "dodqtr", "dodyear", "wgt_new", "sa_wgt_new"])


def getMortalityColumns() -> List[str]:
    return [x for x in allMortalityColumns if x not in toDropColumns]


def downloadCodebook(year: ContinuousNHANES, codebook: str) -> Codebook:
    """
    Downloads a NHANSE codebook from the CDC website.
    Throws a DownloadException if the download fails, doesn't have a SEQN, or repeats SEQN multiple times
    """
    url = codebookURL(year, codebook)
    print(year, codebook)

    try:
        res = Codebook(pd.read_sas(url, index="SEQN"))
        if any(res.index.duplicated()):
            # May want to change to to roll up the dataframe
            raise DownloadException(f"Repeating SEQN rows - {url}")
        return res
    except HTTPError:
        raise DownloadException(
            f"Failed to download {codebook} for {year}\n{url}")
    except KeyError:
        raise DownloadException(f"No SEQN index - {url}")
    except OverflowError:
        raise DownloadException(f"A value is over maximum size")


def downloadCodebooks(cd: CodebookDownload) -> Codebook:
    # Should throw an exception whenever something fails to download
    """
    Return all CodeBooks within specified for the NHANES year
    """
    def handleDownload(year, codebook):
        try:
            return downloadCodebook(year, codebook)
        except DownloadException:
            return []

    res = [handleDownload(cd.year, c)
           for c in cd.codebooks]
    res = [c for c in res if not isinstance(c, list)]

    return joinCodebooks(res)


def downloadAllCodebooksForYear(c: ContinuousNHANES) -> Codebook:
    """
    returns DataFrame of all codebook data for a nhanes year
    """
    desc = getYearsCodebookDescriptions(c)
    toDownload = CodebookDownload(c, *desc.dataFile)
    return downloadCodebooks(toDownload)


def downloadAllCodebooksForYears(c: Set[ContinuousNHANES]) -> Codebook:
    res = [downloadAllCodebooksForYear(y) for y in c]
    return appendCodebooks(res)


def downloadAllCodebooks() -> Codebook:
    return downloadAllCodebooksForYears(allContinuousNHANES())


def downloadCodebooksForYears(c: Set[CodebookDownload]) -> Codebook:
    """
    returns DataFrame of appended codebook data for all CodebookDownloads
    """
    res = [downloadCodebooks(x) for x in c]

    return Codebook(appendCodebooks(res))


def downloadMortality(year: ContinuousNHANES) -> Mortality:
    """
    returns DataFrame of the ContinuousNHANES mortality data
    """

    url = mortalityURL(year)

    try:
        data = pd.read_fwf(url, widths=mortalityWidths)
        data.columns = allMortalityColumns
        return data.assign(SEQN=data.PUBLICID).drop(columns=toDropColumns).apply(
            lambda x: pd.to_numeric(x, errors="coerce")).set_index("SEQN")
    except HTTPError:
        raise DownloadException(
            f"Failed to download mortality data for {year}\n{url}")


def downloadMortalityForYears(years: Set[ContinuousNHANES]) -> Mortality:
    """
    returns DataFrame of the ContinuousNHANES mortality data of the years passed in
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
    returns DataFrame of the ContinuousNHANES mortality data of the years passed in
    """
    book = downloadCodebooks(c)
    mort = downloadMortality(c.year)

    return linkCodebookWithMortality(book, mort)


def downloadCodebooksWithMortalityForYears(c: Set[CodebookDownload]) -> Codebook:
    """
    returns DataFrame of the ContinuousNHANES mortality data of the years passed in
    """
    years = {x.year for x in c}
    book = downloadCodebooksForYears(c)
    mort = downloadMortalityForYears(years)

    return linkCodebookWithMortality(book, mort)


def downloadAllCodebooksWithMortalityForYears(c: Set[ContinuousNHANES]) -> Codebook:
    codebooks = downloadAllCodebooksForYears(c)
    mortality = downloadMortalityForYears(c)

    return linkCodebookWithMortality(codebooks, mortality)
