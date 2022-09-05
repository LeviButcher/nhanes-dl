from typing import Set, List
import pandas as pd
from urllib.error import HTTPError, URLError
from nhanes_dl.types import ContinuousNHANES, appendCodebooks, appendMortalities, \
    codebookURL, Codebook, Mortality, getStartEndYear, joinCodebooks, \
    linkCodebookWithMortality, mortalityURL, \
    CodebookDownload, DownloadException, getYearsCodebookDescriptions, allContinuousNHANES
from nhanes_dl.utils import makeDirectoryIfNotExists, readOrUpdateCache


# Kinda think I should convert the return types to either...
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
    Downloads a NHANES codebook from the CDC website.
    Throws a DownloadException if the download fails, doesn't have a SEQN, or repeats SEQN multiple times
    """
    ignoreCodebooks = ["PAXMIN"]

    url = codebookURL(year, codebook)
    print(year, codebook)

    try:
        if any([codebook.startswith(ignore) for ignore in ignoreCodebooks]):
            raise DownloadException("Ignore codebook download")

        res = Codebook(pd.read_sas(url, index="SEQN"))

        if any(res.index.duplicated()):
            # May want to change to to roll up the Dataframe
            raise DownloadException(f"Repeating SEQN rows - {url}")
        return res
    except HTTPError:
        raise DownloadException(
            f"Failed to download {codebook} for {year}\n{url}")
    except URLError:
        raise DownloadException("Request timed out")
    except KeyError:
        raise DownloadException(f"No SEQN index - {url}")
    except OverflowError:
        raise DownloadException(f"A value is over maximum size")


def downloadCodebookWithRetry(year, codebook):
    """
    Download the codebook and retries it again if failed due to Network Error
    """
    url = codebookURL(year, codebook)
    try:
        return downloadCodebook(year, codebook)
    except DownloadException as de:
        mes = str(de)
        if (mes == "Request timed out") or (mes == f"Failed to download {codebook} for {year}\n{url}"):
            return downloadCodebook(year, codebook)

        raise DownloadException(f"Failed during retry of download")


def downloadCodebooks(cd: CodebookDownload) -> Codebook:
    # Should throw an exception whenever something fails to download
    """
    Return all CodeBooks within specified for the NHANES year
    """
    def handleDownload(year, codebook):
        try:
            return downloadCodebookWithRetry(year, codebook)
        except DownloadException:
            return []

    res = [handleDownload(cd.year, c)
           for c in cd.codebooks]
    res = [c for c in res if not isinstance(c, list)]

    return joinCodebooks(res)


def downloadAllCodebooksForYear(c: ContinuousNHANES) -> Codebook:
    """
    returns DataFrame of all codebook data for a NHANES year
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


# Download each nhanes code for that year, then cache the csv file in a directory
def buildNhanesYearCache(cacheDir: str, c: ContinuousNHANES, updateCache: bool = False) -> bool:
    makeDirectoryIfNotExists(cacheDir)
    description = getYearsCodebookDescriptions(c)
    dataFile = description.dataFile
    yearPath = nhanesYearSavePath(c)
    saveBase = f"{cacheDir}/{yearPath}"
    makeDirectoryIfNotExists(saveBase)

    for codebookName in dataFile:
        try:
            savePath = f"{saveBase}/{codebookName}.csv"
            readOrUpdateCache(
                savePath, lambda: downloadCodebook(c, codebookName), updateCache)
        except DownloadException:
            print("Failed Download")
    return True


def buildNhanesCache(cacheDir: str, updateCache: bool = False) -> bool:
    allSets = allContinuousNHANES()
    for year in allSets:
        buildNhanesYearCache(cacheDir, year, updateCache)
    return True


def readCacheOrDownloadCodebook(cacheDir: str, year: ContinuousNHANES, codebook: str,
                                updateCache: bool = False) -> pd.DataFrame:
    savePath = f"{cacheDir}/{codebookSavePath(year, codebook)}"
    saveDir = f"{cacheDir}/{nhanesYearSavePath(year)}"
    makeDirectoryIfNotExists(saveDir)

    try:
        return readOrUpdateCache(savePath,
                                 lambda: downloadCodebook(year, codebook),
                                 updateCache)
    except DownloadException:
        return


def readCacheOrDownloadAllCodebooks(cacheDir: str, year: ContinuousNHANES, updateCache: bool = False):
    description = getYearsCodebookDescriptions(year)
    dataFile = description.dataFile
    allCodebooks = [readCacheOrDownloadCodebook(cacheDir, year, x, updateCache)
                    for x in dataFile]
    return joinCodebooks(allCodebooks)


def readCacheOrDownloadNhanesYearCodebooks(cacheDir: str, years: Set[ContinuousNHANES], updateCache: bool = False):
    allResults = [readCacheOrDownloadAllCodebooks(
        cacheDir, year, updateCache) for year in years]
    return appendCodebooks(allResults)


def readCacheOrDownloadMortality(cacheDir: str, year: ContinuousNHANES, updateCache: bool = False):
    saveDir = f"{cacheDir}/{nhanesYearSavePath(year)}"
    savePath = f"{saveDir}/mortality.csv"
    try:
        return readOrUpdateCache(savePath,
                                 lambda: downloadMortality(year),
                                 updateCache)
    except DownloadException:
        return


def readCacheOrDownloadMortalityYears(cacheDir: str, years: Set[ContinuousNHANES], updateCache: bool = False):
    res = [readCacheOrDownloadMortality(
        cacheDir, y, updateCache) for y in years]
    return appendMortalities(res)


def readCacheOrDownloadAllCodebooksWithMortality(cacheDir: str, years: Set[ContinuousNHANES], updateCache: bool = False):
    codebooks = readCacheOrDownloadNhanesYearCodebooks(
        cacheDir, years, updateCache)
    mortality = readCacheOrDownloadMortalityYears(cacheDir, years, updateCache)
    return linkCodebookWithMortality(codebooks, mortality)


def nhanesYearSavePath(c: ContinuousNHANES):
    s, e = getStartEndYear(c)
    return f"{s}-{e}"


def codebookSavePath(c: ContinuousNHANES, codebookName: str):
    year = nhanesYearSavePath(c)
    return f"{year}/{codebookName}.csv"


def readCacheCodebook(cacheDir: str, year: ContinuousNHANES, codebook: str):
    savePath = f"{cacheDir}/{codebookSavePath(year, codebook)}"
    try:
        return pd.read_csv(savePath).set_index("SEQN")
    except Exception:
        print(f"Couldn't read cache - {savePath}")
        return None


def readCacheAllCodebooks(cacheDir: str, year: ContinuousNHANES):
    description = getYearsCodebookDescriptions(year)
    dataFile = description.dataFile
    res = [readCacheCodebook(cacheDir, year, codebook)
           for codebook in dataFile]
    res = [x for x in res if x is not None]
    return joinCodebooks(res)


def readCacheNhanesYears(cacheDir: str, years: Set[ContinuousNHANES]):
    res = [readCacheAllCodebooks(cacheDir, y) for y in years]
    return appendCodebooks(res)


def readCacheMortality(cacheDir: str, year: ContinuousNHANES):
    saveDir = f"{cacheDir}/{nhanesYearSavePath(year)}"
    savePath = f"{saveDir}/mortality.csv"
    try:
        return pd.read_csv(savePath).set_index("SEQN")
    except Exception:
        print(f"Couldn't read cache - {savePath}")
        return None


def readCacheMortalityYears(cacheDir: str, years: Set[ContinuousNHANES]):
    res = [readCacheMortality(cacheDir, y) for y in years]
    res = [x for x in res if x is not None]
    return appendMortalities(res)


def readCacheNhanesYearsWithMortality(cacheDir: str, years: Set[ContinuousNHANES]):
    codebooks = readCacheNhanesYears(cacheDir, years)
    mortality = readCacheMortalityYears(cacheDir, years)
    return linkCodebookWithMortality(codebooks, mortality)
