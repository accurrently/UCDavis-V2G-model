from __future__ import absolute_import
import datetime, random, time

def str_time(s):
    return time.strptime(s,'%H:%M:%S')

def str_timedelta(s):
    x = str_time(s)
    return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec)

def td_minutes(td):
    return (td.total_seconds()//60)

def td_gauss(mu, sigma):
    m = 0
    s = 0
    if isinstance(mu, string):
        m = td_minutes(str_timedelta(mu))
    elif isinstance(mu, int) or isinstance(mu, float):
        m = mu
    if isinstance(sigma, string):
        s = td_minutes(str_timedelta(sigma))
    elif isinstance(sigma, int) or isinstance(sigma, float):
        s = sigma

    return datetime.timedelta( minutes = random.gauss(m, s) )
