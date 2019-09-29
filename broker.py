from feed import Feed


class Broker():

    def __init__(self, account):
        self.account = account
        self.feed = None
        self._init_feed()

    def _init_feed(self):
        products = self.account.get_products()
        product_list = []
        for product in products:
            product_list.append(product["id"])
        self.feed = Feed(self, self.account.sandbox, product_list, channels=["ticker"])

    def notify(self, product):
        print(product)

    def buy(self):
        self.account.buy()