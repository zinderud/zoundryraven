from zoundry.base.util.daterange import ZDateRange
from zoundry.base.util.daterange import createEndDate
from zoundry.base.util.daterange import createStartDate
from zoundry.base.util.schematypes import UTC_TIMEZONE
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.zdatetime import ZLocalTimezone
from zoundry.base.util.zdatetime import createDateTime
import calendar
import datetime
import re

EPOCH_TIME_ZERO = datetime.datetime(1970, 1, 1, 0, 0, 0, 0, UTC_TIMEZONE)
XMLRPC_UTC_DATE_PATTERN = re.compile(u"(\\d\\d\\d\\d)(\\d\\d)(\\d\\d)T(\\d\\d):(\\d\\d):(\\d\\d)Z", re.IGNORECASE) #$NON-NLS-1$
XMLRPC_LOCAL_DATE_PATTERN = re.compile(u"(\\d\\d\\d\\d)(\\d\\d)(\\d\\d)T(\\d\\d):(\\d\\d):(\\d\\d)") #$NON-NLS-1$

# Set the first weekday to 6
# FIXME (EPW) date range localization problem
calendar.setfirstweekday(6)

# ------------------------------------------------------------------------------
# A convenience method for parsing a date string that might actually be None.
# If the string is None, then None is returned, otherwise a ZSchemaDateTime
# object is returned.
# ------------------------------------------------------------------------------
def getNoneDate(dateString):
    if not dateString:
        return None
    else:
        return ZSchemaDateTime(dateString)
# end getNoneDate()


# ------------------------------------------------------------------------------
# A convenience method for parsing a xml-rpc IS8601 date string that might actually be None.
# The common format used by xmlrpc is YYYYMMDDTHH:MM:SS.
# If the string is None, then None is returned, otherwise a ZSchemaDateTime
# object is returned.
# ------------------------------------------------------------------------------
def getIso8601Date(dateString):
    if not dateString:
        return None
    # check GMT time match YYYYMMDD:HHMMZ sent by some xml-rpc servers (wordpress 2.2+)
    m = re.match(XMLRPC_UTC_DATE_PATTERN, dateString)
    if m:
        (year, month, day, h, m, s) = m.groups()
        return ZSchemaDateTime(createDateTime(int(year), int(month), int(day), int(h), int(m), int(s), UTC_TIMEZONE))
    
    # check local time match YYYYMMDD:HHMM sent by some xml-rpc servers.
    m = re.match(XMLRPC_LOCAL_DATE_PATTERN, dateString)
    if m:
        (year, month, day, h, m, s) = m.groups()
        return ZSchemaDateTime(createDateTime(int(year), int(month), int(day), int(h), int(m), int(s), ZLocalTimezone()))
    else:
        return ZSchemaDateTime(dateString)
# end getIso8601Date()


# ------------------------------------------------------------------------------
# A convenience method for creating a schema datetime given the
# year, month, day, hour, min and sec. If localTz is false, the
# UTC tz is assumed.
# ------------------------------------------------------------------------------
def createSchemaDateTime(year, month, day, hour, min, secs, localTz = True):
    if localTz:
        tz = ZLocalTimezone()
    else:
        tz = UTC_TIMEZONE
    dt = createDateTime(year, month, day, hour, min, secs, tz)
    return ZSchemaDateTime(dt)
# end createSchemaDateTime()


# ------------------------------------------------------------------------------
# This function takes the number of seconds since the epoch and returns a
# python datetime instance.
# ------------------------------------------------------------------------------
def getDateTimeFromEpoch(secondsSinceEpoch):
    return EPOCH_TIME_ZERO + datetime.timedelta(seconds=secondsSinceEpoch)
# end getDateTimeFromEpoch()


# ------------------------------------------------------------------------------
# Gets a range of dates for the month containing the given date.
# ------------------------------------------------------------------------------
def getContainingMonthDateRange(schemaTime):
    u"""getContainingMonthDateRange() -> ZDateRange
    Gets the date range that defines the 28, 29, 30, or 31 day
    month containing the given date.  For example, if the input
    is Dec 20, 2006, the return value would be the range
    beginning Dec 1, 2006 and ending Dec 31, 2006.""" #$NON-NLS-1$
    dt = schemaTime.getDateTime()
    (_notused, numDaysInMonth) = calendar.monthrange(dt.year, dt.month)
    startDate = createStartDate(dt.year, dt.month, 1)
    endDate = createEndDate(dt.year, dt.month, numDaysInMonth)
    return ZDateRange(ZSchemaDateTime(startDate), ZSchemaDateTime(endDate))
# end getContainingMonthDateRange()


# ------------------------------------------------------------------------------
# Gets a range of dates for the month containing today.
# ------------------------------------------------------------------------------
def getRangeForThisMonth():
    u"""getRangeForThisMonth() -> ZDateRange
    Returns the date range for this month.  See the documentation
    for getContainingMonthDateRange() for more details.""" #$NON-NLS-1$
    now = ZSchemaDateTime()
    return getContainingMonthDateRange(now)
# end getRangeForThisMonth()


# ------------------------------------------------------------------------------
# Gets a range of dates for a single 7 day week that contains the input date.
#
# FIXME (EPW) depending on the locale, first day of the week may be Monday
# ------------------------------------------------------------------------------
def getContainingWeekDateRange(schemaTime):
    u"""getContainingWeekDateRange(IZSchemaDateTime) -> ZDateRange
    Gets the date range that defines the 7 day week (from Sunday to
    Saturday) containing the given date.  For example, if the
    input is Wed Nov 22, 2006, the return value would be the range
    beginning Sun Nov 19, 2006 and ending Sat Nov 25, 2006.""" #$NON-NLS-1$
    dt = schemaTime.getDateTime()
    weekDay = calendar.weekday(dt.year, dt.month, dt.day)
    # Note: The calendar module returns 0 for Monday, 6 for Sunday
    startDiffDays = (weekDay + 1) % 7
    # Note: -1 mod 7 == 6
    endDiffDays = (6 - (weekDay + 1)) % 7
    startDelta = datetime.timedelta(days = startDiffDays)
    endDelta = datetime.timedelta(days = endDiffDays)
    startDate = dt - startDelta
    endDate = dt + endDelta
    startDate = createStartDate(startDate.year, startDate.month, startDate.day)
    endDate = createEndDate(endDate.year, endDate.month, endDate.day)
    return ZDateRange(ZSchemaDateTime(startDate), ZSchemaDateTime(endDate))
# end getContainingWeekDateRange()


# ------------------------------------------------------------------------------
# Gets the date range that defines this week.
# ------------------------------------------------------------------------------
def getRangeForThisWeek():
    u"""getRangeForThisWeek() -> ZDateRange
    Gets the date range that defines this week.  See the
    documentation in getContainingWeekDateRange() for more
    details.""" #$NON-NLS-1$
    now = ZSchemaDateTime()
    return getContainingWeekDateRange(now)
# end getRangeForThisWeek()


# ------------------------------------------------------------------------------
# Gets the date range that defines a single day.
# ------------------------------------------------------------------------------
def getRangeForDate(schemaTime):
    u"""getRangeForDate(IZSchemaDateTime) -> ZDateRange
    Gets the date range that defines the single day represented by
    the given input.  In other words, this function always returns
    a date range that spans a single day, from midnight AM to
    midnight PM.""" #$NON-NLS-1$
    dt = schemaTime.getDateTime(True)
    startDate = createStartDate(dt.year, dt.month, dt.day)
    endDate = createEndDate(dt.year, dt.month, dt.day)
    return ZDateRange(ZSchemaDateTime(startDate), ZSchemaDateTime(endDate))
# end getContainingWeekDateRange()


# ------------------------------------------------------------------------------
# Gets the date range that defines yesterday.
# ------------------------------------------------------------------------------
def getRangeForYesterday():
    u"""getRangeForYesterday() -> ZDateRange
    Gets the date range that defines 'yesterday'.  See the
    documentation for "getRangeForDate()" for more details.""" #$NON-NLS-1$
    now = ZSchemaDateTime()
    dt = now.getDateTime(True)
    delta = datetime.timedelta(days = 1)
    yesterdayDt = dt - delta
    yesterday = ZSchemaDateTime(yesterdayDt)
    return getRangeForDate(yesterday)
# end getRangeForYesterday()


# ------------------------------------------------------------------------------
# Gets the date range that defines today.
# ------------------------------------------------------------------------------
def getRangeForToday():
    u"""getRangeForToday() -> ZDateRange
    Gets the date range that defines 'today'.  See the
    documentation for "getRangeForDate()" for more details.""" #$NON-NLS-1$
    now = ZSchemaDateTime()
    return getRangeForDate(now)
# end getRangeForToday()


# ------------------------------------------------------------------------------
# Gets the date range that spans the last "N" days, where "N" is the input
# to the function.
# ------------------------------------------------------------------------------
def getLastNDaysAsDateRange(numDays):
    u"""getLastNDaysAsDateRange(int) -> ZDateRange
    Returns the last 'numDays' days as a date range.  This range
    will start at midnight AM 'numDays' ago and end 'today' at
    midnight PM.""" #$NON-NLS-1$
    # FIXME (EPW) implement getLastNDaysAsDateRange()
# end getLastNDaysAsDateRange()
