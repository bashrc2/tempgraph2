__filename__ = "anomaly.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"

import os


def _stations_anomaly(year: int, stations_data: {}, stations_locations: {},
                      baseline: [], station_ids: set,
                      min_latitude: float, max_latitude: float,
                      month_number: int) -> float:
    """Returns anomaly for the given stations for the given year
    """
    anomaly = 0.0
    hits = 0

    for sid in station_ids:
        if sid not in stations_data:
            continue
        if year not in stations_data[sid]:
            continue
        if stations_locations[sid]['latitude'] < min_latitude or \
           stations_locations[sid]['latitude'] > max_latitude:
            continue
        month_data = stations_data[sid][year]['month']
        if month_number > -1:
            month_index = month_number
            if baseline[month_index]:
                if month_data[month_index]['av'] > -80 and \
                   month_data[month_index]['av'] < 80:
                    anomaly += \
                        month_data[month_index]['av'] - baseline[month_index]
                    hits += 1
        else:
            for month_index in range(12):
                if not baseline[month_index]:
                    continue
                if month_data[month_index]['av'] > -80 and \
                   month_data[month_index]['av'] < 80:
                    anomaly += \
                        month_data[month_index]['av'] - baseline[month_index]
                    hits += 1
    if hits > 0:
        return anomaly / float(hits)
    return None


def update_grid_anomalies(grid: [], stations_data: {}, stations_locations: {},
                          start_year: int, end_year: int,
                          min_latitude: float, max_latitude: float) -> int:
    """Calculates anomalies for each grid cell within a range of years
    """
    ctr = 0
    year_ctr = 0
    for grid_cell in grid:
        grid_cell['anomalies'] = {}
        grid_cell['anomalies_monthly'] = {}
        if not grid_cell['station_ids']:
            continue
        baseline = grid_cell['baseline']
        station_ids = grid_cell['station_ids']
        for year in range(start_year, end_year + 1, 1):
            grid_cell['anomalies'][year] = \
                _stations_anomaly(year, stations_data, stations_locations,
                                  baseline, station_ids,
                                  min_latitude, max_latitude, -1)
            if grid_cell['anomalies'][year] is not None:
                year_ctr += 1
                grid_cell['anomalies_monthly'][year] = []
                for month_index in range(12):
                    mnth_anom = \
                        _stations_anomaly(year, stations_data, stations_locations,
                                          baseline, station_ids, min_latitude,
                                          max_latitude, month_index)
                    grid_cell['anomalies_monthly'][year].append(mnth_anom)
            ctr += 1
    if year_ctr > 0:
        return int(year_ctr * 100 / float(ctr))
    return 0


def get_global_anomalies(grid: [],
                         start_year: int, end_year: int) -> {}:
    """Returns global anomalies in the given year range
    """
    result = {}
    for year in range(start_year, end_year + 1, 1):
        year_anomaly = 0.0
        ctr = 0
        for grid_cell in grid:
            if grid_cell['anomalies'].get(year):
                year_anomaly += grid_cell['anomalies'][year]
                ctr += 1
        if ctr > 0:
            result[year] = year_anomaly / float(ctr)
        else:
            result[year] = None
    return result


def get_monthly_anomalies(grid: [],
                          start_year: int, end_year: int) -> {}:
    """Returns monthly anomalies in the given year range
    """
    result = {}
    for year in range(start_year, end_year + 1, 1):
        months_anomaly = [0,0,0,0,0,0,0,0,0,0,0,0]
        months_ctr = [0,0,0,0,0,0,0,0,0,0,0,0]
        ctr = 0
        for grid_cell in grid:
            if grid_cell['anomalies_monthly'].get(year):
                months_list = grid_cell['anomalies_monthly'][year]
                idx = 0
                for month_anom in months_list:
                    if month_anom is None:
                        idx += 1
                        continue
                    months_anomaly[idx] += month_anom
                    months_ctr[idx] += 1
                    idx += 1
                ctr += 1
        for month_index in range(12):
            if months_ctr[month_index] > 0:
                months_anomaly[month_index] /= months_ctr[month_index]
            else:
                months_anomaly[month_index] = None
        if ctr > 0:
            result[year] = months_anomaly
        else:
            result[year] = None
    return result


def plot_global_anomalies(grid: [],
                          start_year: int, end_year: int,
                          baseline_start: int, baseline_end: int,
                          min_latitude: float, max_latitude: float) -> None:
    """Plot yearly anomalies graph
    """
    anomalies = get_global_anomalies(grid, start_year, end_year)
    series = []
    minimum_temp = 99999999
    maximum_temp = -99999999
    for year in range(start_year, end_year + 1, 1):
        series.append(anomalies[year])
        if anomalies[year] > maximum_temp:
            maximum_temp = anomalies[year]
        if anomalies[year] < minimum_temp:
            minimum_temp = anomalies[year]

    title = \
        "Global Temperature Anomalies " + \
        str(start_year) + ' - ' + str(end_year) + \
        ' for latitude range ' + str(min_latitude) + ' - ' + str(max_latitude)
    subtitle = "Source https://www.ncei.noaa.gov/pub/data/ghcn/v4"
    x_label = 'Year'
    y_label = 'Average Temperature Anomaly (Celcius) ' + \
        'relative to ' + str(baseline_start) + '-' + str(baseline_end)
    indent = 0.34
    vpos = 0.94
    image_width = 1000
    image_height = 1000
    plot_name = 'global_anomalies'
    image_format = 'jpg'
    image_format2 = 'jpeg'
    filename = plot_name + '.' + image_format
    script_filename = plot_name + '.gnuplot'
    data_filename = plot_name + '.data'
    with open(data_filename, 'w+', encoding='utf-8') as fp_data:
        year = start_year
        for temperature_anomaly in series:
            fp_data.write(str(year) + "    " + str(temperature_anomaly) + '\n')
            year += 1
    script = \
        "reset\n" + \
        "set title \"" + title + "\"\n" + \
        "set label \"" + subtitle + "\" at screen " + \
        str(indent) + ", screen " + str(vpos) + "\n" + \
        "set yrange [" + str(minimum_temp) + ":" + \
        str(maximum_temp) + "]\n" + \
        "set xrange [" + str(start_year) + ":" + str(end_year) + "]\n" + \
        "set lmargin 9\n" + \
        "set rmargin 2\n" + \
        "set xlabel \"" + x_label + "\"\n" + \
        "set ylabel \"" + y_label + "\"\n" + \
        "set grid\n" + \
        "set key right bottom\n" + \
        "set terminal " + image_format2 + \
        " size " + str(image_width) + "," + str(image_height) + "\n" + \
        "set output \"" + filename + "\"\n" + \
        "plot \"" + data_filename + "\" using 1:2 notitle with lines\n"
    with open(script_filename, 'w+', encoding='utf-8') as fp_scr:
        fp_scr.write(script)
    os.system('gnuplot ' + script_filename)


def plot_monthly_anomalies(grid: [],
                           start_year: int, end_year: int,
                           baseline_start: int, baseline_end: int,
                           min_latitude: float, max_latitude: float) -> None:
    """Plot monthly anomalies graph
    """
    anomalies = get_monthly_anomalies(grid, start_year, end_year)
    series = []
    minimum_temp = 99999999
    maximum_temp = -99999999
    for year in range(start_year, end_year + 1, 1):
        series.append(anomalies[year])
        for month_index in range(12):
            if anomalies[year][month_index] is None:
                continue
            if anomalies[year][month_index] > maximum_temp:
                maximum_temp = anomalies[year][month_index]
            if anomalies[year][month_index] < minimum_temp:
                minimum_temp = anomalies[year][month_index]

    title = \
        "Monthly Temperature Anomalies " + \
        str(start_year) + ' - ' + str(end_year) + \
        ' for latitude range ' + str(min_latitude) + ' - ' + str(max_latitude)
    subtitle = "Source https://www.ncei.noaa.gov/pub/data/ghcn/v4"
    x_label = 'Month'
    y_label = 'Average Monthly Temperature Anomaly (Celcius) ' + \
        'relative to ' + str(baseline_start) + '-' + str(baseline_end)
    indent = 0.34
    vpos = 0.94
    image_width = 1000
    image_height = 1000
    plot_name = 'monthly_anomalies'
    image_format = 'jpg'
    image_format2 = 'jpeg'
    filename = plot_name + '.' + image_format
    script_filename = plot_name + '.gnuplot'
    data_filename = plot_name + '.data'
    with open(data_filename, 'w+', encoding='utf-8') as fp_data:
        for month_index in range(12):
            line = str(month_index + 1)
            for temperature_anomaly in series:
                if temperature_anomaly[month_index] is not None:
                    line += " " + str(temperature_anomaly[month_index])
                else:
                    line += " 0"
            fp_data.write(line + '\n')
    script = \
        "reset\n" + \
        "set title \"" + title + "\"\n" + \
        "set label \"" + subtitle + "\" at screen " + \
        str(indent) + ", screen " + str(vpos) + "\n" + \
        "set yrange [" + str(minimum_temp) + ":" + \
        str(maximum_temp) + "]\n" + \
        "set xrange [1:12]\n" + \
        "set lmargin 9\n" + \
        "set rmargin 2\n" + \
        "set xlabel \"" + x_label + "\"\n" + \
        "set ylabel \"" + y_label + "\"\n" + \
        "set xtics (\"Jan\" 1, \"Feb\" 2, \"Mar\" 3, \"Apr\" 4, " + \
        "\"May\" 5, \"Jun\" 6, \"Jul\" 7, \"Aug\" 8, \"Sep\" 9, " + \
        "\"Oct\" 10, \"Nov\" 11, \"Dec\" 12)\n" + \
        "set grid\n" + \
        "set key right bottom\n" + \
        "set terminal " + image_format2 + \
        " size " + str(image_width) + "," + str(image_height) + "\n" + \
        "set output \"" + filename + "\"\n"
    script += "plot "
    for year in range(start_year, end_year+1, 20):
        script += \
            "\"" + data_filename + "\" using 1:" + str(2+year-start_year) + \
            " title \"" + str(year) + "\" with lines"
        if year < end_year+1:
            script += ', '
    script += '\n'
    with open(script_filename, 'w+', encoding='utf-8') as fp_scr:
        fp_scr.write(script)
    os.system('gnuplot ' + script_filename)
