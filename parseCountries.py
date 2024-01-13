__filename__ = "parseCountries.py"
__author__ = "Bob Mottram"
__license__ = "GPL3+"
__version__ = "2.0.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Commandline Interface"


def load_countries(filename: str) -> {}:
    """Loads countries from file
    """
    lines = []
    try:
        with open(filename, 'r', encoding='utf-8') as fp_countries:
            lines = fp_countries.readlines()
    except OSError:
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
