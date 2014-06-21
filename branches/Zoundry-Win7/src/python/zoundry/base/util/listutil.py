
# ------------------------------------------------------------------------------
# A single list difference.  When the differences between two lists is gotten,
# a list of instances of ZListDiff is returned.
# ------------------------------------------------------------------------------
class ZListDiff:

    def __init__(self, obj, position):
        self.obj = obj
        self.position = position
    # end __init__()
    
    def getObject(self):
        return self.obj
    # end getObject()
    
    def getPosition(self):
        return self.position
    # end getPosition()

# end ZListDiff


# ------------------------------------------------------------------------------
# Safe list getter - if the list is too small or is None, this returns None.
# ------------------------------------------------------------------------------
def getSafeListItemAtIdx(aList, idx):
    if aList is None:
        return None
    if idx < len(aList):
        return aList[idx]
    return None
# end getSafeListItemAtIdx()


# ------------------------------------------------------------------------------
# Returns a difference between two lists as a list of ZListDiff objects.
# ------------------------------------------------------------------------------
#def diffLists(startList, endList):
#    done = False
#    idx = 0
#    # FIXME (EPW) implement diffLists() and use it in the various custom widgets that need to refresh()
#    # See panellist.py (ZPanelListBoxInternal) for algorithm
#    while not done:
#        pass
## end diffLists()
