from zoundry.base import messages

# ------------------------------------------------------------------------------------
# Extends the base messages class in order to provide a different bundle name.
# ------------------------------------------------------------------------------------
class ZMessages(messages.ZMessages):

    def __init__(self):
        messages.ZMessages.__init__(self)
    # end __init__()

    def _getBundleName(self):
        return u"zoundry.blogapp.xml" #$NON-NLS-1$
    # end _getBundleName()

# end ZBundleCollection

MESSAGES = None

def getMessages():
    global MESSAGES
    if MESSAGES is None:
        MESSAGES = ZMessages()
    return MESSAGES
# end getMessages()

def _extstr(name):
    val = getMessages().getString(name)
    if not val:
        val = u"!!%s!!" % name #$NON-NLS-1$
    return val
# end _extstr()
