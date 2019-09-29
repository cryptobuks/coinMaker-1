from account import Account
from broker import Broker
from feed import Feed

sandbox = True
if sandbox:
    with open("sandbox_credentials.cfg", "r") as fp:
        key, secret, password = fp.readline().split(":")
else:
    with open("credentials.cfg", "r") as fp:
        key, secret, password = fp.readline().split(":")

my_account = Account(key, secret, password, sandbox=sandbox)
broker = Broker(account=my_account)
