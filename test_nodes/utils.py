
class Utils(object):
    """
    Static helper functions.
    """
    @staticmethod
    def split_currency_pair(currency_pair):
        """
        Returns the two currencies from a currency pair passed
        in like "EUR/USD".
        """
        return currency_pair[:3], currency_pair[-3:]


