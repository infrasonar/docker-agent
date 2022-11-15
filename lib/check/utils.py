from datetime import datetime
import re


_TZONE = re.compile('[0-9]*(.*)')


def get_ts_from_time_str(time_str: str):
    # String format: '2022-04-05T11:30:56.93289351+02:00';
    # remove .93289351 but keep the time-zone
    dstr, tz = time_str.split('.')
    tz = _TZONE.match(tz).group(1)
    return int(datetime.strptime(dstr + tz, '%Y-%m-%dT%H:%M:%S%z').timestamp())


def format_list(val):
    if val is None:
        return 'None'

    joined = ' ,'.join(map(str, val))
    return f'[{joined}]'


def format_name(names: list):
    return names[0][1:]


if __name__ == '__main__':
    a = get_ts_from_time_str('2022-04-05T11:30:56.93289351+02:00')
    b = get_ts_from_time_str('2022-04-05T11:30:56.93289351Z')
    c = get_ts_from_time_str('2022-04-05T11:30:56.93289351-02:00')
    print(a, b, c)

    ts = 1649158256
    assert a == ts - 7200 and b == ts and c == ts + 7200
