import pytest
from nhanes_dl import download, types

# These are all intergrations tests


def test_downloadCodebook():
    res = download.downloadCodebook(types.ContinuousNHANES.Fourth, "DEMO_D")

    assert len(res) != 0
    # unlikely that that nhanes changes underlying data
    assert res.shape == (10122, 43)
    assert res.index.name == "SEQN"


def test_downloadCodebooks():
    conf = download.CodebookDownload(
        types.ContinuousNHANES.Fourth, "DEMO_D", "L16_D")

    res = download.downloadCodebooks(conf)

    assert len(res) != 0
    assert res.shape == (10122, 47)
    assert res.index.name == "SEQN"


def test_downloadCodebooks_morethenfive():
    conf = download.CodebookDownload(
        types.ContinuousNHANES.Fourth, "DEMO_D", "L16_D")

    res = download.downloadCodebooks(conf)

    assert len(res) != 0
    assert res.shape == (10122, 47)
    assert res.index.name == "SEQN"


def test_downloadCodebooksForYears():
    confs = {
        download.CodebookDownload(
            types.ContinuousNHANES.Fourth, "DEMO_D", "L16_D"),
        download.CodebookDownload(
            types.ContinuousNHANES.Fourth, "DEMO_D", "BMX_D")
    }
    res = download.downloadCodebooksForYears(confs)

    assert len(res) != 0
    assert res.shape == (20470, 74)
    assert res.index.name == "SEQN"


def test_downloadMortality():
    conf = types.ContinuousNHANES.Fourth
    res = download.downloadMortality(conf)
    assert len(res) != 0
    assert res.shape == (10121, 7)
    assert res.index.name == "SEQN"


def test_downloadMortalities():
    confs = {
        types.ContinuousNHANES.Fourth,
        types.ContinuousNHANES.Fourth
    }
    res = download.downloadMortalityForYears(confs)

    assert len(res) != 0
    assert res.shape == (20468, 7)


def test_downloadCodebookWithMortality():
    conf = types.ContinuousNHANES.Fourth
    res = download.downloadCodebookWithMortality(conf, "DEMO_D")

    assert len(res) != 0
    assert res.shape == (10122, 50)
    assert res.index.name == "SEQN"


def test_downloadCodebooksWithMortality():
    conf = download.CodebookDownload(
        types.ContinuousNHANES.Fourth, "DEMO_D", "L16_D")

    res = download.downloadCodebooksWithMortality(conf)

    assert len(res) != 0
    assert res.shape == (10122, 54)
    assert res.index.name == "SEQN"


def test_downloadCodebooksWithMortalityForYears():
    confs = {
        download.CodebookDownload(
            types.ContinuousNHANES.Fourth, "DEMO_D", "L16_D"),
        download.CodebookDownload(
            types.ContinuousNHANES.Fourth, "DEMO_D", "BMX_D")
    }

    res = download.downloadCodebooksWithMortalityForYears(confs)

    assert len(res) != 0
    assert res.shape == (20470, 81)
    assert res.index.name == "SEQN"


def test_downloadCodebooksForYears_complex():
    downloadConfig = {
        download.CodebookDownload(types.ContinuousNHANES.Fourth,
                                  "TCHOL_D", "TRIGLY_D", "HDL_D", "GLU_D", "CDQ_D",
                                  "DIQ_D", "BPQ_D", "BMX_D", "DEMO_D", "BPX_D"),
        download.CodebookDownload(types.ContinuousNHANES.Fifth,
                                  "TCHOL_E", "TRIGLY_E", "HDL_E", "GLU_E", "CDQ_E",
                                  "DIQ_E", "BPQ_E", "BMX_E", "DEMO_E", "BPX_E"),
        download.CodebookDownload(types.ContinuousNHANES.Sixth,
                                  "TCHOL_F", "TRIGLY_F", "HDL_F", "GLU_F", "CDQ_F",
                                  "DIQ_F", "BPQ_F", "BMX_F", "DEMO_F", "BPX_F"),
        download.CodebookDownload(types.ContinuousNHANES.Seventh,
                                  "TCHOL_G", "TRIGLY_G", "HDL_G", "GLU_G", "CDQ_G",
                                  "DIQ_G", "BPQ_G", "BMX_G", "DEMO_G", "BPX_G"),
        download.CodebookDownload(types.ContinuousNHANES.Eighth,
                                  "TCHOL_H", "TRIGLY_H", "HDL_H", "GLU_H", "CDQ_H",
                                  "DIQ_H", "BPQ_H", "BMX_H", "DEMO_H", "BPX_H"),
    }

    res = download.downloadCodebooksForYears(downloadConfig)

    assert len(res) != 0
    assert res.index.name == "SEQN"
    assert res.shape == (50965, 235)


def test_downloadCodebook_ThrowsDownloadException():
    year = types.ContinuousNHANES.Fifth
    codebook = "FAKEBOOK"
    url = types.codebookURL(year, codebook)
    with pytest.raises(download.DownloadException) as de:
        download.downloadCodebook(year, codebook)
    assert de.value.args[0] == f"Failed to download {codebook} for {year}\n{url}"


def test_downloadMortality_ThrowsDownloadException():
    year = types.ContinuousNHANES.Tenth
    url = types.mortalityURL(year)
    with pytest.raises(download.DownloadException) as de:
        download.downloadMortality(year)
    assert de.value.args[0] == f"Failed to download mortality data for {year}\n{url}"


def test_downloadAllCodebooksForYear():
    res = download.downloadAllCodebooksForYear(types.ContinuousNHANES.Fourth)
    print(res)
    print(res.index.duplicated())
    assert len(res) != 0


def test_downloadAllCodebooks():
    res = download.downloadAllCodebooks()
    print(res.shape)
    assert len(res) != 0


def test_downloadAllCodebooksWithMortalityForYears():
    res = download.downloadAllCodebooksWithMortalityForYears(
        types.allContinuousNHANES())
    print(res)
    assert len(res) != 0

# def test_custom():
#     res = download.downloadAllCodebooksForYear(types.ContinuousNHANES.Tenth)
#     assert len(res) != 0
