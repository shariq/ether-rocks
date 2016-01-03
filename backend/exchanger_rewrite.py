# exchanger rewite
# When receiving eth trade for btc on exchange
# Then transfer to 

from poloniex import poloniex
import time, pickledb, threading, json, logging, sys

#connect to poloniex using key and secret file
apiKey = open('poloniexapi.key', 'r').read()
secret = open('poloniexapi.secret', 'r').read()
poloniexAcc = poloniex(apiKey, secret)

while True:
    #Get withdrawel and deposit history up to current time
    currTime = str(time.time())
    #TODO consider setting start time to a week ago or at some period of time to avoid unneeded work on old deposits

    depositHistory = poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime})["deposits"]
    while (depositHistory == prevDepositHistory):
        # Wait until there are new deposits to process
        depositHistory = poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime})["deposits"]
        time.sleep(1)

    prevDepositHistory = depositHistory
