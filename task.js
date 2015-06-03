

function validateAnswers() {
	var visibleTopic = $("li.topic:visible"); 
	var shortAnswer = $(visibleTopic).find("input.short").val();
	var longAnswer = $(visibleTopic).find("input.long").val();
	var confAnswer = $(visibleTopic).find("input[name='confidence']:checked").val();
	if(shortAnswer=="" || longAnswer=="" || typeof confAnswer == "undefined") {
		$("li.topic:visible").find(".errorMessage").text("You can proceed after answering every question.");
		return false;
	}  else {
		confidence.push(confAnswer);
		return true;
	}
}

function submitAnswers() {
	var timeSpentForAnswers = [];
	for(var i=1;i<timeStamp.length;i++) {
		timeSpentForAnswers.push((timeStamp[i]-timeStamp[i-1])/1000);
	}
	var answers = $.map($("li.topic"), function(topicEl,i) {
		var topicIndex = $(topicEl).attr('topicIndex');
		var shortAns = $(topicEl).find("input.short").val();
		var longAns = $(topicEl).find("input.long").val();
		var mode = $(".topic_representation").attr("mode");
		var confAnswer = confidence[i]; 
		return {"topicIndex":topicIndex, "mode":mode, "short":shortAns, 
				"long":longAns, "conf":confAnswer, "duration":timeSpentForAnswers[i]};
	});
	var answersJSON = JSON.stringify(answers);
	var timeJSON = JSON.stringify(timeStamp);

	$.post("submit", {
		mode: $("div.topic_representation").attr("mode"),
		randomImage_idx: $("div.topic_representation").attr("randomImage_idx"),
		wordNum: $("div.topic_representation").attr("wordNum"),
		answers: answersJSON,
		timestamp: timeJSON
	}, function(data) {
		// display returned code and message
		$("body").empty();
		$(data).appendTo("body");
	});

	// window.location = "/submit?mode="+$("div.topic_representation").attr("mode")+
	// 		"&answers="+answersJSON+
	// 		"&timestamp="+timeJSON;
}

$(document).ready(function() {
	// initialization
	confidence = [];
	timeStamp = [];

	$(".topic_representation").hide();
	$("li.topic").hide();		$("li.ending").hide();
	$("li.topic[questionnumber='1']").show();

	// if($(".topic_representation").attr("mode")=="wordcloud") {
	// 	generateWordCloud();
	// }

	$("button.start_button").click(function() {
		$(".topic_representation").show();
		$(".introduction").hide();
		timeStamp.push(new Date());
	});
	$("button.finish").click(function(event) {
		// submit and show the last message
		if(!validateAnswers()) {
			$(event.target).prop('disabled', false);
			return;
		}
		timeStamp.push(new Date());
		// $("li.topic").hide();
		// $("li.ending").show();
		submitAnswers();
	
	});
	$("button.next").click(function(event) {
		// show next question
		var qN = parseInt($(event.target).attr("questionnumber"));
		// proceed to next question
		if(!validateAnswers()) return;
		timeStamp.push(new Date());
		$("li.topic").hide();
		$("li.topic[questionnumber='"+(qN+1)+"']").show();
		
	});

});