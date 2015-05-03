
class Observable(object):
    """
    Base class for observable objects.

    Note: This is a simple implementation, and does not cope
          with adding and removing observers during updating.
    """
    def __init__(self):
        """
        Constructor
        """
        self.observers = set()

    def add_observer(self, observer):
        """
        Adds an observer.
        """
        self.observers.add(observer)

    def remove_observer(self, observer):
        """
        Removes an observer.
        """
        self.observers.remove(observer)

    def remove_all_observers(self):
        """
        Removes all observers.
        """
        self.observers.clear()

    def update_observers(self):
        """
        Calls the updated() method in observers.
        """
        for observer in self.observers:
            observer.updated(self)
