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
from parseData import loadData
from parseStations import loadStationLocations
from parseStations import saveStationLocationsAsKML
from tests import runAllTests
from parseCountries import loadCountries
from grid import getGrid
from grid import saveGridAsKML
from baseline import updateGridBaselines
from anomaly import updateGridAnomalies
from anomaly import getGlobalAnomalies
from anomaly import plotGlobalAnomalies


def str2bool(v) -> bool:
    """Returns true if the given value is a boolean
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
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
    runAllTests()
    sys.exit()

if args.endYear <= args.startYear:
    print('End year should be greater than ' + str(args.startYear))
    sys.exit()

if __name__ == "__main__":
    gridCells = getGrid(args.cellsHorizontal, args.cellsVertical)
    print(str(len(gridCells)) + ' grid cells')
    print('Loading countries')
    countries = loadCountries(args.countries)
    if not countries:
        print('No countries')
        sys.exit()
    print(str(len(countries.items())) + ' countries loaded')
    print('Loading station locations')
    stationLocations = loadStationLocations(args.stations, gridCells)
    if not stationLocations:
        print('No station locations')
        sys.exit()
    print(str(len(stationLocations.items())) + ' station locations loaded')

    saveStationLocationsAsKML(stationLocations, 'stations.kml')
    print('Saved stations as KML')

    saveGridAsKML(gridCells, 'grid.kml')
    print('Saved grid as KML')

    print('Loading data from ' + args.filename)
    stationsData, yearsData = \
        loadData(args.filename, args.startYear, args.endYear)
    if not stationsData:
        print('No data')
        sys.exit()
    print(str(len(stationsData.items())) + ' stations data loaded')
    print('Calculating reference baseline between ' +
          str(args.baselineStart) + ' and ' + str(args.baselineEnd))
    ctr = updateGridBaselines(gridCells, stationsData,
                              args.baselineStart, args.baselineEnd)
    print(str(ctr) + ' grid baselines updated')
    print('Calculating grid anomalies between ' +
          str(args.startYear) + ' and ' + str(args.endYear))
    percent = updateGridAnomalies(gridCells, stationsData,
                                  args.startYear, args.endYear)
    print(str(percent) + '% grid anomalies updated')
    print('Calculating global anomalies between ' +
          str(args.startYear) + ' and ' + str(args.endYear))
    globalAnom = getGlobalAnomalies(gridCells, args.startYear, args.endYear)
    plotGlobalAnomalies(gridCells, args.startYear, args.endYear)
    print('Done')
    sys.exit()
