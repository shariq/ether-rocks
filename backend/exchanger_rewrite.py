# exchanger rewite
from poloniex import poloniex
import time, threading, json, logging, sys, functools
from firebase import firebase
import subprocess
from subprocess import call
from tinydb import TinyDB, Query

firebase = firebase.FirebaseApplication("https://etherrocks.firebaseio.com", None)

#TODO create another firebase db for backup of already posted transactions

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


COMMISION = 0.03

#TODO add locks for multiple dbs


# got this number from these threads:
# https://www.reddit.com/r/ethtrader/comments/3g8eei/how_long_does_it_take_to_deposit_coins_on_poloniex/
# https://forum.ethereum.org/discussion/2835/how-do-i-check-number-of-confirmations-of-one-transactions
# Scratch that a mod from poloniex said 500 confirms or a couple hours
MIN_CONFIRMATIONS = 500
MIN_TIME = 3600 # TODO consider using this later

logging.basicConfig(filename='exchanger.log', level=logging.INFO)

# Transactions that have finished posting
postedTransactions = TinyDB('postedTransactions.db')

# Transactions that are still posted or finished posting
postingTransactions = TinyDB('postingTransactions.db')

# Transactions that haven't been exchanged for bitcoins
exchangingTransactions = TinyDB('exchangingTransactions.db')

transactions = TinyDB('transactions.db')
failedTransactions = TinyDB('failedTransactions.db')

#Send a user bitcoins minus commision
def sendUserBTC(tradeAmount, btcAddr):

    response = poloniexAcc.withdraw("BTC", usersAmount, btcAddr)

    if response and "error" not in response:
        logging.info("Successfully transfered " + str(usersAmount) + " bitcoins to: " + btcAddr)
        return True
    else:
        errMsg = "Could not transfer " + str(usersAmount) + " bitcoins to: " + btcAddr

        if "error" in response:
            errMsg += "\n response: " + str(response["error"])
        logging.warning(errMsg)

        return False

def add_if_not_in_set(l, s, itt):
    if itt not in s:
        l.append(itt)

# Post transactions to ether network
# TODO verify transaction destination, amount
def postEthTransactions():
    while True:
        firebaseTable = firebase.get('/', None)
        signedEtherTrans = set(firebaseTable.keys())

        postedEtherTrans = set(map((lambda s: s['signedTrans']), transactions.all()))

        # If not in postedEtherTrans the transaction must have already been set
        unpostedSignedTrans = filter(functools.partial(add_if_not_in_set, postedEtherTrans), signedEtherTrans) 

        # TODO delete debug
        print "postedEtherTrans: " + str(postedEtherTrans)
        print "unpostedSignedTrans: " + str(unpostedSignedTrans)

        # Get signed Eth transactions that have not been posted to the network
        for signedEtherTran in unpostedSignedTrans:
            transactionScript = "eth.sendRawTransaction(\"" + signedEtherTran + "\");"
            logging.info("sending eth command " + transactionScript)

            transactionID = subprocess.call(["geth", "--exec", transactionScript, "attach"])

            valueScript = "eth.getTransaction(\"" + transactionID + "\").value;"
            value = subprocess.call("geth", "--exec", valueScript, "attach"])

            if "error" in str(transactionID) or "Error" in str(value):
                #TODO handle failed transactions gracefully
                logging.warn("transaction for signedEtherTrans " + signedEtherTran + " failed")
                if "Error" in str(value):
                    logging.warn("Due to value error: " + str(value))
                print "error"  # TODO delete debug
                continue

            logging.info("TransactionID:" + str(transactionID))
            transactions.insert({"signedTrans": signedEtherTran, "txid":transactionID, "status":"confirming", "value": value, "postedAt": time.time()})



# Wait until a certain number of confirmations on ether transactions. 
def checkConfirmations():
    # signedEtherTrans = firebase.get('/', None)
    while True:
        # Wait at least an hour on transactions (since we expect the required number of confirmations to take several hours)
        for transEntry in db.search((Query().status == 'confirming') & (Query().postedAt + MIN_TIME <= time.time())):

            transID = transEntry["txid"]

            # TODO delete this comment web3.eth.blockNumber-web3.eth.getTransaction(transaction).blockNumber
            confirmationScript = "web3.eth.blockNumber-web3.eth.getTransaction(\"" + transID + "\").blockNumber;"
            confirmations = subprocess.call(["geth", "--exec", confirmationScript, "attach"])

            if confirmations >= MIN_CONFIRMATIONS:
                print "TODO ether transaction has >= " + str(MIN_CONFIRMATIONS) + " confirmations send user bitcoins"
                transactions.update({'status':'confirmed'}, Query().txid == transID)




def exhangeForBitcoin():
    while True:
        #TODO do query
        for transEntry in db.search((Query().status == 'confirmed')
            transID = transEntry["txid"]
            ether = transEntry["value"]
            #TODO figure out rate of bitcoin per ethereum from most recent trade
            btcPerEth = #TODO


            #Take off commision from actual trade amount
            profit = float(btcAmount) * COMMISION
            usersAmount = float(btcAmount) - profit

            userSentBTC = sendUserBTC()
            #TODO attempt to post bitcoin transaction
            if userSentBTC:
                transactions.update({'status':'complete'}, Query().txid == transID)



#connect to poloniex using key and secret file
apiKey = open('poloniexapi.key', 'r').read()
secret = open('poloniexapi.secret', 'r').read()
poloniexAcc = poloniex(apiKey, secret)

prevDepositHistory = {}


postEthTransactionsThread = threading.Thread(target=postEthTransactions)
postEthTransactionsThread.start()

checkConfirmationsThread = threading.Thread(target=checkConfirmations)
checkConfirmationsThread.start()
	
