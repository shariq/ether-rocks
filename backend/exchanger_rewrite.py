# exchanger rewite

from poloniex import poloniex
import time, pickledb, threading, json, logging, sys
from firebase import firebase
firebase = firebase.FirebaseApplication("https://etherrocks.firebaseio.com", None)

COMMISION = 0.03

logging.basicConfig(filename='exchanger.log', level=logging.INFO)

# Transactions that have finished processing
processedTransactions = pickledb.load('processedTransactions.db', False)
forever(processedDeposits.dump)

# Transactions that are still processing or finished processing
# deposit => order number
processingTransactions = pickledb.load('processingTransactions.db', False)
forever(processingDeposits.dump)


def forever(func, seconds=1):
    def helper():
        while True:
            try:
                func()
            except:
                pass
            time.sleep(seconds)
    t = threading.Thread(target=helper)
    t.daemon = True
    t.start()


# Post transactions to ether network
def postEthTransactions():
    while True:
        signedEtherTrans = firebase.get('/', None)

        # Get signed Eth transactions that have not been posted to the network
        for signedEtherTran in (set(signedEtherTrans.keys())
                                - set(processingTransactions.getall())):
            print "TODO post signed ether transaction on ether network"
            processingTransactions.set(signedEtherTran, True)


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

