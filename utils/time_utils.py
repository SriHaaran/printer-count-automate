from datetime import datetime, time as dtime, timedelta

def parse_hhmm(s: str) -> dtime:
    hh, mm = s.split(":")
    return dtime(int(hh), int(mm))

def is_working_time(dt, start, end):
    return start <= dt.time() <= end

def compute_window(dt, start, end, poll_work, poll_after, buf_work, buf_after):
    window_end = dt
    if is_working_time(dt, start, end):
        seconds = poll_work + buf_work
    else:
        seconds = poll_after + buf_after
    window_start = dt - timedelta(seconds=seconds)
    return window_start, window_end, seconds