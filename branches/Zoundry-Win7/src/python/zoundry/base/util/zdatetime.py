from datetime import tzinfo, timedelta, datetime
from pytz.reference import LocalTimezone
import pytz

# ------------------------------------------------------------------------------
# Class Definition for ZSimpleTimeZone
#
# This class implements a time zone for use in parsing
# dates and times.
# ------------------------------------------------------------------------------
class ZSimpleTimeZone(tzinfo):
    u"Creates a simple time zone with the given offset (in minutes east of UTC)." #$NON-NLS-1$
    def __init__(self, dstHr, dstMin, dstDir):
        self.offset = (int(dstHr) * 60) + int(dstMin)

        if dstDir == u"-": #$NON-NLS-1$
            self.offset = self.offset * -1
    # end __init__()

    def utcoffset(self, _dt):
        return timedelta(minutes = self.offset)
    # end utcoffset()

    def dst(self, _dt):
        return timedelta(0)
    # end dst()

    def tzname(self, _dt):
        if self.offset == 0:
            return u"UTC" #$NON-NLS-1$
        return u"TZ:[%2d:%2d]" % (self.offset / 60, self.offset % 60) #$NON-NLS-1$
    # end tzname()

# end ZSimpleTimeZone

LOCAL_TIME_ZONE = LocalTimezone()
UTC_TIMEZONE = pytz.utc


# ------------------------------------------------------------------------------
# Getter for the local timezone instance.
# ------------------------------------------------------------------------------
def ZLocalTimezone():
    return LOCAL_TIME_ZONE
# end ZLocalTimezone


# ------------------------------------------------------------------------------
# Setter for the local timezone instance.  This can be used to override the
# default local time zone.
# ------------------------------------------------------------------------------
def setLocalTimezone(tz):
    global LOCAL_TIME_ZONE
    LOCAL_TIME_ZONE = tz
# end setLocalTimezone()


# ------------------------------------------------------------------------------
# A convenience method for returning the current datetime in utc
# ------------------------------------------------------------------------------
def getCurrentUtcDateTime():
    return datetime.now(UTC_TIMEZONE)
# end getCurrentUtcDateTime()


# ------------------------------------------------------------------------------
# A convenience method for returning the current datetime in local time.
# ------------------------------------------------------------------------------
def getCurrentLocalTime():
    return convertToLocalTime(getCurrentUtcDateTime())
# end getCurrentLocalTime()


# ------------------------------------------------------------------------------
# A convenience method for returning the utc time given the datetime object.
# The conversion to utc is made iff datetime tzinfo is LocalTimeZone.  If the
# tzinfo is already UTC, nothing is done.
# ------------------------------------------------------------------------------
def convertToUtcDateTime(dateTime):
    u"""convertToUtcDateTime(datetime) -> datetime
    Converts the given python datetime to the UTC timezone.""" #$NON-NLS-1$
    try:
        if dateTime is None:
            dateTime = getCurrentUtcDateTime()
        elif dateTime.tzinfo == UTC_TIMEZONE:
            pass
        else:
            dateTime = dateTime.astimezone(UTC_TIMEZONE)
    except:
        pass
    return dateTime
# end convertToUtcDateTime()


# ------------------------------------------------------------------------------
# A convenience method for returning the local time given the datetime object.
# If dateTime is None, returns "now" in local time.  If the datetime is already
# in local time, nothing is done.
# ------------------------------------------------------------------------------
def convertToLocalTime(dateTime):
    u"""convertToLocalTime(datetime) -> datetime
    Converts the given python datetime object from UTC
    to local time.""" #$NON-NLS-1$
    # Note: try/except block is here for defect #540.  No any idea why it is needed. :(
    try:
        localTZ = ZLocalTimezone()
        if dateTime is None:
            return getCurrentLocalTime()
        elif dateTime.tzinfo == UTC_TIMEZONE:
            return dateTime.astimezone(localTZ)
        elif isinstance(dateTime.tzinfo, ZSimpleTimeZone):
            return convertToLocalTime(dateTime.astimezone(UTC_TIMEZONE))
    except:
        pass
    return dateTime
# end convertToLocalTime()


# ------------------------------------------------------------------------------
# A convenience method for creating a datetime given the year, month, day, hour, min and sec. If localTz is false, the
# UTC tz is assumed.
# ------------------------------------------------------------------------------
def createDateTime(year, month, day, hour, min, secs, tz):
    # If the tz is a simple one or the UTC tz, then just create,
    # otherwise use the pytz localize mechanism
    if isinstance(tz, ZSimpleTimeZone) or isinstance(tz, LocalTimezone) or tz == UTC_TIMEZONE:
        return datetime(year, month, day, hour, min, secs, 0, tz)
    else:
        dt = datetime(year, month, day, hour, min, secs, 0, None)
        dt = tz.localize(dt)
        return dt
# end createDateTime()
