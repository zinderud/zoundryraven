from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.ui.events.viewevents import ZViewSelectionEvent
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZViewSelection

def fireViewEvent(event):
    getApplicationModel().getViewRegistry().fireViewEvent(event)
# end fireViewEvent()

def fireViewSelectionEvent(selection, view = None):
    event = ZViewSelectionEvent(view, selection)
    fireViewEvent(event)
# end fireViewSelectionEvent()

def fireViewUnselectionEvent():
    fireViewSelectionEvent(ZViewSelection(IZViewSelectionTypes.EMPTY_SELECTION, None));
# end fireViewUnselectionEvent()
