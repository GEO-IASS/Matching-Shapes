(function init() {
  var currentEL = $('.players-text');
  var scoresEL = $('.score-value');
  var scoresDiv = $('table');
  var scoresText = $('.score-text');
  var credits = $('.credits-text');
  credits.hide();
  var timerTime = 60;
  var currentTime = 0;
  var stopTimerBool = false;
  var type = '';
  var gotWinner = false;
  var playerNames = ["Player 1","Player 2"];
  var ip = '128.237.202.46';
  window.setInterval(function(){ 
	  $.get('http://'+ip+':5000/getCompleteCount', function(path) {
	  		myObject = JSON.parse(path);
	  		completeCount = myObject['completed'].toString();
	  		completeCounts = completeCount.split(",");
	  		if(completeCount == "") {
	  			completeCounts = [];
	  		}
	  		str = '';
	  		for(var i = 0 ; i < completeCounts.length ; i++) {
	  			str = str + '<th>' + completeCounts.toString(); + "</th>";
	  			if(i != completeCounts.length) {
	  				str += '<th></th>';
	  			}
	  		}
	  		scoresEL.html(str);
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 200);

  window.setInterval(function(){ 
	  $.get('http://'+ip+':5000/getWinner', function(path) {
	  		myObject = JSON.parse(path);
	  		var winner = parseInt(myObject['winner']);
	  		if(playerNames.length >= winner) {
		  		var winnerName = playerNames[winner-1];
		  		if(winner > 0) {
		  			gotWinner = true;
		  			credits.show();
		  			scoresEL.hide();
				  	scoresDiv.hide();
				  	scoresText.hide();
		  			var str = '<h1><b>' + winnerName.toString() + ' Wins! </b></h1>';
			  		currentEL.html(str);
			  		currentEL.css({
					    fontSize: 30
					});
		  		}
		  	}
	    })
	    .fail(function() {
	      console.log('Sorry failed to load an image.');
	    });
  }, 500);

})();