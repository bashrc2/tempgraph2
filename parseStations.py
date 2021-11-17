__filename__ = "parseStations.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

from grid import getClosestGridIndex


def loadStationLocations(filename: str, grid: []) -> {}:
    """Loads station locations from inv file
    """
    lines = []
    try:
        with open(filename, 'r') as fp:
            lines = fp.readlines()
    except BaseException:
        print('Unable to open ' + filename)
        return None
    stationLocations = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if len(line) < 38:
            continue
        id = line[:10]
        latitude = float(line[11:19])
        longitude = float(line[20:29])
        altitude = float(line[30:37])
        name = line[38:].lower().title()
        gridIndex = getClosestGridIndex(longitude, latitude, grid)
        if id not in grid[gridIndex]['stationIds']:
            grid[gridIndex]['stationIds'].add(id)
        stationLocations[id] = {
            'gridIndex': gridIndex,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'name': name
        }
    return stationLocations


def saveStationLocationsAsKML(stationLocations: {}, filename: str) -> None:
    """Save station locations in KML format for visualization
    """
    kmlStr = \
        "<?xml version=\"1.0\" encoding='UTF-8'?>\n" + \
        "<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n" + \
        "<Document>\n"
    for id, item in stationLocations.items():
        kmlStr += \
            "  <Placemark>\n" + \
            "    <name>" + str(item['name']) + "</name>\n" + \
            "    <description>" + str(item['latitude']) + \
            ' ' + str(item['longitude']) + '</description>\n' + \
            "    <Point>\n" + \
            "      <coordinates>" + str(item['longitude']) + "," + \
            str(item['latitude']) + "," + str(item['altitude']) + \
            "</coordinates>\n" + \
            "    </Point>\n" + \
            "  </Placemark>\n"
    kmlStr += \
        "</Document>\n" + \
        "</kml>\n"
    with open(filename, 'w+') as fp:
        fp.write(kmlStr)
