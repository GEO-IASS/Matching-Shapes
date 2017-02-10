var express = require('express');
var bodyParser = require('body-parser');

var app = express();

var maxPlayers = 2;

var players = [];
var winner = 0;

var foundWinner = false;

app.set('port', (process.env.PORT || 5000));

app.use(bodyParser.json());
app.use(express.static(__dirname + '/public'));

// views is directory for all template files
app.set('views', __dirname + '/views');
app.set('view engine', 'ejs');

app.get('/', function(request, response) {
  response.send('Hello world');
});

app.get('/getPlayers', function(request, response) {
	var obj = {
  	'players':players.toString()
	};
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  response.send(JSON.stringify(obj));
});

app.post('/startGame', function(req, res){
	players = [];
	winner = 0;
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(req.body);
});

app.post('/connectToGame', function(req, res){
	players.push(req.body.playername);

	console.log(req.body.playername);
	var playerNum = players.length;
	var tosend = '{"playerNum":"' + playerNum.toString() + '"}';
	var obj = {
  	'playerNum': playerNum.toString()
  	};
	if(players.length == maxPlayers) {
		currentPlayer = 1;
	}
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(JSON.stringify(obj));
});

app.post('/iAmDone', function(req, res){
	var playerNum = req.body.playernum;
	if(!foundWinner && winner == 0) {
		foundWinner = true;
		winner = playerNum;
	}
	var obj = {
  		'winner': winner.toString()
  	};
	res.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
	res.send(JSON.stringify(obj));
});

app.get('/getWinner', function(request, response) {
  var obj = {
  	'winner': winner.toString(),
	};
	response.setHeader('Access-Control-Allow-Origin', 'http://localhost:8000');
  	response.send(JSON.stringify(obj));
});

app.listen(app.get('port'), function() {
  console.log('Node app is running on port', app.get('port'));
});