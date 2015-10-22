from poloniex import poloniex
apiKey = "FB8EJWXG-L75UYGW7-E6U482VD-N5R87R0C"
secret = "3f709d585cf4c64ac4544e74b8d78d616119e2e522783bfe8460468c7db2208d54d1560df6e16e3a960dd52283331790672670826add166d06d45a640c3ff957"
poloniexAcc = poloniex(apiKey, secret)

balances = poloniexAcc.returnCompleteBalances()

#Get withdrawel and deposit history up to current time
currTime = str(time.time())
history =  poloniexAcc.returnDepositsWithdrawals({"start": 0, "end": currTime)})

