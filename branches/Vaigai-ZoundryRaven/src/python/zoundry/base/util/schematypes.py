from datetime import datetime
from zoundry.base.exceptions import ZException
from zoundry.base.messages import _extstr
from zoundry.base.util.zdatetime import UTC_TIMEZONE
from zoundry.base.util.zdatetime import ZSimpleTimeZone
from zoundry.base.util.zdatetime import convertToLocalTime
from zoundry.base.util.zdatetime import convertToUtcDateTime
from zoundry.base.util.zdatetime import createDateTime
from zoundry.base.util.zdatetime import getCurrentUtcDateTime
import re
import time

DATE_TIME_PATTERN = re.compile(u"(-?)([1-9]*[0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\\.([0-9]*))?(Z|(([+-])([0-9]{2}):([0-9]{2})))?$") #$NON-NLS-1$

# ------------------------------------------------------------------------------
# A XSD Schema formatted dateTime object.  This object takes either a 'datetime'
# object, a string or a int/long in ms (gmt).  It can output either format.
# ------------------------------------------------------------------------------
class ZSchemaDateTime:

    def __init__(self, date = None):
        param = date
        if not date:
            param = getCurrentUtcDateTime()

        if isinstance(param, str) or isinstance(param, unicode):
            self._initFromString(param)
        elif isinstance(param, long) or isinstance(param, int):
            self._initFromLongMs(param)
        elif isinstance(param, datetime):
            self.dateTime = convertToUtcDateTime(param)
        else:
            raise ZException(_extstr(u"schematypes.SchemaDateTimeFormatError")) #$NON-NLS-1$
    # end __init__()

    def _initFromString(self, dtString):
        m = DATE_TIME_PATTERN.match(dtString)
        if not m:
            raise ZException(_extstr(u"schematypes.FailedToParseDateTimeString") % dtString) #$NON-NLS-1$

        year = m.group(2);
        month = m.group(3);
        day = m.group(4);
        hour = m.group(5);
        minute = m.group(6);
        second = m.group(7);

        isUTC = (not m.group(10)) or (m.group(10) == u"Z") #$NON-NLS-1$
        tz = UTC_TIMEZONE
        if not isUTC:
            tzDir = m.group(12)
            tzHr = m.group(13)
            tzMin = m.group(14)
            tz = ZSimpleTimeZone(tzHr, tzMin, tzDir)

        # Note: not sure about the millis param...
        self._initFromYYYYMMDDHHMMSS(int(year), int(month), int(day), int(hour), int(minute), int(second), tz)
    # end _initFromString()

    def _initFromLongMs(self, gmTimeMs):
        (year, month, day, hour, minute, second, wday, yday, isdst) = time.gmtime(gmTimeMs) #@UnusedVariable
        self._initFromYYYYMMDDHHMMSS(int(year), int(month), int(day), int(hour), int(minute), int(second), UTC_TIMEZONE)
    # end _initFromLongMs

    def _initFromYYYYMMDDHHMMSS(self, year, month, day, hour, minute, second, tz = UTC_TIMEZONE):
        # Note: not sure about the millis param...
        dt = createDateTime(year, month, day, hour, minute, second, tz)
        self.dateTime = convertToUtcDateTime(dt)
    # end _initFromYYYYMMDDHHMMSS

    def getDateTime(self, localTime = False):
        if localTime:
            return convertToLocalTime(self.dateTime)
        return self.dateTime
    # end getDateTime()

    def getDay(self):
        return self.dateTime.day
    # end getDay()

    def getMonth(self):
        return self.dateTime.month
    # end getMonth()

    def getYear(self):
        return self.dateTime.year
    # end getYear()

    def getHour(self):
        return self.dateTime.hour
    # end getHour()

    def setHour(self, hour):
        self.dateTime = self.dateTime.replace(hour = hour)
    # end setHour()

    def getMinutes(self):
        return self.dateTime.minute
    # end getMinutes()

    def setMinutes(self, minutes):
        self.dateTime = self.dateTime.replace(minute = minutes)
    # end setMinutes()

    def getSeconds(self):
        return self.dateTime.second
    # end getSeconds()

    def setSeconds(self, seconds):
        self.dateTime = self.dateTime.replace(second = seconds)
    # end setSeconds()

    def __str__(self):
        date = self.dateTime
        if date.microsecond > 0:
            return u"%04d-%02d-%02dT%02d:%02d:%02d.%03dZ" % (date.year, date.month, date.day, date.hour, date.minute, date.second, date.microsecond / 1000) #$NON-NLS-1$
        else:
            return u"%04d-%02d-%02dT%02d:%02d:%02dZ" % (date.year, date.month, date.day, date.hour, date.minute, date.second) #$NON-NLS-1$
    # end __str__()

    def toDateString(self):
        date = self.dateTime
        return u"%04d-%02d-%02dZ" % (date.year, date.month, date.day) #$NON-NLS-1$
    # end toDateString()

    def __repr__(self):
        return u"<%s '%s'>" % (self.__class__.__name__, str(self)) #$NON-NLS-1$
    # end __repr__()

    def __cmp__(self, other):
        dt1 = self.getDateTime()
        dt2 = other.getDateTime()
        if dt1 < dt2:
            return -1
        elif dt1 > dt2:
            return 1
        else:
            return 0
    # end __cmp__()

    def toString(self, formatString = u"%c", localTime = False): #$NON-NLS-1$
        # Stupid strftime only takes a str, not a unicode.
        dt = self.getDateTime()
        if localTime:
            dt = convertToLocalTime(dt)
        return dt.strftime(str(formatString))
    # end toString()

# end ZSchemaDateTime
