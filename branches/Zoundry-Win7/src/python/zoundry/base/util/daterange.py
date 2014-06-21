from zoundry.base.util.zdatetime import ZLocalTimezone
from zoundry.base.util.zdatetime import createDateTime

# ----------------------------------------------------------------------------------
# Creates a start date for a range (local time).
# ----------------------------------------------------------------------------------
def createStartDate(year, month, day):
    return createDateTime(year, month, day, 0, 0, 0, ZLocalTimezone())
# end createStartDate()


# ----------------------------------------------------------------------------------
# Creates an end date for a range (local time).
# ----------------------------------------------------------------------------------
def createEndDate(year, month, day):
    return createDateTime(year, month, day, 23, 59, 59, ZLocalTimezone())
# end createEndDate()


# ----------------------------------------------------------------------------------
# This class represents a simple range of dates.  It has a start of the range and
# an end of the range.
# ----------------------------------------------------------------------------------
class ZDateRange:

    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate
    # end __init__()
    
    def getStartDate(self):
        u"getStartDate() -> ZSchemaDateTime" #$NON-NLS-1$
        return self.startDate
    # end getStartDate()
    
    def getEndDate(self):
        u"getEndDate() -> ZSchemaDateTime" #$NON-NLS-1$
        return self.endDate
    # end getEndDate()

    def isDateInRange(self, date):
        u"""isDateInRange(ZSchemaDateTime) -> boolean
        Returns True if the given date is within the range
        represented by this object (inclusive).""" #$NON-NLS-1$
        return date >= self.startDate and date <= self.endDate
    # end isDateInRange()

    def __str__(self):
        return u"ZDateRange [%s -> %s]" % (self.getStartDate(), self.getEndDate()) #$NON-NLS-1$
    # end __str__()
    
    def __repr__(self):
        return unicode(self)
    # end __repr__()
    
# end ZDateRange
