__filename__ = "parseData.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"


def loadData(filename: str, startYear: int, endYear: int) -> ({}, {}):
    """Loads data from file
    """
    lines = []
    try:
        with open(filename, 'r') as fp:
            lines = fp.readlines()
    except BaseException:
        print('Unable to open ' + filename)
        return None, None
    years = {}
    stations = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if len(line) < 20:
            continue
        year = int(line[11:15])
        if year < 1800 or year > 2099:
            continue
        id = line[:10]
        element = line[15:19]
        month = []
        lineIndex = 20
        for monthIndex in range(12):
            value = float(line[lineIndex:lineIndex + 4]) / 100.0
            dmflag = line[lineIndex + 5:lineIndex + 6]
            qcflag = line[lineIndex + 6:lineIndex + 7]
            dsflag = line[lineIndex + 7:lineIndex + 8]
            month.append({
                "av": value,
                "dmflag": dmflag,
                "qcflag": qcflag,
                "dsflag": dsflag
            })
            lineIndex += 8
        if not stations.get(id):
            stations[id] = {}
        stations[id][year] = {
            'element': element,
            'month': month
        }
        if not years.get(year):
            years[year] = []
        years[year].append({
            'id': id,
            'element': element,
            'month': month
        })
    return stations, years
