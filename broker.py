from bookFeed import BookFeed


class Broker():

    def __init__(self, account, product_list=None):
        self.account = account
        self.product_list = product_list
        self.order_book = {}
        self.feed = None
        self._init_feed()

    def _init_feed(self):
        if self.product_list is None:
            products = self.account.get_products()
            self.product_list = []
            for product in products:
                self.product_list.append(product["id"])
        self.feed = BookFeed(self, self.account.sandbox, self.product_list, channels=["level2"])
        self.order_book = self.feed.order_book

    def get_products(self):
        return self.product_list

    def notify(self, product):
        book = self.feed.order_book[product]

    def buy(self):
        self.account.buy()