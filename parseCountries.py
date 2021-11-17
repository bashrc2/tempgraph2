__filename__ = "parseCountries.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"


def loadCountries(filename: str) -> {}:
    """Loads countries from file
    """
    lines = []
    try:
        with open(filename, 'r') as fp:
            lines = fp.readlines()
    except BaseException:
        print('Unable to open ' + filename)
        return None
    countries = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if len(line) < 5:
            continue
        code = line[:2]
        name = line[3:]
        countries[code] = name
    return countries
