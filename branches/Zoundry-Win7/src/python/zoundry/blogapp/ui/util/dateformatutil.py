from zoundry.base.util.text.unicodeutil import convertToUnicode

# ------------------------------------------------------------------------------
# Convenience functions formatting dates for display
# ------------------------------------------------------------------------------

def _format(zschemaDateTime, pattern, localTime=False):
    if not pattern:
        pattern = u"%c"#$NON-NLS-1$
    if zschemaDateTime is not None:
        return convertToUnicode(zschemaDateTime.toString(pattern, localTime))
    else:
        return u"" #$NON-NLS-1$
# end _format

def formatLocalDateAndTime(zschemaDateTime):
    # FIXME (PJ) extern date time format
    return _format(zschemaDateTime, u"%c", True) #$NON-NLS-1$ #$NON-NLS-2$
# end formatLocalDateAndTime()

def formatLocalDate(zschemaDateTime):
    # FIXME (PJ) extern date time format
    return _format(zschemaDateTime, u"%c", True) #$NON-NLS-1$ #$NON-NLS-2$
# end formatLocalDate()

def formatLocalTime(zschemaDateTime):
    # FIXME (PJ) extern date time format
    return _format(zschemaDateTime, u"%c", True) #$NON-NLS-1$ #$NON-NLS-2$
# end formatLocalTime()
