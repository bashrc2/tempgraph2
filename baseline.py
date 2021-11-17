__filename__ = "baseline.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"


def _getBaselineForYear(id: str, stationsData: {}, year: int) -> []:
    """Returns the baseline for a given station id
    """
    baseline = [None] * 12
    if year not in stationsData[id]:
        return baseline
    monthData = stationsData[id][year]['month']
    for monthIndex in range(12):
        monthData2 = monthData[monthIndex]
        if monthData2['qcflag'] == 'M':
            # Flagged as error
            continue
        if monthData2['av'] > -80:
            if monthData2['av'] < 80:
                baseline[monthIndex] = monthData2['av']
    return baseline


def _getBaseline(id: str, stationsData: {},
                 startYear: int, endYear: int) -> []:
    """Returns the baseline for a given station id
    """
    if id not in stationsData:
        return [None] * 12

    if startYear == endYear:
        return _getBaselineForYear(id, stationsData, startYear)
    else:
        baseline = [0.0] * 12
        hits = [0] * 12
        for year in range(startYear, endYear, 1):
            if year not in stationsData[id]:
                continue
            monthData = stationsData[id][year]['month']
            for monthIndex in range(12):
                monthData2 = monthData[monthIndex]
                if monthData2['qcflag'] == 'M':
                    # Flagged as error
                    continue
                if monthData2['av'] > -80:
                    if monthData2['av'] < 80:
                        baseline[monthIndex] += monthData2['av']
                        hits[monthIndex] += 1

        for monthIndex in range(12):
            if hits[monthIndex] > 0:
                baseline[monthIndex] /= float(hits[monthIndex])
            else:
                baseline[monthIndex] = None
    return baseline


def _baselineForStations(stationsData: {},
                         startYear: int, endYear: int,
                         stationIds: set) -> []:
    """Returns a baseline for the given range of years
    and the given station ids
    """
    if not stationIds:
        return [None] * 12, False

    baseline = [0.0] * 12
    hits = [0] * 12
    for id in stationIds:
        stationBaseline = _getBaseline(id, stationsData, startYear, endYear)
        for monthIndex in range(12):
            if stationBaseline[monthIndex] is not None:
                baseline[monthIndex] += stationBaseline[monthIndex]
                hits[monthIndex] += 1

    for monthIndex in range(12):
        if hits[monthIndex] > 0:
            baseline[monthIndex] /= float(hits[monthIndex])
        else:
            baseline[monthIndex] = None

    return baseline, True


def updateGridBaselines(grid: [], stationsData: {},
                        startYear: int, endYear: int) -> int:
    """Calculates reference baselines for each grid cell
    """
    ctr = 0
    for gridCell in grid:
        if gridCell['stationIds']:
            gridCell['baseline'], hasData = \
                _baselineForStations(stationsData, startYear, endYear,
                                     gridCell['stationIds'])
            if hasData:
                ctr += 1
    return ctr
