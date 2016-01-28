# exchanger rewite
from poloniex import poloniex
import time, pickledb, threading, json, logging, sys
from firebase import firebase
import subprocess
from subprocess import call

firebase = firebase.FirebaseApplication("https://etherrocks.firebaseio.com", None)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

# TODO find a way to log to both stdout and file
# ch = logging.StreamHandler(sys.stdout)
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# root.addHandler(ch)

# ch = logging.StreamHandler('exchanger.log')
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# root.addHandler(ch)

logging.basicConfig(filename='exchanger.log', level=logging.INFO)

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

COMMISION = 0.03
MIN_CONFIRMATIONS = 200

logging.basicConfig(filename='exchanger.log', level=logging.INFO)

# Transactions that have finished processing
processedTransactions = pickledb.load('processedTransactions.db', False)
forever(processedTransactions.dump)

# Transactions that are still processing or finished processing
processingTransactions = pickledb.load('processingTransactions.db', False)
forever(processingTransactions.dump)



# Post transactions to ether network
def postEthTransactions():
    while True:
        print "hi"
        firebaseTable = firebase.get('/', None)
        signedEtherTrans = set(firebaseTable.keys())

        # Get signed Eth transactions that have not been posted to the network
        for signedEtherTran in (signedEtherTrans
                                - set(processingTransactions.getall())):
            transactionScript = "eth.sendRawTransaction(\"" + signedEtherTran + "\");"
            logging.info("sending eth command " + transactionScript)

            # TODO Shariq: is it ok if I execute command line calls
            transactionID = subprocess.call(["geth", "--exec", transactionScript, "attach"])
    
            if "error" in str(transactionID):
                logging.warn("transaction for signedEtherTrans " + signedEtherTran + " failed")
                print "error"
                continue

            logging.info("TransactionID:" + str(transactionID))
            processingTransactions.set(signedEtherTran, transactionID)



# Wait until 200 confirmations on ether transactions. When done send bitcoins to user if available
def checkConfirmations():
    signedEtherTrans = firebase.get('/', None)
    while True:
        for transaction in (set(processingTransactions.getall())
                            - set(processedTransactions.getall())):
            print "TODO check if transaction: " + str(transaction) + " has 200 confirmations"
            confirmations = 200 # TODO get from ether api

            if confirmations >= MIN_CONFIRMATIONS:
                print "TODO ether transaction has >= 200 confirmations send user bitcoins"
                processedTransactions.set(transaction, True)



#connect to poloniex using key and secret file
apiKey = open('poloniexapi.key', 'r').read()
secret = open('poloniexapi.secret', 'r').read()
poloniexAcc = poloniex(apiKey, secret)

prevDepositHistory = {}


postEthTransactionsThread = threading.Thread(target=postEthTransactions)
postEthTransactionsThread.start

checkConfirmationsThread = threading.Thread(target=checkConfirmations)
checkConfirmationsThread.start
	
