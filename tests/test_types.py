import pandas as pd
from src import types


def test_allYears():
    res = types.allYears()
    expected = [(1999, 2000), (2001, 2002), (2003, 2004),
                (2005, 2006), (2007, 2008), (2009, 2010),
                (2011, 2012), (2013, 2014), (2015, 2016),
                (2017, 2018), (2019, 2020), (2021, 2022)]

    assert res == expected


def test_codebookURL():
    set = types.ContinuousNHANES.First
    codebook = "LIB"
    expected = "https://wwwn.cdc.gov/Nchs/Nhanes/1999-2000/LIB.XPT"
    res = types.codebookURL(set, codebook)

    assert res != ""
    assert expected == res


def test_mortalityURL():
    set = types.ContinuousNHANES.First
    expected = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/NHANES_1999_2000_MORT_2015_PUBLIC.dat"
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


def test_appendCodebooks():
    codebooks = map(types.Codebook, [
        pd.DataFrame({"SEQN": [1, 2, 3, 4], "A": [
                     5, 6, 7, 8]}).set_index("SEQN"),
        pd.DataFrame({"SEQN": [5, 6, 7, 8], "B": [9, 10, 11, 12]}).set_index("SEQN")])

    res = types.appendCodebooks(list(codebooks))
    print(res)
    assert res.shape == (8, 2)
    assert res.index.name == "SEQN"
