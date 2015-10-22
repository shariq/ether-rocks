=====
Web Interface
=====
Hosted statically; purely client side javascript.

Part 0:
- Description and explanation of website
- Which exchange rate we use (the latest one from Poloniex)
- How much it will cost you (1% commission plus fixed cost of smart contract and Poloniex)
- Why you can trust us (our smart contract's database is public record and it's in our incentive to preserve reputation)
- If you're worried, convert a small amount at a time

Part 1:
- Text area for wallet
- Password input for your wallet's password

Part 2:
- Your current balance
- How much you would like to convert to Bitcoin
- Which Bitcoin address you'd like to cash out to

Part 3: (tentative)
- All the current records within the smart contract's database

=====
Smart Contract
=====
Public record

- Takes in ETH amount and BTC address
- Stores it in database
- Forwards all the ETH to the forward address

=====
Backend
=====
Responsible for conversion and sending BTC to user

- Monitors the forward address for new ETH from the smart contract
- Forward the ETH to Poloniex

- Sell the ETH on Poloniex for BTC
- Withdraw the BTC from Poloniex to our BTC address
- Forward 99% of what we received to the user's BTC address
