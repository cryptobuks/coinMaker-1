from bookFeed import BookFeed


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
        self.feed = BookFeed(self, self.account.sandbox, product_list, channels=["level2"])

    def notify(self, product):
        book = self.feed.order_book[product]

    def buy(self):
        self.account.buy()