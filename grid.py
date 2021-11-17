__filename__ = "grid.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

import math


def _3DtoLatLong(x: float, y: float, z: float) -> (float, float):
    """Converts 3D coordinate to latitude and longitude
    """
    latitude = math.asin(z) * 180 / math.pi
    longitude = math.atan2(y, x) * 180 / math.pi
    return latitude, longitude


def _latLongTo3D(longitude: float, latitude: float) -> (float, float, float):
    """Convert latitude and longitude into a 3D point
    """
    lng = longitude * math.pi / 180.0
    lat = latitude * math.pi / 180.0
    x = math.cos(lat) * math.cos(lng)
    y = math.cos(lat) * math.sin(lng)
    z = math.sin(lat)
    return x, y, z


def getClosestGridIndex(longitude: float, latitude: float, grid: []) -> int:
    """Returns the closest grid cell index
    """
    cellIndex = 0

    x, y, z = _latLongTo3D(longitude, latitude)

    dx = x - grid[0]['x']
    dy = y - grid[0]['y']
    dz = z - grid[0]['z']
    minDistSqr = (dx * dx) + (dy * dy) + (dz * dz)

    for i in range(len(grid)):
        dx = x - grid[i]['x']
        dist = dx * dx
        if dist >= minDistSqr:
            continue
        dy = y - grid[i]['y']
        dist += dy * dy
        if dist >= minDistSqr:
            continue
        dz = z - grid[i]['z']
        dist += dz * dz
        if dist < minDistSqr:
            cellIndex = i
            minDistSqr = dist
    return cellIndex


def getGrid(cellsHorizontal: int, cellsVertical: int) -> []:
    """Returns evenly spaced points on a sphere
    """
    noOfCells = cellsHorizontal * cellsVertical

    gridCells = []
    phi = math.pi * (3. - math.sqrt(5.))

    for i in range(noOfCells):
        y = 1 - (i / float(noOfCells - 1)) * 2
        radius = math.sqrt(1 - y * y)

        theta = phi * i

        x = math.cos(theta) * radius
        z = math.sin(theta) * radius

        latitude, longitude = _3DtoLatLong(x, y, z)
        gridCells.append({
            'index': i,
            'x': x,
            'y': y,
            'z': z,
            'latitude': latitude,
            'longitude': longitude,
            'stationIds': set()
        })
    return gridCells


def saveGridAsKML(grid: [], filename: str) -> None:
    """Save the grid points in KML format for visualization
    """
    kmlStr = \
        "<?xml version=\"1.0\" encoding='UTF-8'?>\n" + \
        "<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n" + \
        "<Document>\n"
    for gridCell in grid:
        kmlStr += \
            "  <Placemark>\n" + \
            "    <name>" + str(gridCell['index']) + "</name>\n" + \
            "    <description>" + str(gridCell['latitude']) + \
            ' ' + str(gridCell['longitude']) + '</description>\n' + \
            "    <Point>\n" + \
            "      <coordinates>" + str(gridCell['longitude']) + "," + \
            str(gridCell['latitude']) + ",0</coordinates>\n" + \
            "    </Point>\n" + \
            "  </Placemark>\n"
    kmlStr += \
        "</Document>\n" + \
        "</kml>\n"
    with open(filename, 'w+') as fp:
        fp.write(kmlStr)
