from time import time as time
from datetime import datetime as datetime

def current_time():
    """
    current_time function returns current system time as Y-M-D H-M-S string
    Args:
        no arguments required
    
    Returns:
        str: current system time as Y-M-D H-M-S string
    """
    time_not_formatted = time()
    time_formatted = datetime.fromtimestamp(time_not_formatted).strftime('%Y-%m-%d:%H:%M:%S.%f')
    return time_formatted
