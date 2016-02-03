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

#TODO add locks for multiple dbs


# got this number from these threads:
# https://www.reddit.com/r/ethtrader/comments/3g8eei/how_long_does_it_take_to_deposit_coins_on_poloniex/
# https://forum.ethereum.org/discussion/2835/how-do-i-check-number-of-confirmations-of-one-transactions
MIN_CONFIRMATIONS = 6000
MIN_TIME = 600

logging.basicConfig(filename='exchanger.log', level=logging.INFO)

# Transactions that have finished posting
postedTransactions = pickledb.load('postedTransactions.db', False)
forever(postedTransactions.dump)

# Transactions that are still posted or finished posting
postingTransactions = pickledb.load('postingTransactions.db', False)
forever(postingTransactions.dump)

# Transactions that haven't been exchanged for bitcoins
exchangingTransactions = pickledb.load('exchangingTransactions.db', False)
forever(exchangingTransactions.dump)


#Send a user bitcoins minus commision
def sendUserBTC(tradeAmount, btcAddr):

    #Take off commision from actual trade amount
    profit = float(tradeAmount) * COMMISION
    usersAmount = float(tradeAmount) - profit

    response = poloniexAcc.withdraw("BTC", usersAmount, btcAddr)

    if response and "error" not in response:
        logging.info("Successfully transfered " + str(usersAmount) + " bitcoins to: " + btcAddr)
        logging.info("Actual trade amount: " + str(tradeAmount) + " profit: " + str(profit))
        return True
    else:
        errMsg = "Could not transfer " + str(usersAmount) + " bitcoins to: " + btcAddr

        if "error" in response:
            errMsg += "\n response: " + str(response["error"])
        logging.warning(errMsg)

        return False



# Post transactions to ether network
# TODO verify transaction destination, amount
def postEthTransactions():
    while True:
        firebaseTable = firebase.get('/', None)
        signedEtherTrans = set(firebaseTable.keys())

        # Get signed Eth transactions that have not been posted to the network
        for signedEtherTran in (signedEtherTrans
                                - set(postingTransactions.getall())):
            transactionScript = "eth.sendRawTransaction(\"" + signedEtherTran + "\");"
            logging.info("sending eth command " + transactionScript)

            transactionID = subprocess.call(["geth", "--exec", transactionScript, "attach"])
    
            if "error" in str(transactionID):
                logging.warn("transaction for signedEtherTrans " + signedEtherTran + " failed")
                print "error"
                continue

            logging.info("TransactionID:" + str(transactionID))
            postingTransactions.set(signedEtherTran, transactionID)



# Wait until 200 confirmations on ether transactions. When done put in postedTransactions
def checkConfirmations():
    # signedEtherTrans = firebase.get('/', None)
    while True:
        for signedTran in (set(postingTransactions.getall())
                            - set(postedTransactions.getall())):
            transID = processingTransactions.get(signedTran)
            # web3.eth.blockNumber-web3.eth.getTransaction(transaction).blockNumber
            confirmationScript = "web3.eth.blockNumber-web3.eth.getTransaction(\"" + transaction + "\").blockNumber;"
            confirmations = subprocess.call(["geth", "--exec", confirmationScript, "attach"])

            if confirmations >= MIN_CONFIRMATIONS:
                print "TODO ether transaction has >= " + str(MIN_CONFIRMATIONS) + " confirmations send user bitcoins"
                postedTransactions.set(signedTran, transID)
                exchangingTransactions.set(transID, time.time())



def exhangeForBitcoin():
    while True:
        for transID in exchangingTransactions:
            if time.time() > exchangingTransactions.get(transID) + MIN_TIME:
                userSentBTC = sendUserBTC
                #TODO attempt to post bitcoin transaction
                if userSentBTC:
                    exchangingTransactions.rem(transID)



#connect to poloniex using key and secret file
apiKey = open('poloniexapi.key', 'r').read()
secret = open('poloniexapi.secret', 'r').read()
poloniexAcc = poloniex(apiKey, secret)

prevDepositHistory = {}


postEthTransactionsThread = threading.Thread(target=postEthTransactions)
postEthTransactionsThread.start()

checkConfirmationsThread = threading.Thread(target=checkConfirmations)
checkConfirmationsThread.start()
	
