from src import download, types

# These are all intergrations tests


def test_downloadCodebook():
    res = download.downloadCodebook(types.ContinuousNHANES.Third, "DEMO_C")

    assert len(res) != 0
    # unlikely that that nhanes changes underlying data
    assert res.shape == (10122, 43)
    assert res.index.name == "SEQN"


def test_downloadCodebooks():
    conf = download.CodebookDownload(
        types.ContinuousNHANES.Third, "DEMO_C", "L16_C")

    res = download.downloadCodebooks(conf)

    assert len(res) != 0
    assert res.shape == (10122, 47)
    assert res.index.name == "SEQN"


def test_downloadCodebooks_morethenfive():
    conf = download.CodebookDownload(
        types.ContinuousNHANES.Third, "DEMO_C", "L16_C")

    res = download.downloadCodebooks(conf)

    assert len(res) != 0
    assert res.shape == (10122, 47)
    assert res.index.name == "SEQN"


def test_downloadCodebooksForYears():
    confs = {
        download.CodebookDownload(
            types.ContinuousNHANES.Third, "DEMO_C", "L16_C"),
        download.CodebookDownload(
            types.ContinuousNHANES.Fourth, "DEMO_D", "BMX_D")
    }
    res = download.downloadCodebooksForYears(confs)

    assert len(res) != 0
    assert res.shape == (20470, 74)


def test_downloadMortality():
    conf = types.ContinuousNHANES.Third
    res = download.downloadMortality(conf)
    assert len(res) != 0
    assert res.shape == (10121, 7)
    assert res.index.name == "SEQN"


def test_downloadMortalities():
    confs = {
        types.ContinuousNHANES.Third,
        types.ContinuousNHANES.Fourth
    }
    res = download.downloadMortalityForYears(confs)

    assert len(res) != 0
    assert res.shape == (20468, 7)


def test_downloadCodebookWithMortality():
    conf = types.ContinuousNHANES.Third
    res = download.downloadCodebookWithMortality(conf, "DEMO_C")

    assert len(res) != 0
    assert res.shape == (10122, 50)
    assert res.index.name == "SEQN"


def test_downloadCodebooksWithMortality():
    conf = download.CodebookDownload(
        types.ContinuousNHANES.Third, "DEMO_C", "L16_C")

    res = download.downloadCodebooksWithMortality(conf)

    assert len(res) != 0
    assert res.shape == (10122, 54)
    assert res.index.name == "SEQN"


def test_downloadCodebooksWithMortalityForYears():
    confs = {
        download.CodebookDownload(
            types.ContinuousNHANES.Third, "DEMO_C", "L16_C"),
        download.CodebookDownload(
            types.ContinuousNHANES.Fourth, "DEMO_D", "BMX_D")
    }

    res = download.downloadCodebooksWithMortalityForYears(confs)

    assert len(res) != 0
    assert res.shape == (20470, 81)
    assert res.index.name == "SEQN"
