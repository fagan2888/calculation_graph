
class Quality(object):
    """
    Manages an enum and a string indicating the quality of the data and
    calculations in a node.
    """

    # The quality 'enum'...
    GOOD = "Good"
    BAD = "Bad"

    def __init__(self):
        """
        The 'constructor'.
        """
        # The quality enum...
        self.quality = Quality.BAD

        # The string description...
        self.description = ""

    def clear_to_good(self):
        """
        Sets the quality to Good.
        """
        self.quality = Quality.GOOD
        self.description = ""




