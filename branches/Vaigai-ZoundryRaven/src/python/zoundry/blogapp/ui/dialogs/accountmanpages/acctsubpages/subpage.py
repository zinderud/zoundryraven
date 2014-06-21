from zoundry.appframework.ui.widgets.controls.validating.validatingpanel import ZValidatingPanel

# ------------------------------------------------------------------------------
# Base class for the account prefs sub pages.
# ------------------------------------------------------------------------------
class ZAccountPrefsSubPage(ZValidatingPanel):

    def __init__(self, parent, session):
        self.parent = parent
        self.session = session

        ZValidatingPanel.__init__(self, parent)

        self._createWidgets()
        self._bindWidgetEvents()
        self._populateWidgets()
        self._layoutWidgets()
    # end __init__()

    def _getSession(self):
        return self.session
    # end _getSession()

    def _createWidgets(self):
        pass
    # end _createWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _layoutWidgets(self):
        pass
    # end _layoutWidgets()

# end ZAccountPrefsSubPage
