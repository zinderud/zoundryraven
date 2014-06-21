from zoundry.base import messages

# ------------------------------------------------------------------------------------
# Extends the base messages class in order to provide a different bundle name.
# ------------------------------------------------------------------------------------
class ZMessages(messages.ZMessages):

    def __init__(self):
        messages.ZMessages.__init__(self)
    # end __init__()

    def _getBundleName(self):
        return u"zoundry.appframework.xml" #$NON-NLS-1$
    # end _getBundleName()

# end ZBundleCollection

MESSAGES = ZMessages()

def _extstr(name):
    global MESSAGES
    val = MESSAGES.getString(name)
    if not val:
        val = u"!!%s!!" % name #$NON-NLS-1$
    return val
# end _extstr()
