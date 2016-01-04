  
//Globalize variables
//var Tx = require('ethereumjs-tx');
var keythereum = require("keythereum");

BigNumber = require("browserify-bignum");

ethUtil = require("ethereumjs-util");
Buffer = require('buffer').Buffer;
// //Our ether wallet
// const ETH_WALLET = ""

// function transferEth(encryptedWallet, walletPasswd){
	// var keyobject = JSON.parse(encryptedWallet);

	// //TODO check for failure
	// var privkey = keythereum.recover(walletPasswd, keyobject);

	// var rawTx = {
	//   to: '0x0000000000000000000000000000000000000000', 
	//   value: ETH_WALLET, 
	// };

	// var tx = new Tx(rawTx);
	// tx.sign(privkey);

	// var serializedTx = tx.serialize();

// };
