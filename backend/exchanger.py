from poloniex import poloniex
import time, pickledb, threading, json, logging, sys
from threading import Thread, Lock



COMMISION = 0.03

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


dbLock = Lock()

# Orders that have finished processing
# deposit => order number
processedDeposits = pickledb.load('processedDeposits.db', False)
forever(processedDeposits.dump)

# Orders that are still processing
# deposit => order number
processingDeposits = pickledb.load('processingDeposits.db', False)
forever(processingDeposits.dump)

# order number => deposits
# Works with processing deposits for 2 way mapping of: order number <=> deposits
# TODO could implement 2 way mapping. Maybe wrap both in class.
processingTrades = pickledb.load('processingTrades.db', False)
forever(processingTrades.dump)

#connect to poloniex using key and secret file
apiKey = open('poloniexapi.key', 'r').read()
secret = open('poloniexapi.secret', 'r').read()
poloniexAcc = poloniex(apiKey, secret)


#Check if I have enough ether to sell
#raise error if trying to sell more eth than we have
def checkBalance(ethAmount):
    #Safety: Checking if I have enough ether to sell
    #If this under then there is an error
    balances = poloniexAcc.returnBalances()
    ethBalance = balances["ETH"]
    if(ethBalance < ethAmount):
        raise error("Error: trying to sell more ether then we have this state should never be reached")


#Get rate of bitcoins per ethereum
#rate is based on BTC per ETH
#Calculating it by getting the average of the lowest 24 hour score and last price
#TODO make sure if this is fine with shariq. It still does sell fast.
def getBtcPerEth():
    ticker = poloniexAcc.returnTicker()
    btc_eth = ticker["BTC_ETH"]

    return (float(btc_eth["low24hr"]) + float(btc_eth["last"]))/2


def processDeposit(deposit):

    depositID = generateDepositID(deposit)
    ethAmount = float(deposit["amount"])

    #TODO verify if ethAmount is over minimum. If it is should we return it or just keep it?

    logging.info("Processing deposit: \'" + depositID + "\' ether: " + str(ethAmount))

    if depositID not in processedDeposits.db:
        checkBalance(ethAmount)

        btcPerEth = getBtcPerEth()

        logging.info("Selling " + str(ethAmount) + " ether at " + str(btcPerEth) + " bitcoins per ether")
        orderInfo = poloniexAcc.sell("BTC_ETH", btcPerEth, ethAmount)

        logging.info("orderInfo: " + str(orderInfo))

        if orderInfo and "error" not in orderInfo:  # If orderInfo is returned and there is no error
            orderNum = orderInfo["orderNumber"]
            logging.info("Placed order for depositID: " + depositID + " poloniex order number: " + str(orderNum))
            processingDeposits.set(depositID, str(orderNum))
            processingTrades.set(str(orderNum), depositID)
            return True
        else:
            logging.warning("Unable to place poloniex order for: " + str(deposit) + " order info: " + str(order))
            return False
    else:
        logging.debug("Already processed deposit: " + depositID)

#Send a user bitcoins minus commision
def sendUserBTC(tradeAmount, btcAddr):

    #Take off commision from actual trade amount
    profit = float(tradeAmount) * COMMISION
    usersAmount = float(tradeAmount) - profit

    response = poloniexAcc.withdraw("BTC", usersAmount, btcAddr)

    if response and "error" not in response:
        logging.info("Successfully transfered " + str(usersAmount) + " bitcoins to: " + btcAddr)
        logging.info("Actual trade amount: " + str(tradeAmount) + " profit: " + str(profit))
    else:
        errMsg = "Could not transfer " + str(usersAmount) + " bitcoins to: " + btcAddr

        if "error" in response:
            errMsg += "\n response: " + str(response["error"])
            if "Not enough BTC" in response["error"]:
                logging.critical(errMsg)
                #Exit if not enough bitcoins. Should never reach this state.
                #Maybe someone is trying to exploit us
                sys.exit(errMsg)

        logging.warning(errMsg)


#TODO create another thread to monitor processing trades.
#If any orders are still processing then check their status
#If finished forward to corresponding address
def checkProcessingOrders():

    while True:

        #print "Checking processing orders"
        tradeHistory = poloniexAcc.returnTradeHistory("BTC_ETH")

        for trades in tradeHistory:

            orderNum = trades["orderNumber"]
            # fee = trades["fee"]  # fees in btc
            ethAmount = trades["amount"]
            btcAmount = trades["total"]

            dbLock.acquire()

            #Only look at trades that are still proceessing
            if str(orderNum) in processingTrades.db:
                depositID = processingTrades.get(str(orderNum))
                logging.info("Order number finished: " + orderNum + " "
                             + str(ethAmount) + " ether traded for "
                             + str(btcAmount) + " BTC. depositID: "
                             + depositID)
                processingTrades.rem(str(orderNum))
                processingDeposits.rem(depositID)

                processedDeposits.set(depositID, str(orderNum))

                #Send user converted bitcoins
                userAddress = "TODO"  # TODO
                sendUserBTC(btcAmount, userAddress)

            dbLock.release()


#Generate a "unique" id by using a timestamp and amount
#Note probably not actually unique
def generateDepositID(deposit):
    return "timestamp:" + str(deposit["timestamp"]) + " amount:" + deposit["amount"]

checkProcessingThread = threading.Thread(target=checkProcessingOrders)
checkProcessingThread.start

prevDepositHistory = {}
while True:

    #TODO could use a timed wait until depositHistory != previousHistory to
    #avoid unneeded work but have checkProcessingOrders() on another thread

    #Get withdrawel and deposit history up to current time
    currTime = str(time.time())
    #TODO consider setting start time to a week ago or at some period of time to avoid unneeded work on old deposits

    depositHistory = poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime})["deposits"]
    while (depositHistory == prevDepositHistory):
        # Wait until there are new deposits to process
        depositHistory = poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime})["deposits"]
        time.sleep(1)

    #For deposits not already traded
    for deposit in depositHistory:
        depositId = generateDepositID(deposit)
        #Some deposits are pending or whateves ignore them
        if deposit["status"] == "COMPLETE" and deposit["currency"] == "ETH":
            dbLock.acquire()
            if not processingDeposits.get(depositId) and not processedDeposits.get(depositId):
                processDeposit(deposit) # TODO create thread threading.Thread(target=deposit,args=)
            dbLock.release()

    #checkProcessingOrders()
    prevDepositHistory = depositHistory

    time.sleep(1)  # TODO consider deletion
