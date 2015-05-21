
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
        self._descriptions = set()

    def __eq__(self, other):
        """
        Returns True if this object is the same as other.
        """
        if self._quality != other._quality:
            return False
        if self._descriptions != other._descriptions:
            return False
        return True

    def clear_to_good(self):
        """
        Sets the quality to Good and clears the collection of descriptions.
        """
        self._quality = Quality.GOOD
        self._descriptions.clear()

    def set_to_bad(self, description):
        """
        Sets the quality to Bad with the description passed in.

        Note: Normally you would merge quality, to preserve any
              other descriptions. Sometimes, though, you just need
              to directly set the quality Bad with a known description.
        """
        self._quality = Quality.BAD
        self._descriptions.clear()
        self._descriptions.add(description)

    def set_from(self, other):
        """
        Sets our state from 'other'.
        """
        self._quality = other._quality
        self._descriptions = other._descriptions.copy()

    def get_quality(self):
        """
        Returns the quality enum.
        """
        return self._quality

    def get_description(self):
        """
        Returns a string description by joining the set of descriptions.
        """
        return "; ".join(self._descriptions)

    def is_good(self):
        """
        Returns True if the quality is GOOD.
        """
        return (self._quality == Quality.GOOD)

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
            self._descriptions.add(description)
        else:
            # b. We are merging another Quality object...
            self._merge_quality(quality._quality)
            self._descriptions |= quality._descriptions

    def _merge_quality(self, quality):
        """
        Merges our quality with the quality passed in.
        """
        if quality == Quality.BAD:
            self._quality = Quality.BAD




