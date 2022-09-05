import pandas as pd
from nhanes_dl import types


def test_allYears():
    res = types.allYears()
    expected = {(2005, 2006), (2007, 2008), (2009, 2010),
                (2011, 2012), (2013, 2014), (2015, 2016), (2017, 2018)}

    assert len(res) == len(expected)
    assert all([year in expected for year in res])


def test_codebookURL():
    year = types.ContinuousNHANES.Fourth
    codebook = "LIB"
    expected = "https://wwwn.cdc.gov/Nchs/NHANES/2005-2006/LIB.XPT"
    res = types.codebookURL(year, codebook)

    assert res != ""
    assert expected == res


def test_mortalityURL():
    set = types.ContinuousNHANES.Fourth
    expected = \
        "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/NHANES_2005_2006_MORT_2019_PUBLIC.dat"
    res = types.mortalityURL(set)

    assert res != ""
    assert expected == res


def test_joinCodebooks():
    codebooks = map(types.Codebook, [
        pd.DataFrame({"SEQN": [1, 2, 3, 4], "A": [
                     5, 6, 7, 8]}).set_index("SEQN"),
        pd.DataFrame({"SEQN": [1, 2, 3, 4], "B": [9, 10, 11, 12]}).set_index("SEQN")])

    res = types.joinCodebooks(list(codebooks))
    print(res)
    assert res.shape == (4, 2)
    assert res.index.name == "SEQN"


def test_joinCodebooks_Complex():
    codebooks = map(types.Codebook, [
        pd.DataFrame({"SEQN": [1, 3, 4], "A": [
                     5, 6, 7]}).set_index("SEQN"),
        pd.DataFrame({"SEQN": [1, 3, 5, 10, 12], "B": [
                     9, 10, 11, 12, 13]}).set_index("SEQN"),
        pd.DataFrame({"SEQN": [22, 23, 1, 5], "C": [4, 4, 4, 4]}).set_index("SEQN")])

    res = types.joinCodebooks(list(codebooks))
    print(res)
    assert res.shape == (8, 3)
    assert res.index.name == "SEQN"


def test_appendCodebooks():
    codebooks = map(types.Codebook, [
        pd.DataFrame({"SEQN": [1, 2, 3, 4], "A": [
                     5, 6, 7, 8]}).set_index("SEQN"),
        pd.DataFrame({"SEQN": [5, 6, 7, 8], "B": [9, 10, 11, 12]}).set_index("SEQN")])

    res = types.appendCodebooks(list(codebooks))
    print(res)
    assert res.shape == (8, 2)
    assert res.index.name == "SEQN"


def test_getYearsCodebookDescriptions():
    # 'codebookType', 'startYear', 'endYear', 'name', 'docFile',
    # 'docFileLink', 'dataFile', 'dataFileLink', 'published'
    year = types.ContinuousNHANES.Fourth
    res = types.getYearsCodebookDescriptions(year)
    (s, e) = types.getStartEndYear(year)
    print(res.columns)
    assert len(res) != 0
    assert all(res.startYear == s)
    assert res.shape == (136, 9)
