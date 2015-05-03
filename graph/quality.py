
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
        self._quality = Quality.BAD

        # The string descriptions...
        self.descriptions = set()

    def clear_to_good(self):
        """
        Sets the quality to Good.
        """
        self._quality = Quality.GOOD
        self.descriptions.clear()

    def get_quality(self):
        """
        Returns the quality enum.
        """
        return self._quality

    def get_description(self):
        """
        Returns a string description by joining the set of descriptions.
        """
        return "; ".join(self.descriptions)

    def merge(self, quality, description=None):
        """
        Merges quality with the data passed in.

        This function is 'overloaded':
        a. quality=Quality.GOOD/BAD, description=string
        b. quality=a Quality object, description=None
        """
        if description is not None:
            # a. We have a quality and description...
            self._merge_quality(quality)
            self.descriptions.add(description)
        else:
            # b. We are merging another Quality object...
            self._merge_quality(quality.quality)
            self.descriptions |= quality.descriptions

    def _merge_quality(self, quality):
        """
        Merges our quality with the quality passed in.
        """
        if quality == Quality.BAD:
            self._quality = Quality.BAD




