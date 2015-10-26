from poloniex import poloniex
import time, pickledb, threading, json

#TODO realized too late that I could just convert ether as I receive them. 
#I don't have to do this on each individual deposit

#TODO maybe add functions to check on failing bitcoin transfers to users

def forever(func, seconds = 1):
    def helper():
        while True:
            try:
                func()
            except:
                pass
            time.sleep(seconds)
    t = threading.Thread(target = helper)
    t.daemon = True
    t.start()

# deposit => order number
processedDeposits = pickledb.load('processedDeposits.db', False)
forever(processedDeposits.dump)

# deposit => order number
processingDeposits = pickledb.load('processingDeposits.db', False)
forever(processingDeposits.dump)

# order number => deposits
# Works with processing deposits for 2 way mapping of: order number <=> deposits
#TODO implement 2 way mapping. Maybe wrap both in class
processingTrades = pickledb.load('processingTrades.db', False)
forever(processingTrades.dump)

#connect to poloniex using key and secret file
apiKey = open('poloniexapi.key', 'r').read()
secret = open('poloniexapi.secret', 'r').read()
poloniexAcc = poloniex(apiKey, secret)

prehistory = {}

COMMISION = 0.03

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
#TODO make sure if this is fine with shariq
def getBtcPerEth():
	ticker = poloniexAcc.returnTicker()
	btc_eth = ticker["BTC_ETH"]

	return (float(btc_eth["low24hr"]) + float(btc_eth["last"]))/2

#TODO ask shariq did you say to only process 1 deposit at a time?
def processDeposit(deposit):

	depositID = generateDepositID(deposit)
	ethAmount = float(deposit["amount"])

	#TODO verify if ethAmount is over minimum

	print "Processing deposit: \'" + depositID + "\' ether: " + str(ethAmount)

	if depositID not in processedDeposits.db:
		checkBalance(ethAmount)

		btcPerEth = getBtcPerEth()

		print "Selling " + str(ethAmount) + " ether at " + str(btcPerEth) + " bitcoins per ether" 
		order = poloniexAcc.sell("BTC_ETH", btcPerEth, ethAmount)

		print "order: " + str(order)

		if order and "error" not in order: 	#If order is returned and there is no error
			orderNum = order["orderNumber"]
			print "Placed order for depositID: " + depositID + " poloniex order number: " + str(orderNum)
			processingDeposits.set(depositID, str(orderNum))
			processingTrades.set(str(orderNum), depositID)
			return True
		else:
			print("Unable to place poloniex order for: " + str(deposit) + " order info: " + str(order))
			return False
	else:
		print "Already processed deposit: " + depositID

#Send a user bitcoins minus commision
def sendUserBTC(tradeAmount, btcAddr):

	#Take off commision from actual trade amount
	profit = float(tradeAmount) * COMMISION
	usersAmount = float(tradeAmount) - profit

	#TODO add additional safety check to make sure I have enough bitcoins to transfer just in case

	response = poloniexAcc.withdraw("BTC", usersAmount, btcAddr)

	#TODO add additional check on response
	if response and "error" not in response:
		print "Successfully transfered " + str(usersAmount) + " bitcoins to: " + btcAddr
		print "Actual trade amount: " + str(tradeAmount) + " profit: " + str(profit)
	else:
		#This might be important to log in a different file. As failed bitcoin transfers
		print "Could not transfer " + str(usersAmount) + " bitcoins to: " + btcAddr 
		if "error" in response:
			print response["error"]



#TODO create another thread to monitor processing trades
#If any orders are still processing then check their status
#If finished forward to corresponding address
def checkProcessingOrders():

	#print "Checking processing orders"
	
	tradeHistory = poloniexAcc.returnTradeHistory("BTC_ETH")
	
	for trades in tradeHistory:

		orderNum = trades["orderNumber"]
		fee = trades["fee"] #fees in btc
		amount = trades["amount"] #amount in btc

		#Only look at trades that are still proceessing
		if str(orderNum) in processingTrades.db:
			depositID = processingTrades.get(str(orderNum))
			print "Order number finished: " + orderNum + " depositID: " + depositID
			processingTrades.rem(str(orderNum))
			processingDeposits.rem(depositID)
			#TODO set value to something useful. 
			processedDeposits.set(depositID, str(orderNum))

			#Send user converted bitcoins
			userAddress = "TODO" #TODO
			sendUserBTC(amount, userAddress)


#Generate a "unique" id by using a timestamp and amount
#Note probably not actually unique
def generateDepositID(deposit):
	return "timestamp:" + str(deposit["timestamp"]) + " amount:" + deposit["amount"]

while True:

	#TODO could use a timed wait until depositHistory != previousHistory to 
	#avoid unneeded work but have checkProcessingOrders() on another thread
	
	#Get withdrawel and deposit history up to current time
	currTime = str(time.time())
	#TODO consider setting start time to a month ago or something like that
	depositHistory = poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime})["deposits"]
	
	#For deposits not already
	for deposit in depositHistory:
		depositId = generateDepositID(deposit)
		#Some deposits are pending or whateves ignore them
		if deposit["status"] == "COMPLETE" and deposit["currency"] == "ETH":
			if not processingDeposits.get(depositId) and not processedDeposits.get(depositId):
				processDeposit(deposit)

	checkProcessingOrders()
	prevDepositHistory = depositHistory
	time.sleep(1)