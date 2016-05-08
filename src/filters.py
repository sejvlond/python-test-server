"""
Jinja2 template filters
"""
import pytz


def nl2br(text):
    """
    New lines to <br>

    Parameters
    ----------
    text: str

    Returns
    -------
    text
        with <br>
    """
    return text.replace("\n", "<br>")


def str_(text):
    """
    str() filter which transofrms None to ""

    Parameters
    ----------
    text: str

    Returns
    -------
    str
    """
    return "" if text is None else str(text)


def datetime(value, format='%d.%m.%Y %H:%M:%S', timezone="Europe/Prague"):
    """
    Format datatime value to timezone

    Parameters
    ----------
    value: datetime
        datetime

    format: str
        formating string

    timezone: str
        name of timezone

    Returns
    -------
        datetime or original value if failes
    """
    try:
        return value.replace(tzinfo=pytz.utc).\
            astimezone(pytz.timezone(timezone)).strftime(format)
    except:
        return value


def timedelta(dates):
    """
    Format time delta between dates to readable format. Negative delta like
    timedelta(-1, 86391) = -1 day 86391 sec are computed as abs(total_seconds)
    and displayed as they should be = -0:00:09

    Parameters
    ----------
    dates: tuple
        (from, to) as datetimes

    Returns
    -------
    string
        [- ]%H:%M:%S
    """
    diff = (dates[0] - dates[1]).total_seconds()
    h, rem = divmod(abs(diff), 3600)
    m, s = divmod(rem, 60)
    return ("- " if diff < 0 else "") + "%d:%02d:%02d" % (h, m, s)
