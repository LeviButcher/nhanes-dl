from nhanes_dl.types import ContinuousNHANES, allContinuousNHANES


if __name__ == "__main__":
    import nhanes_dl.download as dl
    cacheDir = "nhanes_cache"
    year = ContinuousNHANES.Fourth
    updateCache = False
    # years = allContinuousNHANES()
    years = [ContinuousNHANES.Fourth, ContinuousNHANES.Fifth]
    # dl.buildNhanesCache("nhanes_cache")
    res = dl.readCacheNhanesYearsWithMortality(cacheDir, years)
    print(res.describe())
