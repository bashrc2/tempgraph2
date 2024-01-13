__filename__ = "grid.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

import math


def _3d_to_lat_long(x_co: float, y_co: float, z_co: float) -> (float, float):
    """Converts 3D coordinate to latitude and longitude
    """
    latitude = math.asin(z_co) * 180 / math.pi
    longitude = math.atan2(y_co, x_co) * 180 / math.pi
    return latitude, longitude


def _lat_long_to_3d(longitude: float,
                    latitude: float) -> (float, float, float):
    """Convert latitude and longitude into a 3D point
    """
    lng = longitude * math.pi / 180.0
    lat = latitude * math.pi / 180.0
    x_co = math.cos(lat) * math.cos(lng)
    y_co = math.cos(lat) * math.sin(lng)
    z_co = math.sin(lat)
    return x_co, y_co, z_co


def get_closest_grid_index(longitude: float, latitude: float, grid: []) -> int:
    """Returns the closest grid cell index
    """
    cell_index = 0

    x_co, y_co, z_co = _lat_long_to_3d(longitude, latitude)

    dx1 = x_co - grid[0]['x']
    dy1 = y_co - grid[0]['y']
    dz1 = z_co - grid[0]['z']
    min_dist_sqr = (dx1 * dx1) + (dy1 * dy1) + (dz1 * dz1)

    for idx in range(len(grid)):
        dx1 = x_co - grid[idx]['x']
        dist = dx1 * dx1
        if dist >= min_dist_sqr:
            continue
        dy1 = y_co - grid[idx]['y']
        dist += dy1 * dy1
        if dist >= min_dist_sqr:
            continue
        dz1 = z_co - grid[idx]['z']
        dist += dz1 * dz1
        if dist < min_dist_sqr:
            cell_index = idx
            min_dist_sqr = dist
    return cell_index


def get_grid(cells_horizontal: int, cells_vertical: int) -> []:
    """Returns evenly spaced points on a sphere
    """
    no_of_cells = cells_horizontal * cells_vertical

    grid_cells = []
    phi = math.pi * (3. - math.sqrt(5.))

    for i in range(no_of_cells):
        y_co = 1 - (i / float(no_of_cells - 1)) * 2
        radius = math.sqrt(1 - y_co * y_co)

        theta = phi * i

        x_co = math.cos(theta) * radius
        z_co = math.sin(theta) * radius

        latitude, longitude = _3d_to_lat_long(x_co, y_co, z_co)
        grid_cells.append({
            'index': i,
            'x': x_co,
            'y': y_co,
            'z': z_co,
            'latitude': latitude,
            'longitude': longitude,
            'station_ids': set()
        })
    return grid_cells


def save_grid_as_kml(grid: [], filename: str) -> None:
    """Save the grid points in KML format for visualization
    """
    kml_str = \
        "<?xml version=\"1.0\" encoding='UTF-8'?>\n" + \
        "<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n" + \
        "<Document>\n"
    for grid_cell in grid:
        kml_str += \
            "  <Placemark>\n" + \
            "    <name>" + str(grid_cell['index']) + "</name>\n" + \
            "    <description>" + str(grid_cell['latitude']) + \
            ' ' + str(grid_cell['longitude']) + '</description>\n' + \
            "    <Point>\n" + \
            "      <coordinates>" + str(grid_cell['longitude']) + "," + \
            str(grid_cell['latitude']) + ",0</coordinates>\n" + \
            "    </Point>\n" + \
            "  </Placemark>\n"
    kml_str += \
        "</Document>\n" + \
        "</kml>\n"
    with open(filename, 'w+', encoding='utf-8') as fp_kml:
        fp_kml.write(kml_str)
