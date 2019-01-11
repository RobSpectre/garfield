import datetime
import pytz


def daterange(start_date, end_date):
    dates = []
    for n in range(int((end_date - start_date).days + 1)):
        dates.append((start_date +
                      datetime.timedelta(days=n)).replace(hour=0,
                                                          minute=0,
                                                          second=0,
                                                          microsecond=0))

    return dates


def daterange_by_week(year, week):
    start_date = datetime.datetime.strptime("{0} {1} 1".format(year, week),
                                            "%Y %W %w")
    timezone = pytz.timezone("utc")

    start_date = timezone.localize(start_date)

    return [x for x in daterange(start_date,
                                 start_date + datetime.timedelta(days=7))]
