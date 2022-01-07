__filename__ = "parseData.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"


def load_data(filename: str, start_year: int, end_year: int) -> ({}, {}):
    """Loads data from file
    """
    lines = []
    try:
        with open(filename, 'r') as fp_load:
            lines = fp_load.readlines()
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
        sid = line[:10]
        element = line[15:19]
        month = []
        line_index = 20
        for _ in range(12):
            value = float(line[line_index:line_index + 4]) / 100.0
            dmflag = line[line_index + 5:line_index + 6]
            qcflag = line[line_index + 6:line_index + 7]
            dsflag = line[line_index + 7:line_index + 8]
            month.append({
                "av": value,
                "dmflag": dmflag,
                "qcflag": qcflag,
                "dsflag": dsflag
            })
            line_index += 8
        if not stations.get(sid):
            stations[sid] = {}
        stations[sid][year] = {
            'element': element,
            'month': month
        }
        if not years.get(year):
            years[year] = []
        years[year].append({
            'id': sid,
            'element': element,
            'month': month
        })
    return stations, years
