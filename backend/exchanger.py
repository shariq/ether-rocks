from poloniex import poloniex
from sets import Set
from enum import Enum
import time, pickledb, threading, json

#TODO consider deletion
class ProcessingStatus(Enum):
	processing = 1
	failed = 2
	passed = 3

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

processedDeposits = pickledb.load('processedDeposits.db', False)
forever(processedDeposits.dump)

# deposit address 
processingDeposits = pickledb.load('processingDeposits.db', False)
forever(processingDeposits.dump)

apiKey = "FB8EJWXG-L75UYGW7-E6U482VD-N5R87R0C"
secret = "3f709d585cf4c64ac4544e74b8d78d616119e2e522783bfe8460468c7db2208d54d1560df6e16e3a960dd52283331790672670826add166d06d45a640c3ff957"
poloniexAcc = poloniex(apiKey, secret)




prehistory = {}

#TODO ask shariq did you say to only process 1 deposit at a time?
def processDeposit(deposit):
	rate = 10000000 #TODO change (get normal market rate or slightly below?)

	ethAmount = deposit["amount"]

	coinsToBuy = 1
	orderNum = poloniexAcc.sell("ETH_BTC", rate, coinsToBuy)
	
	#Safety: Checking if I have enough ether to sell
	#If this under then there is an error
	balances = poloniexAcc.returnBalances()
	ethBalance = balances["ETH"]
	if(ethBalance < ethAmount):
		raise error("Error: trying to sell more ether then we have this state should never be reached")

	if orderNum:
		processingDeposits.set(generateDepositID(deposit), ProcessingStatus.processing)
		return True
	else:
		print("Unable to sell order for some reason: " + deposit)
		return False
	#TODO create another thread to monitor processing threads

#If any orders are still processing then check their status
#If finished forward to corresponding address
def checkProcessingOrders():
	tradeHistory = poloniexAcc.returnTradeHistory("ETH_BTC")
	for trades in tradeHistory:
		done = False #TODO see if trade is finished
		if done:
			processingDeposits.remove(generateDepositID(deposit))
			processedDeposits.set(generateDepositID(deposit), True)

#Generate a "unique" id by using a timestamp and amount
#Note probably not actually unique
def generateDepositID(deposit):
	return "timestamp:" + str(deposit["timestamp"]) + " amount:" + deposit["amount"]

while True:

	#TODO use a timed wait until depositHistory != previousHistory to avoid unneeded work

	#Get withdrawel and deposit history up to current time
	currTime = str(time.time())
	#TODO consider setting start time to a month ago or something like that
	depositHistory = poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime})["deposits"]
	
	#For deposits not already
	for deposit in depositHistory:
		depositId = generateDepositID(deposit)
		#Some deposits are pending or whateves ignore them
		if deposit["status"] == "COMPLETE" and deposit["currency"] == "ETH":
			if not processingDeposits.get(generateDepositID(deposit)):
				processDeposit(deposit)

	checkProcessingOrders()
	prehistory = history
	sleep(1)