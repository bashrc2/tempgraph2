__filename__ = "parseStations.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

from grid import get_closest_grid_index


def load_station_locations(filename: str, grid: []) -> {}:
    """Loads station locations from inv file
    """
    lines = []
    try:
        with open(filename, 'r') as fp_loc:
            lines = fp_loc.readlines()
    except BaseException:
        print('Unable to open ' + filename)
        return None
    station_locations = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if len(line) < 38:
            continue
        sid = line[:10]
        latitude = float(line[11:19])
        longitude = float(line[20:29])
        altitude = float(line[30:37])
        name = line[38:].lower().title()
        grid_index = get_closest_grid_index(longitude, latitude, grid)
        if sid not in grid[grid_index]['station_ids']:
            grid[grid_index]['station_ids'].add(sid)
        station_locations[sid] = {
            'grid_index': grid_index,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'name': name
        }
    return station_locations


def save_station_locations_as_kml(station_locations: {},
                                  filename: str) -> None:
    """Save station locations in KML format for visualization
    """
    kml_str = \
        "<?xml version=\"1.0\" encoding='UTF-8'?>\n" + \
        "<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n" + \
        "<Document>\n"
    for _, item in station_locations.items():
        kml_str += \
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
    kml_str += \
        "</Document>\n" + \
        "</kml>\n"
    with open(filename, 'w+') as fp_kml:
        fp_kml.write(kml_str)
