__filename__ = "anomaly.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

import os


def _stationsAnomaly(year: int, stationsData: {},
                     baseline: [], stationIds: set) -> float:
    """Returns anomaly for the given stations for the given year
    """
    anomaly = 0.0
    hits = 0

    for id in stationIds:
        if id not in stationsData:
            continue
        if year not in stationsData[id]:
            continue
        monthData = stationsData[id][year]['month']
        for monthIndex in range(12):
            if not baseline[monthIndex]:
                continue
            if monthData[monthIndex]['av'] > -80:
                if monthData[monthIndex]['av'] < 80:
                    anomaly += \
                        monthData[monthIndex]['av'] - baseline[monthIndex]
                    hits += 1
    if hits > 0:
        return anomaly / float(hits)
    return None


def updateGridAnomalies(grid: [], stationsData: {},
                        startYear: int, endYear: int) -> int:
    """Calculates anomalies for each grid cell within a range of years
    """
    ctr = 0
    yearCtr = 0
    for gridCell in grid:
        gridCell['anomalies'] = {}
        if not gridCell['stationIds']:
            continue
        baseline = gridCell['baseline']
        stationIds = gridCell['stationIds']
        for year in range(startYear, endYear + 1, 1):
            gridCell['anomalies'][year] = \
                _stationsAnomaly(year, stationsData, baseline, stationIds)
            if gridCell['anomalies'][year] is not None:
                yearCtr += 1
            ctr += 1
    if yearCtr > 0:
        return int(yearCtr * 100 / float(ctr))
    return 0


def getGlobalAnomalies(grid: [],
                       startYear: int, endYear: int) -> {}:
    """Returns global anomalies in the given year range
    """
    result = {}
    for year in range(startYear, endYear + 1, 1):
        yearAnomaly = 0.0
        ctr = 0
        for gridCell in grid:
            if gridCell['anomalies'].get(year):
                yearAnomaly += gridCell['anomalies'][year]
                ctr += 1
        if ctr > 0:
            result[year] = yearAnomaly / float(ctr)
        else:
            result[year] = None
    return result


def plotGlobalAnomalies(grid: [],
                        startYear: int, endYear: int) -> None:
    """Plot anomalies graph
    """
    anomalies = getGlobalAnomalies(grid, startYear, endYear)
    series = []
    minimumTemp = 99999999
    maximumTemp = -99999999
    for year in range(startYear, endYear + 1, 1):
        series.append(anomalies[year])
        if anomalies[year] > maximumTemp:
            maximumTemp = anomalies[year]
        if anomalies[year] < minimumTemp:
            minimumTemp = anomalies[year]

    title = \
        "Global Temperature Anomalies " + \
        str(startYear) + ' - ' + str(endYear)
    subtitle = "Source https://www.ncei.noaa.gov/pub/data/ghcn/v4"
    Xlabel = 'Year'
    Ylabel = 'Average Temperature Anomaly (Celcius)'
    indent = 0.34
    vpos = 0.94
    imageWidth = 1000
    imageHeight = 1000
    plotName = 'global_anomalies'
    imageFormat = 'jpg'
    imageFormat2 = 'jpeg'
    filename = plotName + '.' + imageFormat
    scriptFilename = plotName + '.gnuplot'
    dataFilename = plotName + '.data'
    with open(dataFilename, 'w+') as fp:
        year = startYear
        for temperatureAnomaly in series:
            fp.write(str(year) + "    " + str(temperatureAnomaly) + '\n')
            year += 1
    script = \
        "reset\n" + \
        "set title \"" + title + "\"\n" + \
        "set label \"" + subtitle + "\" at screen " + \
        str(indent) + ", screen " + str(vpos) + "\n" + \
        "set yrange [" + str(minimumTemp) + ":" + \
        str(maximumTemp) + "]\n" + \
        "set xrange [" + str(startYear) + ":" + str(endYear) + "]\n" + \
        "set lmargin 9\n" + \
        "set rmargin 2\n" + \
        "set xlabel \"" + Xlabel + "\"\n" + \
        "set ylabel \"" + Ylabel + "\"\n" + \
        "set grid\n" + \
        "set key right bottom\n" + \
        "set terminal " + imageFormat2 + \
        " size " + str(imageWidth) + "," + str(imageHeight) + "\n" + \
        "set output \"" + filename + "\"\n" + \
        "plot \"" + dataFilename + "\" using 1:2 notitle with lines\n"
    with open(scriptFilename, 'w+') as fp:
        fp.write(script)
    os.system('gnuplot ' + scriptFilename)
