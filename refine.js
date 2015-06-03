
function showDocuments(topicIdx) {
	$.get("relatedDocuments", {
		topicIdx: topicIdx
	}, function(documentData) {
		// update ul.document_list with documentData
		$("ul.document_list").empty();
		docs = JSON.parse(documentData);
		_.each(docs, function(doc,i) {
			var lastSpaceIdx = doc.fulltext.substring(0,230).search(/ [^ ]*$/);
			var trimmedFulltext = doc.fulltext.substring(0,lastSpaceIdx);
			var prob = (i==0) ? "("+Math.floor(doc.prob*100)+"% matching)" : "("+Math.floor(doc.prob*100)+"%)";
			$("<li>\
				<div class='idx'>"+topicIdx+ALPHABET[i]+"</div>\
				<div class='title'>"+doc.title+"<span class='prob'>"+prob+"</span></div>\
				<div class='fulltext'>"+trimmedFulltext+"...</div>\
			</li>").appendTo("ul.document_list");
		});
		$(".document_container").find(".tidx").text(topicIdx);
		$("li.topic").removeClass("selected");
		$("li.topic[tid='"+topicIdx+"']").addClass("selected");
	});
}

function makeid() {
	var text = ""; 	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	for (var i = 0; i < 5; i++) text += possible.charAt(Math.floor(Math.random() * possible.length));
	return text;
}

// function showPreview(data) {
// 	if(data['ref_type']=="split-topic") {
// 		var targetTopicEl = $("li.topic[tid='"+data.topicNum+"']");
// 		if (targetTopicEl.length!=1) { return; }
// 		var html = "<div class='preview' rid='"+data['rid']+"'>\
// 			<label>Split this topic into two.</label>\
// 			<div class='splitted_topic topic1'></div>\
// 			<div class='splitted_topic topic2'></div>\
// 		</div>";
// 		_.each(data['words1'], function(w) {
// 			$(html).find(".topic1").append("<span>"+w+"</span>");
// 		});	
// 		_.each(data['words2'], function(w) {
// 			$(html).find(".topic2").append("<span>"+w+"</span>");
// 		});	
// 		$(targetTopicEl).append(html);
// 	} else if(data['ref_type']=="merge-topic") {
		
// 	} else if(data['ref_type']=="overarching-word") {
		
// 	} else if(data['ref_type']=="add-stop-words") {
		
// 	} else if(data['ref_type']=="custom-refinement") {
		
// 	} else {}
// }

// function renderAllPreview() {
// 	$('.preview').remove();
// 	_.each(refPhase2, function(ref){
// 		showPreview(ref);
// 	});
// }

function submitReport() {
	var result = {
		'openingPhase1': openingPhase1,
		'closingPhase1': closingPhase1,
		'openingPhase2': openingPhase2,
		'closingPhase2': closingPhase2,
		'refPhase1' : refPhase1,
		'refPhase2' : refPhase2
	};
	result['dump'] = JSON.stringify(result);
	$.post("submitReport", result, function(data){
		// returned feedback
		clearInterval(int_clock2);
		$(".clock").text(data);
		//window.location.href = 'questionnaire';
	});
}


function resetTemplate(templateEl) {
	var ref_type = $(templateEl).attr("type");
	// GENERAL RESETTING
	$(templateEl).find("input").val(""); 	// clear up the values
	$(templateEl).find("textarea").val("");
	// TYPE SPECIFIC RESETTING
	if(ref_type=="split-topic") {
		$(templateEl).find(".wordBucket").empty();
	} else if(ref_type=="merge-topic") {
	} else if(ref_type=="add-words-to-topic") {
	} else if(ref_type=="remove-words-from-topic") {
		$(templateEl).find(".wordBucket").empty();
	} else if(ref_type=="overarching-word") {
	} else if(ref_type=="add-stop-words") {
	} else if(ref_type=="move-documents") {
	} else if(ref_type=="remove-documents") {
	} else if(ref_type=="custom-refinement") {
	} else {}
}


function extractRefinementPlan(templateEl) {
	var ref_type = $(templateEl).attr("type");
	if(ref_type=="split-topic") {
		var data = { 
			'rid': makeid(),
			'ref_type':"split-topic",
			'topicNum':$(templateEl).find("input.topicNum").val(),
			'words1':$.map( $(templateEl).find(".wordBucket[bucketNum='1']").find("li"), function(li) { return $(li).text(); }),
			'words2' :$.map( $(templateEl).find(".wordBucket[bucketNum='2']").find("li"), function(li) { return $(li).text(); }),
		};
		data['desc'] = "Split Topic "+data['topicNum']+" into two topics";
	} else if(ref_type=="merge-topic") {
		var data = { 
			'rid': makeid(),
			'ref_type':"merge-topic",
			'topicNum1': $(templateEl).find("input.topic1").val(),
			'topicNum2': $(templateEl).find("input.topic2").val()
		};
		data['desc'] = "Merge Topic <span class='color1 editable' contentEditable='true'>"+data['topicNum1']+"</span> and <span class='color2 editable' contentEditable='true'>"+ data['topicNum2']+"</span>";
	} else if(ref_type=="add-words-to-topic") {
		var data = { 
			'rid': makeid(),
			'ref_type':"add-words-to-topic",
			'topicNum':$(templateEl).find("input.topicNum").val(),
			'words_to_add': $(templateEl).find("textarea.full-col-text").val().replace(/[,\s]\s*/g,',').split(",")
		};
		data['desc'] = "Add <span class='color1 editable' contentEditable='true'>"
			+data['words_to_add'].join(", ")
			+"</span> to Topic <span class='color2 editable' contentEditable='true'>"
			+ data['topicNum']+"</span>";
	} else if(ref_type=="remove-words-from-topic") {
		var data = { 
			'rid': makeid(),
			'ref_type':"remove-words-from-topic",
			'topicNum':$(templateEl).find("input.topicNum").val(),
			'words_to_remove': $.map( $(templateEl).find(".wordBucket").find("li.crossed"), function(li) { return $(li).text(); }),
		};
		data['desc'] = "Remove <span class='color1 editable' contentEditable='true'>"
			+data['words_to_remove'].join(", ")
			+"</span> from Topic <span class='color2 editable' contentEditable='true'>"
			+ data['topicNum']+"</span>";
	} else if(ref_type=="overarching-word") {
		var data = { 
			'rid': makeid(),
			'ref_type':"overarching-word",
			'overarching_word': $(templateEl).find("input.singleWord").val(),
			'words_to_be_merged': $(templateEl).find("textarea.full-col-text").val().replace(/[,\s]\s*/g,',').split(",")
		};
		data['desc'] = "Make an overarching word" +
			"<span class='color1 editable' contentEditable='true'>"+data['overarching_word']
			+"</span> that merges <span class='color2 editable' contentEditable='true'>"
			+data['words_to_be_merged'].join(", ")+"</span>";
	} else if(ref_type=="add-stop-words") {
		var data = { 
			'rid': makeid(),
			'ref_type':"add-stop-words",
			'stop_words': $(templateEl).find("textarea.full-col-text").val().replace(/[,\s]\s*/g,',').split(",")
		};
		data['desc'] = "Ignore <span class='color1 editable' contentEditable='true'>"+data['stop_words']+"</span>";
	} else if(ref_type=="move-documents") {
		var data = { 
			'rid': makeid(),
			'ref_type':"move-documents",
			'topicNum': $(templateEl).find("input.topicNum").val(),
			'documents_to_move': $(templateEl).find("textarea.full-col-text").val().replace(/[,\s]\s*/g,',').split(",")
		};
		data['desc'] = "Move documents <span class='color1'>"+data['documents_to_move']+"</span>"+
			" to Topic <span class='color1'>"+data['topicNum']+"</span>";
	} else if(ref_type=="remove-documents") {
		var data = { 
			'rid': makeid(),
			'ref_type':"remove-documents",
			'topicNum': $(templateEl).find("input.topicNum").val(),
			'documents_to_remove': $(templateEl).find("textarea.full-col-text").val().replace(/[,\s]\s*/g,',').split(",")
		};
		data['desc'] = "Remove documents <span class='color1'>"+data['documents_to_remove']+"</span>"+
			" from Topic <span class='color1'>"+data['topicNum']+"</span>";
	} else if(ref_type=="custom-refinement") {
		var data = {
			'rid': makeid(),
			'ref_type':"custom-refinement",
			'description' : $(templateEl).find("textarea.full-col-text").val()
		};
		data['desc'] = data['description'];
	} else {}
	data['timestamp'] = new Date().getTime();
	return data;
}

function renderRefinement(data, animate) {
	var html = $("<li class='ref_plan' rid='"+data['rid']+"'>\
		<img class='remove' src='images/icon-x-white.png'>\
		<label class='ref_description'>"+data['desc']+"</label>\
	</li>");
	var detail_el = $("<div class='ref_plan_detail'></div>");
	/////////////////////////////////////////////
	/////////////////////////////////////////////
	if(data['ref_type']=="split-topic") {
		$(detail_el).append("<div class='detail_part'>Group 1</div>");
		var part_el = $("<ul></ul>").appendTo(detail_el);
		_.each(data['words1'], function(w) {
			$(part_el).append("<li>"+w+"</li>");
		});	
		$(detail_el).append("<div class='detail_part'>Group 2</div>");
		var part_el = $("<ul></ul>").appendTo(detail_el);
		_.each(data['words2'], function(w) {
			$(part_el).append("<li>"+w+"</li>");
		});	
		$(detail_el).appendTo(html);
		/////////////////////////////////////////////
		/////////////////////////////////////////////
	} else if(data['ref_type']=="merge-topic") {
		$(detail_el).append("<div class='detail_part'>Preview of merged topic</div>");
		var part_el = $("<ul></ul>").appendTo(detail_el);
		var terms_to_merge = $("li.topic[tid='"+data.topicNum1+"']").find("ul.topic_terms > li > div.term");
		$.each(terms_to_merge, function(i,t) {
			var newFontSize = parseFloat($(t).css('font-size'))/1.1;
			$("<li style='font-size:"+newFontSize+"px' size="+newFontSize+">"+$(t).text()+"</li>")
			.addClass("color1")
			.appendTo(part_el);
		});
		var terms_to_merge = $("li.topic[tid='"+data.topicNum2+"']").find("ul.topic_terms > li > div.term");
		$.each(terms_to_merge, function(i,t) {
			var newFontSize = parseFloat($(t).css('font-size'))/1.1;
			$("<li style='font-size:"+newFontSize+"px' size="+newFontSize+">"+$(t).text()+"</li>")
			.addClass("color2")
			.appendTo(part_el);
		});
		$(part_el).find("li").sort(function(a,b) {
			var afs = parseFloat($(a).attr("size"));
			var bfs = parseFloat($(b).attr("size"));
			var result = (afs > bfs)? -1 : (afs<bfs)?1 : 0;
			return result;
		}).appendTo(part_el);
		$(detail_el).appendTo(html);
		/////////////////////////////////////////////
		/////////////////////////////////////////////
	} else if(data['ref_type']=="add-words-to-topic") {
		$(detail_el).append("<div class='detail_part'>Preview of the topic</div>");
		var part_el = $("<ul></ul>").appendTo(detail_el);
		var original_terms = $("li.topic[tid='"+data.topicNum+"']").find("ul.topic_terms > li > div.term");
		$.each(original_terms, function(i,t) {
			var newFontSize = parseFloat($(t).css('font-size'))/1.1;
			$("<li style='font-size:"+newFontSize+"px' size="+newFontSize+">"+$(t).text()+"</li>")
			.addClass("color2")
			.appendTo(part_el);
		});
		$.each(data['words_to_add'], function(i,t) {
			var newFontSize = 13;
			$("<li style='font-size:"+newFontSize+"px' size="+newFontSize+">"+t+"</li>")
			.addClass("color1")
			.appendTo(part_el);
		});
		$(detail_el).appendTo(html);
	} else if(data['ref_type']=="remove-words-from-topic") {
		$(detail_el).append("<div class='detail_part'>Preview of the topic after removal</div>");
		var part_el = $("<ul></ul>").appendTo(detail_el);
		var original_terms = $("li.topic[tid='"+data.topicNum+"']").find("ul.topic_terms > li > div.term");
		$.each(original_terms, function(i,t) {
			var newFontSize = 13;
			var el = $("<li style='font-size:"+newFontSize+"px' size="+newFontSize+">"+$(t).text()+"</li>");
			if (data['words_to_remove'].indexOf($(t).text())!=-1) {
				$(el).addClass('crossed');
			}
			$(el).appendTo(part_el);
		});
		$(detail_el).appendTo(html);
		/////////////////////////////////////////////
		/////////////////////////////////////////////
	} else if(data['ref_type']=="overarching-word") {
		$(detail_el).append("<div class='detail_part'>Words converted to '"+data['overarching_word']+"'</div>");
		$("li.topic").each(function(i) {
			var terms = $(this).find("div.term").map(function(j) { return $(this).text(); });
			var terms_to_be_merged = _.filter(terms, function(t) { return data['words_to_be_merged'].indexOf(t)!=-1;});
			if(terms_to_be_merged.length==0) return;
			else {
				var part_el = $("<ul></ul>").appendTo(detail_el);
				$(part_el).append($("<span class='heading'>Topic "+i+"</span>"));
				_.each(terms_to_be_merged, function(t) {   $(part_el).append("<li>"+t+"</li>")});
			}
		});
		$(detail_el).appendTo(html);
	} else if(data['ref_type']=="add-stop-words") {
		$(detail_el).append("<div class='detail_part'>Removed words</div>");
		$("li.topic").each(function(i) {
			var terms = $(this).find("div.term").map(function(j) { return $(this).text(); });
			var terms_to_be_removed = _.filter(terms, function(t) { return data['stop_words'].indexOf(t)!=-1;});
			if(terms_to_be_removed.length==0) return;
			else {
				var part_el = $("<ul></ul>").appendTo(detail_el);
				$(part_el).append($("<span class='heading'>Topic "+(i+1)+"</span>"));
				_.each(terms_to_be_removed, function(t) {   $(part_el).append("<li>"+t+"</li>")});
			}
		});
		$(detail_el).appendTo(html);
		
	} else if(data['ref_type']=="move-documents") {
		
	} else if(data['ref_type']=="remove-documents") {
		
	} else if(data['ref_type']=="custom-refinement") {
		
	} else {}
	
	if (animate==true) {
		$(html).addClass('hidden').prependTo($('ul.ref_list'));	
		$(html).show('slow');
	} else {
		$(html).prependTo($('ul.ref_list'));
	}
}

function renderAllRefinement(animateLastOne) {
	$('ul.ref_list').empty();
	_.each(refPhase2, function(ref, i, list){
		if (animateLastOne==true && i==list.length-1) {
			renderRefinement(ref, true);
		} else {
			renderRefinement(ref);	
		}
	});
}

function renderOpenRefinement(animateLastOne) {
	$("ul.open_ref_list").empty();
	_.each(refPhase1, function(ref, i, list) {
		var html = $("<li class='ref_plan' rid='"+ref['rid']+"'>\
			<img class='remove' src='images/icon-x-white.png'>\
			<label class='ref_description'>"+ref['desc']+"</label>\
		</li>");
		if (animateLastOne==true && i==list.length-1) {
			$(html).addClass('hidden').prependTo($('ul.open_ref_list'));
			$(html).show('slow');
		} else {
			$(html).prependTo($('ul.open_ref_list'));
		}
		
	});
}


function validateAnswers() {
	// var visibleTopic = $("li.topic:visible"); 
	// var shortAnswer = $(visibleTopic).find("input.short").val();
	// var longAnswer = $(visibleTopic).find("input.long").val();
	// var confAnswer = $(visibleTopic).find("input[name='confidence']:checked").val();
	// if(shortAnswer=="" || longAnswer=="" || typeof confAnswer == "undefined") {
	// 	$("li.topic:visible").find(".errorMessage").text("You can proceed after answering every question.");
	// 	return false;
	// }  else {
	// 	confidence.push(confAnswer);
	// 	return true;
	// }
}

function splitTopicSupport() {
	// INIT 1st and 2nd word groups when topicNum is updated
	var template = $("div.template[type='split-topic']");
	$(template).find("input.topicNum").change(function(event) {
		var topicNum = $(event.target).val();
		var g1 = $(event.target).parents(".ref_instruction").find(".words1");
		var g2 = $(event.target).parents(".ref_instruction").find(".words2");
		g1.empty();		g2.empty();
		var termsEl = $("li.topic[tid='"+topicNum+"']").find("ul.topic_terms > li > div.term");
		$.each(termsEl, function(i,t){ 
			$(g1).append("<li>"+$(t).text()+"</li>");
		});
	});
	// DEFINE CLICK EVENT HANDLER: SWITCH WORD GROUP
	$(template).find(".wordBucket").on("click", "li", function(event) {
		var current_bucket = $(event.target).parents(".wordBucket").attr('bucketNum');
		var target_bucket = (current_bucket=='1') ? "2" : "1";
		var target_bucket_el = $(event.target).parents(".template").find(".wordBucket[bucketNum='"+target_bucket+"']");
		$(target_bucket_el).append(event.target);
	});
}

function removeWordsFromTopicSupport() {
	var template = $("div.template[type='remove-words-from-topic']");
	$(template).find("input.topicNum").change(function(event) {
		var topicNum = $(event.target).val();
		var wordBucket = $(event.target).parents(".ref_instruction").find(".wordBucket");
		$(wordBucket).empty();	
		var termsEl = $("li.topic[tid='"+topicNum+"']").find("ul.topic_terms > li > div.term");
		$.each(termsEl, function(i,t){ 
			$(wordBucket).append("<li>"+$(t).text()+"</li>");
		});
	});
	// DEFINE CLICK EVENT HANDLER: SWITCH WORD GROUP
	$(template).find(".wordBucket").on("click", "li", function(event) {
		$(event.target).toggleClass("crossed");
	});
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
		var mode = $(".main_container").attr("mode");
		var confAnswer = confidence[i]; 
		return {"topicIndex":topicIndex, "mode":mode, "short":shortAns, 
				"long":longAns, "conf":confAnswer, "duration":timeSpentForAnswers[i]};
	});
	var answersJSON = JSON.stringify(answers);
	var timeJSON = JSON.stringify(timeStamp);

	$.post("submit", {
		mode: $("div.main_container").attr("mode"),
		randomImage_idx: $("div.main_container").attr("randomImage_idx"),
		wordNum: $("div.main_container").attr("wordNum"),
		answers: answersJSON,
		timestamp: timeJSON
	}, function(data) {
		// display returned code and message
		$("body").empty();
		$(data).appendTo("body");
	});

	// window.location = "/submit?mode="+$("div.main_container").attr("mode")+
	// 		"&answers="+answersJSON+
	// 		"&timestamp="+timeJSON;
}

function updateClock(startTimeStamp, totalMinutes, clockEl) {
	currentTime = new Date();
	var remainingSeconds = (totalMinutes*60) - Math.floor((currentTime-startTimeStamp)/1000);
	var min = Math.floor(remainingSeconds/60);
	var sec = remainingSeconds % 60;
    $(clockEl).text(min + ":" + sec + " remaining until you can finish");
}

$(document).ready(function() {
	ALPHABET = "abcdefghijklmnopqrstuvwxyz";
	refPhase1 = [];
	refPhase2 = [];

	// GENERAL EVENT HANDLER
	//  	SELECTING TOPIC WHEN CLICKED
	$("li.topic").click(function() {
		var topicIdx = $(this).attr('tid');
		showDocuments(parseInt(topicIdx));
	});
	showDocuments(1);


	// PHASE1 : OPEN_ENDED REFINEMENT 
	function startPhase1() {
		$(".bottom_UI > .clock").show();
		$("button.next_stage").show();
		openingPhase1 = new Date().getTime();
		updateClock(openingPhase1, 15, $(".bottom_UI").find(".clock"));
    	int_clock1 = setInterval(function() {updateClock(openingPhase1, 15, $(".bottom_UI").find(".clock"));  }, 1000); 
	}
	$(".open_template > textarea").click(function() {
		if (typeof openingPhase1 == "undefined") startPhase1();
	});
	$("button.add_open_ref").click(function() {
		var new_open_ref = {
			'rid': makeid(),
			'ref_type':"open-refinement",
			'description' : $(".open_template").find("textarea.full-col-text").val(),
			'timestamp': new Date().getTime()
		};
		new_open_ref['desc'] = new_open_ref['description'];
		refPhase1.push(new_open_ref);
		$(".open_template").find("textarea").val("");
		renderOpenRefinement(true);
	});
	$("button.next_stage").click(function() {
		closingPhase1 = new Date().getTime();
		clearInterval(int_clock1);
		$(".open_ref_list").hide();
		$(".ref_list").show();
		$(".open_refinement_tool").hide();
		$(".clock").hide();
		$(".refinement_tool").show();
		$(".open_refinement_tool > div.instruction").hide();
	});


	// PHASE 2 : CREATING refPhase2 WITH TEMPLATES
	// ADD INTERACTIVE SUPPORT TO SPLITTOPIC TEMPLATE
	splitTopicSupport();
	removeWordsFromTopicSupport(); 

	function startPhase2() {
		$(".next_stage").hide();
		$(".finish_phase2").show();
		$(".clock").show();
		openingPhase2 = new Date().getTime();
		updateClock(openingPhase2, 15, $(".bottom_UI").find(".clock"));
    	int_clock2 = setInterval(function() { updateClock(openingPhase2, 15, $(".bottom_UI").find(".clock"));}, 1000); 
	}
	$(".template").click(function() {
		// initialize if this is the first time clicking template
		if (typeof openingPhase2 == "undefined") startPhase2();
		// unfocus all the templates
		$(".template").not(this).find(".ref_instruction").hide('fast');
		$(".template").not(this).find(".ref_title").show('fast');
		// focus on clicked template
		$(this).find(".ref_instruction").show('fast');
		$(this).find(".ref_title").hide('fast');
	});

	$("button.add").click(function() {
		refPhase2.push(extractRefinementPlan($(this).parents(".template")));
		var temp_el = $(this).parents(".template");
		renderAllRefinement(true);
	});
	$("button.reset").click(function() {
		var temp_el = $(this).parents(".template");
		resetTemplate(temp_el);
	});
	// BUTTON FOR REMOVING REFINEMENT PLAN
	$("ul.ref_list").on("click", "img.remove" ,function(event) {
		var rid_to_remove = $(event.target).parents('li.ref_plan').attr("rid");
		refPhase2 = _.filter(refPhase2, function(r) {
			return r['rid']!=rid_to_remove;
		});
		renderAllRefinement();
	});

	$("ul.open_ref_list").on("click", "img.remove" ,function(event) {
		var rid_to_remove = $(event.target).parents('li.ref_plan').attr("rid");
		refPhase1 = _.filter(refPhase1, function(r) {
			return r['rid']!=rid_to_remove;
		});
		renderOpenRefinement();
	});

	$("button.finish_phase2").click(function() {
		closingPhase2 = new Date().getTime();
		submitReport();
	});


// 	$("button.start_button").click(function() {
// 		$(".main_container").show();
// 		$(".introduction").hide();
// 		timeStamp.push(new Date());
// 	});
// 	$("button.finish").click(function(event) {
// 		// submit and show the last message
// 		if(!validateAnswers()) {
// 			$(event.target).prop('disabled', false);
// 			return;
// 		}
// 		timeStamp.push(new Date());
// 		// $("li.topic").hide();
// 		// $("li.ending").show();
// 		submitAnswers();
	
// 	});
// 	$("button.next").click(function(event) {
// 		// show next question
// 		var qN = parseInt($(event.target).attr("questionnumber"));
// 		// proceed to next question
// 		if(!validateAnswers()) return;
// 		timeStamp.push(new Date());
// 		$("li.topic").hide();
// 		$("li.topic[questionnumber='"+(qN+1)+"']").show();
		
// 	});

});