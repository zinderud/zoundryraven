
# ------------------------------------------------------------------------------
# Base class for all ZList impls.
# ------------------------------------------------------------------------------
class ZBaseList:

    def __init__(self):
        self.data = []
    # end __init__()

    def add(self, item):
        self.data.append(item)
    # end add()

    def addAll(self, list):
        for item in list:
            self.add(item)
    # end addAll()

    def append(self, item):
        self.add(item)
    # end append()
    
    def getLast(self):
        if self.isEmpty():
            return None
        return self[self.size() - 1]
    # end getLast()

    def remove(self, item):
        if item in self.data:
            self.data.remove(item)
            return True
        return False
    # end remove()
    
    def size(self):
        return len(self.data)
    # end size()

    def contains(self, item):
        return item in self.data
    # end contains()

    def isEmpty(self):
        return len(self.data) == 0
    # end isEmpty()

    def __len__(self):
        return self.size()
    # end __len__()

    def __contains__(self, item):
        return self.contains(item)
    # end __contains__()

    def __iter__(self):
        return self.data.__iter__()
    # end __iter__()

    def __getitem__(self, index):
        return self.data[index]
    # end __getitem__()

# end ZBaseList


# ------------------------------------------------------------------------------
# Interface used to compare two objects.
# ------------------------------------------------------------------------------
class IZComparator:

    def compare(self, object1, object2):
        u"""compare(object, object) -> int
        Compares the two objects and returns -1 (if object1
        is less than object2) or 0 (if the two objects are
        equal) or 1 (if object1 is greater than object2).""" #$NON-NLS-1$
    # end compare()

    def equals(self, object1, object2):
        u"""equals(object, object) -> boolean
        Returns True if the two objects are equal.  A
        comparator will typically call compare() and
        return True if the result is 0.  However, it
        may be desirable for equals() to be more
        precise than compare() when items in a list
        are sorted by weight, but removed by identity.""" #$NON-NLS-1$
    # end equals()

# end IZComparator


# ------------------------------------------------------------------------------
# A default comparator implementation.
# ------------------------------------------------------------------------------
class ZDefaultListComparator(IZComparator):

    def compare(self, object1, object2):
        if object1 < object2:
            return -1
        if object1 > object2:
            return 1
        return 0
    # end compare()

    def equals(self, object1, object2):
        return object1 == object2
    # end equals()

# end ZDefaultListComparator


# ------------------------------------------------------------------------------
# A list implementation that uses a IZComparator to keep the items in the list
# sorted.
# ------------------------------------------------------------------------------
class ZSortedList(ZBaseList):

    def __init__(self, comparator = None):
        ZBaseList.__init__(self)
        self.comparator = comparator
        if self.comparator is None:
            self.comparator = ZDefaultListComparator()
    # end __init__()

    # TODO use quick insert rather than linear insert
    def add(self, item):
        for idx in range(0, len(self.data)):
            dataItem = self.data[idx]
            if self.comparator.compare(item, dataItem) == -1:
                self.data.insert(idx, item)
                return
        self.data.append(item)
    # end add()

    def remove(self, item):
        for dataItem in self.data:
            if self.comparator.equals(item, dataItem):
                self.data.remove(dataItem)
                return True
    # end remove()

    def contains(self, item):
        for dataItem in self.data:
            if self.comparator.equals(item, dataItem):
                return True
        return False
    # end contains()

# end ZSortedList


# ------------------------------------------------------------------------------
# A set implementation that uses a IZComparator to keep the items in the set
# sorted.
# ------------------------------------------------------------------------------
class ZSortedSet(ZSortedList):

    def __init__(self, comparator = None):
        ZSortedList.__init__(self, comparator)
    # end __init__()

    def add(self, item):
        if not self.contains(item):
            ZSortedList.add(self, item)
            return True
        return False
    # end add()

# end ZSortedSet


# ------------------------------------------------------------------------------
# List impl where the items are sorted by 'most recently used' first.
# ------------------------------------------------------------------------------
class ZMruList(ZBaseList):

    def __init__(self):
        ZBaseList.__init__(self)
    # end __init__()

    def add(self, item):
        if self.contains(item):
            self.remove(item)
        self.data.insert(0, item)
    # end add()

# end ZMruList


# ------------------------------------------------------------------------------
# List impl where the items are sorted by 'most recently used' first, and the
# list is prevented from growing beyond a certain size.
# ------------------------------------------------------------------------------
class ZBoundedMruList(ZMruList):

    def __init__(self, maxSize):
        self.maxSize = maxSize

        ZMruList.__init__(self)
    # end __init__()

    def add(self, item):
        ZMruList.add(self, item)
        if self.size() > self.maxSize:
            self.remove(self.getLast())
    # end add()
    
# end ZBoundedMruList
