from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.widgets.controls.listex import ZRadioBoxListView
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.templates.templatemanagermodel import ZTemplateManagerModel
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.subpage import ZAccountPrefsSubPage
from zoundry.blogapp.ui.templates.templatemanagerui import ZTemplateCheckBoxListProvider
import wx

# ------------------------------------------------------------------------------
# Implements the account preferences sub-page for template options.
# ------------------------------------------------------------------------------
class ZTemplatePrefSubPage(ZAccountPrefsSubPage):

    def __init__(self, parent, session):
        self.model = ZTemplateManagerModel()

        ZAccountPrefsSubPage.__init__(self, parent, session)
    # end __init__()

    def _createWidgets(self):
        self._createTemplateWidgets(self)
    # end _createWidgets()

    def _createTemplateWidgets(self, parent):
        self.staticBox = wx.StaticBox(parent, wx.ID_ANY, _extstr(u"templatesubpage.ChooseTemplate")) #$NON-NLS-1$
        self.contentProvider = ZTemplateCheckBoxListProvider(self.model)
        self.templates = ZRadioBoxListView(self.contentProvider, parent, wx.ID_ANY)
    # end _createTemplateWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onTemplateCheckListChange, self.templates)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        templateId = self.session.getTemplateId()
        self.contentProvider.setSelectedTemplateId(templateId)
        self.templates.refreshItems()
    # end _populateWidgets()

    def _layoutWidgets(self):
        sizer = self._createTemplateLayout()

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def _createTemplateLayout(self):
        sbSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        sbSizer.Add(self.templates, 1, wx.EXPAND | wx.ALL, 8)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(sbSizer, 1, wx.ALL | wx.EXPAND, 5)

        return box
    # end _createTemplateLayout()

    def onTemplateCheckListChange(self, event):
        templateId = self.contentProvider.getSelectedTemplateId()
        if templateId:
            self.session.setTemplateId(templateId)
        event.Skip()
    # end onTemplateSelected()

# end ZTemplatePrefSubPage
