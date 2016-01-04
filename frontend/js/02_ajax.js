var SERVERURL = "https://rpc.myetherwallet.com/api.php";
var KRAKENAPI = "https://api.kraken.com/0/public/";
function getBalance(addr, callback){
    $.post( SERVERURL, { balance: addr }).done(callback);
}
function getTransactionData(addr, callback){
    $.post( SERVERURL, { txdata: addr }).done(callback);
}
function sendRawTx(rawTx, callback){
    $.post( SERVERURL, { rawtx: rawTx }).done(callback);
}
function getEstimatedGas(txobj, callback){
    $.post( SERVERURL, { estimatedGas: txobj }).done(callback);
}
function getEthCall(txobj, callback){
    $.post( SERVERURL, { ethCall: txobj }).done(callback);
}
function getETHvalue(slavePair, callback){
    var prefix = "XETHZ";
    $.post( KRAKENAPI+"Ticker", { pair: prefix+slavePair }).done(function(data){
        callback(data['result'][prefix+slavePair]['o']);
    });
}