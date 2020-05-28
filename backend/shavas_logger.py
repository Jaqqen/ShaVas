from inspect import currentframe, getframeinfo

import os
import pytz
import datetime

def logInfo(logText):
    file_name, line_num = getFileInfo()
    print(f'\033[94m>>>\033[0m {file_name}:{line_num} ||---|| \x1b[0;30;44m{logText}\x1b[0m')

def logError(logText):
    file_name, line_num = getFileInfo()
    print(f'\033[91m>>>\033[0m {file_name}:{line_num} ||---|| \x1b[0;30;41m{logText}\x1b[0m')


def logSuccess(logText):
    file_name, line_num = getFileInfo()
    print(f'\033[92m>>>\033[0m {file_name}:{line_num} ||---|| \x1b[6;30;42m{logText}\x1b[0m')


def logDebug(logText):
    file_name, line_num = getFileInfo()
    current_time = getCurrentTimeByTimezone('Europe/Berlin')
    print(f'\033[93m>>>\033[0m {file_name}:{line_num} [{current_time}] ||---|| \x1b[6;30;43m{logText}\x1b[0m')


def getFileInfo():
    frameinfo = getframeinfo(currentframe().f_back.f_back)
    base_filename = os.path.basename(frameinfo.filename)
    return (base_filename, frameinfo.lineno)


def getCurrentTimeByTimezone(_timezone):
    tz = pytz.timezone(_timezone)

    date_now = datetime.datetime.now(tz)
    time_now = date_now.time()
    f_time_now = time_now.strftime("%H:%M:%S")

    return f_time_now