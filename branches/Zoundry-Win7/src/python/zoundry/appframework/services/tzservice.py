from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.engine.service import IZService
from zoundry.base.util.zdatetime import setLocalTimezone
import pytz
import time

# ------------------------------------------------------------------------------
# Encapsulates time zone information.
# ------------------------------------------------------------------------------
class IZTimeZoneInfo:

    def getName(self):
        u"""getName() -> string
        Returns the name of the time zone.  e.g. US/Eastern""" #$NON-NLS-1$
    # end getName()

    def getPyTimeZone(self):
        u"""getPyTimeZone() -> tzinfo
        Return the python tzinfo timezone object for this timezone
        (suitable for use with a python datetime).""" #$NON-NLS-1$
    # end getPyTimeZone()

# end IZTimeZoneInfo


# ------------------------------------------------------------------------------
# Time zone info impl.
# ------------------------------------------------------------------------------
class ZTimeZoneInfo(IZTimeZoneInfo):

    def __init__(self, tzName):
        self.name = tzName
    # end __init__()

    def getName(self):
        return self.name
    # end getName()

    def getPyTimeZone(self):
        return pytz.timezone(self.name)
    # end getPyTimeZone()

# end ZTimeZoneInfo


# ------------------------------------------------------------------------------
# This defines the methods found on the Zoundry TimeZone Service.  The TimeZone
# Service is responsible for:
# 1) figuring out the current local timezone
# 2) managing a list of global timezones
# 3) providing a mechanism to override the local timezone
# ------------------------------------------------------------------------------
class IZTimeZoneService(IZService):

    def getTimeZones(self):
        u"""getTimeZones() -> IZTimeZoneInfo[]
        Returns the list of timezone objects.""" #$NON-NLS-1$
    # end getTimeZones()

    def getTimeZone(self):
        u"""getTimeZone() -> IZTimeZoneInfo
        Returns the current timezone, or None if no timezone is set.""" #$NON-NLS-1$
    # end getTimeZone()

    def setTimeZone(self, tzInfo):
        u"""setTimeZone(IZTimeZoneInfo) -> None
        Changes the timezone (can be None).""" #$NON-NLS-1$
    # end setTimeZone()

    def findTimeZone(self, tzName):
        u"""findTimeZone(string) -> IZTimeZoneInfo
        Finds a timezone with the given name.""" #$NON-NLS-1$
    # end findTimeZone()

# end IZTimeZoneService


# ------------------------------------------------------------------------------
# This is an implementation of the Zoundry TimeZone Service.
# ------------------------------------------------------------------------------
class ZTimeZoneService(IZTimeZoneService):

    def __init__(self):
        self.timeZones = []
        self.timeZone = None
        self.tupleToTZNameMap = {}
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)

        self._initTZMap()
        self._loadTimeZones()
        self._configureTimeZone()

        self.logger.debug(u"TimeZone Service started [%d time zones loaded]." % len(self.timeZones)) #$NON-NLS-1$
    # end start()

    def stop(self):
        self.timeZones = []
        self.timeZone = None
    # end stop()

    def _initTZMap(self):
        self.tupleToTZNameMap[(u"Alaskan Standard Time", u"Alaskan Daylight Time")] = u"US/Alaska" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#        self.tupleToTZNameMap[(u"", u"")] = u"US/Aleutian" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"US Mountain Standard Time", u"US Mountain Standard Time")] = u"US/Arizona" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"Central Standard Time", u"Central Daylight Time")] = u"US/Central" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"US Eastern Standard Time", u"US Eastern Standard Time")] = u"US/East-Indiana" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"Eastern Standard Time", u"Eastern Daylight Time")] = u"US/Eastern" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"Hawaiian Standard Time", u"Hawaiian Standard Time")] = u"US/Hawaii" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#        self.tupleToTZNameMap[(u"", u"")] = u"US/Indiana-Starke" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#        self.tupleToTZNameMap[(u"", u"")] = u"US/Michigan" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"Mountain Standard Time", u"Mountain Daylight Time")] = u"US/Mountain" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"Pacific Standard Time", u"Pacific Daylight Time")] = u"US/Pacific" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#        self.tupleToTZNameMap[(u"", u"")] = u"US/Pacific-New" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        self.tupleToTZNameMap[(u"Samoa Standard Time", u"Samoa Standard Time")] = u"US/Samoa" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
    # end _initTZMap()

    def _loadTimeZones(self):
        self.timeZones = map(ZTimeZoneInfo, pytz.common_timezones)
    # end _loadTimeZones()

    def _configureTimeZone(self):
        # 1) look for a command-line override
        # 2) look for a user prefs override
        # 3) try to figure out the TZ from the time.tzname info
        # 4) do nothing
        tzName = self._getCommandLineTZOverride()
        if tzName is None:
            tzName = self._getUserPrefsTZOverride()
        if tzName is None:
            tzName = self._divineTZFromPython()

        # Now, try to set the timezone if one was found
        if tzName is not None:
            tz = self.findTimeZone(tzName)
            if tz is not None:
                self.timeZone = tz
                setLocalTimezone(tz.getPyTimeZone())
    # end _configureTimeZone()

    def _getCommandLineTZOverride(self):
        # FIXME (EPW) impl command line TZ override
        return None
    # end _getCommandLineTZOverride()

    def _getUserPrefsTZOverride(self):
        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        tzName = userPrefs.getUserPreference(IZAppUserPrefsKeys.TIMEZONE, None)
        if tzName:
            return tzName
        else:
            return None
    # end _getUserPrefsTZOverride()

    def _divineTZFromPython(self):
        if time.tzname in self.tupleToTZNameMap:
            return self.tupleToTZNameMap[time.tzname]
        return None
    # end _divineTZFromPython()

    def getTimeZones(self):
        return self.timeZones
    # end getTimeZones()

    def getTimeZone(self):
        return self.timeZone
    # end getTimeZone()

    def setTimeZone(self, tzInfo):
        self.timeZone = tzInfo
        setLocalTimezone(tzInfo.getPyTimeZone())

        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        if tzInfo:
            userPrefs.setUserPreference(IZAppUserPrefsKeys.TIMEZONE, tzInfo.getName())
        else:
            userPrefs.setUserPreference(IZAppUserPrefsKeys.TIMEZONE, u"") #$NON-NLS-1$
    # end setTimeZone()

    def findTimeZone(self, tzName):
        for tz in self.timeZones:
            if tz.getName() == tzName:
                return tz
        return None
    # end findTimeZone()

# end ZTimeZoneService
