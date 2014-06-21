import wx

# -------------------------------------------------------------------------------------
# A simple password text control.  This basically just extends TextCtrl and adds the
# password style.
# -------------------------------------------------------------------------------------
class ZPasswordCtrl(wx.TextCtrl):

    def __init__(self, parent, id, value, pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0, name = u"ZPasswordCtrl"): #$NON-NLS-1$
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style | wx.TE_PASSWORD, name = name)
    # end __init__()

# end ZPasswordCtrl
