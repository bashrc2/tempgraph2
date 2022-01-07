__filename__ = "tempgraph2.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

# import os
import sys
import argparse
from parseData import load_data
from parseStations import load_station_locations
from parseStations import save_station_locations_as_kml
from tests import run_all_tests
from parseCountries import load_countries
from grid import get_grid
from grid import save_grid_as_kml
from baseline import update_grid_baselines
from anomaly import update_grid_anomalies
from anomaly import get_global_anomalies
from anomaly import plot_global_anomalies


def str2bool(value) -> bool:
    """Returns true if the given value is a boolean
    """
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser(description='tempgraph2')
parser.add_argument('--filename', '-f', type=str,
                    default='data/v4.mean',
                    help='Filename for the series data')
parser.add_argument('--countries', '-c', type=str,
                    default='data/v4.country.codes',
                    help='County codes')
parser.add_argument('--stations', type=str,
                    default='data/wmo.txt',
                    help='Station locations filename')
parser.add_argument('--start', '--startYear', dest='startYear', type=int,
                    default=1900,
                    help='Start year')
parser.add_argument('--end', '--endYear', dest='endYear', type=int,
                    default=2020,
                    help='End year')
parser.add_argument('--baselineStart', dest='baselineStart', type=int,
                    default=1961,
                    help='Reference baseline start year')
parser.add_argument('--baselineEnd', dest='baselineEnd', type=int,
                    default=1990,
                    help='Reference baseline end year')
parser.add_argument('--cellsHorizontal', dest='cellsHorizontal', type=int,
                    default=72,
                    help='Number of cells across the grid')
parser.add_argument('--cellsVertical', dest='cellsVertical', type=int,
                    default=36,
                    help='Number of cells down the grid')
parser.add_argument("--debug", type=str2bool, nargs='?',
                    const=True, default=False,
                    help="Show debug")
parser.add_argument("--tests", type=str2bool, nargs='?',
                    const=True, default=False,
                    help="Run unit tests")

args = parser.parse_args()

debug = False
if args.debug:
    debug = True

if args.tests:
    run_all_tests()
    sys.exit()

if args.endYear <= args.startYear:
    print('End year should be greater than ' + str(args.startYear))
    sys.exit()

if __name__ == "__main__":
    grid_cells = get_grid(args.cellsHorizontal, args.cellsVertical)
    print(str(len(grid_cells)) + ' grid cells')
    print('Loading countries')
    countries = load_countries(args.countries)
    if not countries:
        print('No countries')
        sys.exit()
    print(str(len(countries.items())) + ' countries loaded')
    print('Loading station locations')
    station_locations = load_station_locations(args.stations, grid_cells)
    if not station_locations:
        print('No station locations')
        sys.exit()
    print(str(len(station_locations.items())) + ' station locations loaded')

    save_station_locations_as_kml(station_locations, 'stations.kml')
    print('Saved stations as KML')

    save_grid_as_kml(grid_cells, 'grid.kml')
    print('Saved grid as KML')

    print('Loading data from ' + args.filename)
    stations_data, years_data = \
        load_data(args.filename, args.startYear, args.endYear)
    if not stations_data:
        print('No data')
        sys.exit()
    print(str(len(stations_data.items())) + ' stations data loaded')
    print('Calculating reference baseline between ' +
          str(args.baselineStart) + ' and ' + str(args.baselineEnd))
    ctr = update_grid_baselines(grid_cells, stations_data,
                                args.baselineStart, args.baselineEnd)
    print(str(ctr) + ' grid baselines updated')
    print('Calculating grid anomalies between ' +
          str(args.startYear) + ' and ' + str(args.endYear))
    percent = update_grid_anomalies(grid_cells, stations_data,
                                    args.startYear, args.endYear)
    print(str(percent) + '% grid anomalies updated')
    print('Calculating global anomalies between ' +
          str(args.startYear) + ' and ' + str(args.endYear))
    globalAnom = get_global_anomalies(grid_cells, args.startYear, args.endYear)
    plot_global_anomalies(grid_cells, args.startYear, args.endYear)
    print('Done')
    sys.exit()
