var wallet_token = '';

function base58_decode(string) {
  var table = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  var table_rev = new Array();
  var i;
  for (i = 0; i < 58; i++) {
    table_rev[table[i]] = int2bigInt(i, 8, 0);
  } 
  var l = string.length;
  var long_value = int2bigInt(0, 1, 0);  
  var num_58 = int2bigInt(58, 8, 0);
  var c;
  for(i = 0; i < l; i++) {
    c = string[l - i - 1];
    long_value = add(long_value, mult(table_rev[c], pow(num_58, i)));
  }
  var hex = bigInt2str(long_value, 16);  
  var str = hex2a(hex);  
  var nPad;
  for (nPad = 0; string[nPad] == table[0]; nPad++);  
  var output = str;
  if (nPad > 0) output = repeat("\0", nPad) + str;
  return output;
}

function hex2a(hex) {
  var str = '';
  for (var i = 0; i < hex.length; i += 2)
    str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
  return str;
}

function a2hex(str) {
  var aHex = "0123456789abcdef";
  var l = str.length;
  var nBuf;
  var strBuf;
  var strOut = "";
  for (var i = 0; i < l; i++) {
    nBuf = str.charCodeAt(i);
    strBuf = aHex[Math.floor(nBuf/16)];
    strBuf += aHex[nBuf % 16];
    strOut += strBuf;
  }
  return strOut;
}

function pow(big, exp) {
  if (exp == 0) return int2bigInt(1, 1, 0);
  var i;
  var newbig = big;
  for (i = 1; i < exp; i++) {
    newbig = mult(newbig, big);
  }
  return newbig;
}

function repeat(s, n){
  var a = [];
  while(a.length < n){
    a.push(s);
  }
  return a.join('');
}

$(document).ready(function() {

// initialize ethereum library
web3 = new Web3();
provider = 'https://52.32.15.54:8545';
web3.setProvider(new web3.providers.HttpProvider(provider));

// fill textbox with file
function readSingleFile(e) {
  var file = e.target.files[0];
  if (!file) {
    return;
  }
  var reader = new FileReader();
  reader.onload = function(e) {
    var contents = e.target.result;
    displayContents(contents);
  };
  reader.readAsText(file);
}
function displayContents(contents) {
  var element = document.getElementById('wallet');
  element.innerHTML = contents;
}
document.getElementById('file-input').addEventListener('change', readSingleFile, false);

// bitcoin address verifier
function checkBitcoinAddress(address) {
  var decoded = base58_decode(address);     
  if (decoded.length != 25) return false;
  var cksum = decoded.substr(decoded.length - 4); 
  var rest = decoded.substr(0, decoded.length - 4);  
  var good_cksum = hex2a(sha256_digest(hex2a(sha256_digest(rest)))).substr(0, 4);
  if (cksum != good_cksum) return false;
  return true;
}

// update balance with message and error/great/wait
function updateBalance(message, color_str) {
  var balance_element = document.getElementById('balance');
  balance_element.innerHTML = message;
  balance_element.style.color = color_str;
}

function setStatus() {
  var status_element = document.getElementById('status');
  status_element.href = 'http://52.32.15.54/wallet?id=' + wallet_token;
  status_element.innerHTML = 'Monitor your conversions';
}

function removeStatus() {
  var status_element = document.getElementById('status');
  status_element.href = 'https://52.32.15.54/wallet?id=';
  status_element.innerHTML = '';
}

$('#submit_wallet').submit(function(event) {
  function successfulSubmission(message) {
    wallet_token = message;
    updateBalance('(success!)', 'rgb(30,200,30)');
    setStatus();
  }
  function unsuccessfulSubmission(message) {
    updateBalance(message, 'rgb(200,30,30)');
  }
  
  removeStatus();
  updateBalance('(waiting...)', 'rgb(30,30,200)');
  
  // Outdated comments
  // grabs wallet file and password
  // creates callback1 on an endpoint
  // callback1 returns status and message
  // status is either successful or unsuccessful
  // call corresponding method

  wallet_contents = document.getElementById('wallet').innerHTML;
  wallet_password = document.getElementById('password').innerHTML
  


  return false;
});

$('#submit_conversion').submit(function(event) {
  
  return false;
});

});

