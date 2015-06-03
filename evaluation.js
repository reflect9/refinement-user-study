

function validateAnswers() {
	var visibleTopic = $("li.evaluation:visible"); 
	var box_best = $(visibleTopic).find("input[name='quality_best']:checked");
	var box_worst = $(visibleTopic).find("input[name='quality_worst']:checked");
	if(box_best.length != 1 || box_worst.length != 1) {
		$("li.evaluation:visible").find(".errorMessage").text("You can proceed after choosing the best and worst labels.");
		return false;
	} else {
		var kn_best = $.makeArray($(box_best).parent().parent().find("p.desc_data").map(function() {
			return $(this).attr("keyname"); 
		}));
		var kn_worst = $.makeArray($(box_worst).parent().parent().find("p.desc_data").map(function() {
			return $(this).attr("keyname"); 
		}));
		var algorithm_label = $(visibleTopic).find("p.desc_data[keyname='algorithm']");
		var bad_random_label = $(visibleTopic).find("p.desc_data[keyname*='bad']");
		if ($(visibleTopic).attr("memo")=="dummy") {
			var memo="dummy"
		} else {
			//var memo = (algorithm_label.length>0)?$(algorithm_label).attr("keyname"):"" 
			//+ "," + (bad_random_label.length>0)?$(bad_random_label).attr("keyname"):"" 	
			var memo = "real"
		}
		evalResults.push({
			"eID":$(visibleTopic).attr("eID"),
			"topicIdx":$(visibleTopic).attr("topicIndex"),
			"wordNum":$(visibleTopic).attr("wordNum"),
			"shortOrLong":$(visibleTopic).attr("shortOrLong"),
			"best":kn_best, 
			"worst":kn_worst, 
			"duration":((new Date()-timestamp)/1000),
			"memo": memo
		});
		timestamp = new Date();
		return true;
	}
}


function submitAnswers() {
	$.post("evaluationSubmit", {
		evalResults: JSON.stringify(evalResults),
	}, function(data) {
		$("body").empty();
		$(data).appendTo("body");
	}).fail(function() {
		alert("submission failed");
	});

	
}

$(document).ready(function() {
	// initialization
	evalResults = [];
	$(".evaluation_container").hide();
	$("li.evaluation").hide();		$("li.ending").hide();
	$("li.evaluation[questionnumber='1']").show();

	// RADIO BUTTON BEHAVIOR OF EXCLUSIVE SELECTION OF BEST OR WORST FOR ONE LABEL
	$("input[name='quality_best']").click(function() {
		$(this).parent().parent().find("input[name='quality_worst']").prop('checked',false);
		$(this).parent().parent().parent().find("input[name='quality_best']").prop('checked',false);
		$(this).prop('checked',true);
	});
	$("input[name='quality_worst']").click(function() {
		$(this).parent().parent().find("input[name='quality_best']").prop('checked',false);
		$(this).parent().parent().parent().find("input[name='quality_worst']").prop('checked',false);
		$(this).prop('checked',true);
	});


	// TOGGLE FULLTEXT WHEN CLICKED
	$("li.document_li").click(function() {
		$(this).find(".doc_fulltext").toggle();
		$(this).find(".show_more").toggle();
	});

	$("button.start_button").click(function() {
		$(".evaluation_container").show();
		$(".introduction").hide();
		timestamp = new Date();

	});
	$("button.finish").click(function(event) {
		// submit and show the last message
		if(!validateAnswers()) {
		$(event.target).prop('disabled', false);
			return;
		}
		submitAnswers();
	});
	$("button.next").click(function(event) {
		// show next question
		var qN = parseInt($(event.target).attr("questionNumber"));
		// proceed to next question
		if(!validateAnswers()) return;
		$("li.evaluation").hide();
		$("li.evaluation[questionNumber='"+(qN+1)+"']").show();
		$("html, body").animate({ scrollTop: 0 }, "slow");
		
	});

});