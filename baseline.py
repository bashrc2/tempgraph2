__filename__ = "baseline.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"


def _get_baseline_for_year(id: str, stations_data: {}, year: int) -> []:
    """Returns the baseline for a given station id
    """
    baseline = [None] * 12
    if year not in stations_data[id]:
        return baseline
    month_data = stations_data[id][year]['month']
    for month_index in range(12):
        month_data2 = month_data[month_index]
        if month_data2['qcflag'] == 'M':
            # Flagged as error
            continue
        if month_data2['av'] > -80:
            if month_data2['av'] < 80:
                baseline[month_index] = month_data2['av']
    return baseline


def _get_baseline(id: str, stations_data: {},
                  start_year: int, end_year: int) -> []:
    """Returns the baseline for a given station id
    """
    if id not in stations_data:
        return [None] * 12

    if start_year == end_year:
        return _get_baseline_for_year(id, stations_data, start_year)

    baseline = [0.0] * 12
    hits = [0] * 12
    for year in range(start_year, end_year, 1):
        if year not in stations_data[id]:
            continue
        month_data = stations_data[id][year]['month']
        for month_index in range(12):
            month_data2 = month_data[month_index]
            if month_data2['qcflag'] == 'M':
                # Flagged as error
                continue
            if month_data2['av'] > -80:
                if month_data2['av'] < 80:
                    baseline[month_index] += month_data2['av']
                    hits[month_index] += 1

    for month_index in range(12):
        if hits[month_index] > 0:
            baseline[month_index] /= float(hits[month_index])
        else:
            baseline[month_index] = None
    return baseline


def _baseline_for_stations(stations_data: {},
                           start_year: int, end_year: int,
                           station_ids: set) -> []:
    """Returns a baseline for the given range of years
    and the given station ids
    """
    if not station_ids:
        return [None] * 12, False

    baseline = [0.0] * 12
    hits = [0] * 12
    for sid in station_ids:
        station_baseline = \
            _get_baseline(sid, stations_data, start_year, end_year)
        for month_index in range(12):
            if station_baseline[month_index] is not None:
                baseline[month_index] += station_baseline[month_index]
                hits[month_index] += 1

    for month_index in range(12):
        if hits[month_index] > 0:
            baseline[month_index] /= float(hits[month_index])
        else:
            baseline[month_index] = None

    return baseline, True


def update_grid_baselines(grid: [], stations_data: {},
                          start_year: int, end_year: int) -> int:
    """Calculates reference baselines for each grid cell
    """
    ctr = 0
    for grid_cell in grid:
        if grid_cell['station_ids']:
            grid_cell['baseline'], has_data = \
                _baseline_for_stations(stations_data, start_year, end_year,
                                       grid_cell['station_ids'])
            if has_data:
                ctr += 1
    return ctr
