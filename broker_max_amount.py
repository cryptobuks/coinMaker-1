import math

from broker import Broker

class BrokerMaxAmount(Broker):

    def check_possible_new_transactions(self):
        refresh = False
        for currency in self.account.watched_currencies:
            value = self.account.wallet[currency]
            for product_id in value["in_products"]:
                product = self.account.products[product_id]
                if product["base_currency"] == currency:
                    side = "buy"
                    decimals = int(-math.log10(float(product["quote_increment"])))
                else:
                    side = "sell"
                    decimals = int(-math.log10(float(product["quote_increment"])))

                if len(product["open_transactions"][side]) == 0 and len(product["done_transactions"][side]) > 0:
                    last_done = product["done_transactions"][side][0]
                    min = float(product["base_min_size"])
                    last_price = float(last_done["price"])
                    new_price = None
                    try:
                        if side == "buy":
                            second_lowest = self.account.feed.order_book[product_id]["bids"][0][0]
                            price_diff = second_lowest - last_price
                            new_amount = min
                            if price_diff < 0:
                                new_price = second_lowest
                        else:
                            second_highest = self.account.feed.order_book[product_id]["asks"][0][0]
                            price_diff = second_highest - last_price
                            new_amount = min
                            if price_diff > 0:
                                new_price = second_highest
                    except KeyError:
                        continue

                    if new_price is not None:
                        base, quoted = product_id.split("-")
                        if side == "buy" and float(self.account.wallet[quoted]["available"]) <= new_price * new_amount:
                            continue
                        elif side == "sell" and float(self.account.wallet[base]["available"]) <= new_amount:
                            continue
                        print(self.account.place_limit_order(product_id=product_id, side=side, price=new_price,
                                                             size=new_amount))
                        refresh = True

        if refresh:
            print("from here?")
            self.account.update()