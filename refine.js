
function showDocuments(topicIdx) {
	$.get("relatedDocuments", {
		topicIdx: topicIdx
	}, function(documentData) {
		var kid = $("li.topic[tid='"+topicIdx+"']").attr("kid");  
		$(".document_container").find(".tidx").text(kid);
		$("li.topic").removeClass("selected");
		$("li.topic[tid='"+topicIdx+"']").addClass("selected");
		if($("li.topic.selected").attr("unlocked")=="true") {
			$("ul.document_list").empty().show();
			$(".document_show").hide();
		} else {
			$("ul.document_list").empty().hide();
			$(".document_show").show();
		}
		// update ul.document_list with documentData
		docs_all = JSON.parse(documentData);
		docs = docs_all.slice(0,30);
		// previous_weight=100; 
		current_weight_base = 100;
		_.each(docs, function(doc,i) {
			var title = doc['content']['title'];
			var fulltext = doc['content']['text'];
			var other_topics = doc['other_topics'];
			var lastSpaceIdx = fulltext.substring(0,1500).search(/ [^ ]*$/);
			var trimmedFulltext = fulltext.substring(0,lastSpaceIdx);
			var weight = Math.round(doc['weight']*100);
			// var restText = fulltext.substring(lastSpaceIdx, fulltext.length);
			// var prob = (i==0) ? "("+Math.floor(doc.prob*100)+"% matching)" : "("+Math.floor(doc.prob*100)+"%)";
			while(weight<=current_weight_base) {
				current_weight_base-=10;
				$("<div class='separation'>"+current_weight_base+"-"+(current_weight_base+10)+
					"% association to the theme</div>").appendTo("ul.document_list");
			}

			// if (weight<90) $("<div class='separation'>100-90% association</div>").appendTo("ul.document_list");
			// if (previous_weight>=80 && weight<80) $("<div class='separation'>90-80% association</div>").appendTo("ul.document_list");
			// if (previous_weight>=70 && weight<70) $("<div class='separation'>80-70% association</div>").appendTo("ul.document_list");
			// if (previous_weight>=60 && weight<60) $("<div class='separation'>70-60% association</div>").appendTo("ul.document_list");
			// if (previous_weight>=50 && weight<50) $("<div class='separation'>60-% association</div>").appendTo("ul.document_list");
			// previous_weight = weight;
			var el = $("<li class='document_item' docID='"+(topicIdx+ALPHABET[i])+"'>\
				<div class='title'>"+title+"</div>\
				<div class='keyPhrase'></div>\
				<div class='fulltext'>"+trimmedFulltext+"</div>\
				<div class='relevancyScore'>"+weight+"% associated to this theme.</div>\
				<div class='otherTopics'></div>\
				<div class='fadeCurtain'></div>\
			</li>");
			// RENDERING OTHER ASSOCIATED TOPICS
			var association_values_of_major_themes = weight;
			var topRelatedTopics = _.first(
				_.filter(
					_.sortBy(_.pairs(other_topics), function(tuple) {
						return tuple[1]; 	// SORT ASSOCIATED TOPICS BY THEIR PROBABILITIES
					}), function(tuple) {
					return tuple[1]>0.1 && tuple[0]!=topicIdx-1;	// EXCLUDE TOPICS < 0.1 OR CURRENT TOPIC
				}),3); // GET THE TOP 3 TOPICS
			_.each(topRelatedTopics, function(tuple) {
				var tid = parseInt(tuple[0])+1; // original topic id
				var kid = $("li.topic[tid='"+tid+"']").attr("kid");  
				var topic_words = $("li.topic[tid='"+tid+"']").find("ul.topic_terms").text().replace(/\s+/ig," ").split(" ").slice(0,10).join(" ");
				var relatedTopicEl = $("<div class='relatedTopic'> "+Math.round(tuple[1]*100)+"% associated to Theme "+kid+" ("+topic_words+" ... )</div>");
				$(el).find(".otherTopics").append(relatedTopicEl);	
				association_values_of_major_themes = association_values_of_major_themes + Math.round(tuple[1]*100);
			});
			// ADD THE REMAINING ASSOCIATION VALUE TO OTHER THEMES
			$(el).find(".otherTopics").append("<div class='relatedTopic'>"+(100-association_values_of_major_themes)+"% to other themes.</div>");
			// EXPAND WHEN CLICKED
			$(el).click(function(event) {
				if ($(event.target).hasClass("showmore")) {
					return false;
				}
				$(this).toggleClass("selectedDoc");
				events.push({type:'expand_document',topicIdx:$("li.topic.selected").attr("tid"),kID:$("li.topic.selected").attr("kid"), docId:$(this).attr('docID'), timestamp:new Date().getTime()});
				// $(this).find(".restText").toggleClass('hidden');
				// $(this).find(".restText").click(function() { $(this).hide(); });
			});
			// ADD FULL ARTICLE BUTTON IF THE DOCUMENT IS TOO LONG
			if(fulltext.length>1500) {
				var showmore_el = $("<span class='showmore'>... FULL ARTICLE</span>")
				.click($.proxy(function(event) {
					//console.log(this.fulltext);
					var docID = $(event.target).parents("li.document_item").attr("docID");
					events.push({type:'show_full_article', topicIdx:$("li.topic.selected").attr("tid"),kID:$("li.topic.selected").attr("kid"), docId:docID, timestamp:new Date().getTime()});
					showModal(this);
				},{title:title, content:fulltext}));
				$(el).find(".fulltext").after(showmore_el);	
			}
			$(el).appendTo("ul.document_list");
		});
		$(".document_container").scrollTop(0);
		
		// HIGHLIGHT WORDS IF FOCUSED WORDS ARE NOT EMPTY
		_.each(focusedWords, function(w) {
			$("li.document_item").each(function(i,el) {
				// HIGHLIGHTING TITLE
				// TBD
				// HIGHLIGHTING FULLTEXT
				var fulltext = $(el).find(".fulltext").text();
				var indices = findAllIndicesOfSubstring(fulltext, w);
				var w_reg = new RegExp(w,'ig');
				if(indices.length>0) {
					var ind = indices[0];
					var phraseAroundWord = fulltext.substring(Math.max(0,ind-40), Math.min(fulltext.length,ind+40))
						.replace(/^[a-zA-Z0-9]+\s/i,"").replace(/\s[a-zA-Z0-9]+$/i,""); 
					phraseAroundWord= phraseAroundWord.replace(w_reg, "<span class='keyword'>"+w+"</span>");
					$(el).find(".keyPhrase").html("... "+phraseAroundWord+ " ...");
					$(el).addClass("showingKeyPhrase");
					// ALSO HIGHLIGHT THE WORD IN THE FULLTEXT
					text_with_highlight = fulltext.replace(w_reg, "<span class='keyword'>"+w+"</span>"); 
					$(el).find(".fulltext").html(text_with_highlight);
				} 
			});
		});

	});
}

function makeid() {
	var text = ""; 	var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	for (var i = 0; i < 5; i++) text += possible.charAt(Math.floor(Math.random() * possible.length));
	return text;
}

function showModal(config) {
	$(".modal_title").html(config.title);
	$(".modal_content").html(config.content);
	$(".modal_frame").click(function(event) {
		event.stopPropagation();
	});
	$(".overlay, .modal_close").click(function(event) {
		$(".overlay").hide();
	});
	$(".overlay").show();
	$(".modal_frame").scrollTop(0);
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

function submitLog() {
	var user_id = $("input.user_id").val();
	if(user_id=="") {
		alert("Please provide adequate user name.");
		return;
	}
	var data = {
		'user_id':user_id,
		'events':events
	}
	$.post("submitLog",{
		data:JSON.stringify(data)
	},function(response){
		console.log(response);
		alert(response);
	});
}


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
	// var remainingSeconds = (totalMinutes*60) - Math.floor((currentTime-startTimeStamp)/1000);
	// var min = Math.floor(remainingSeconds/60);
	// var sec = remainingSeconds % 60;
 //    $(clockEl).text(min + ":" + sec + " remaining until you can finish");
 	var elapsedSeconds = Math.floor((currentTime-startTimeStamp)/1000);
 	var min = Math.floor(elapsedSeconds/60);
	var sec = elapsedSeconds % 60;
 	$(clockEl).text(min + ":" + sec);
}

function showWarning(message) {
	$(".warning").text(message);
}

function findAllIndicesOfSubstring(long, short) {
	var reg = new RegExp("[^a-zA-Z]"+short+"[^a-zA-Z]", 'ig');
	var match, matches = [];
	while ((match = reg.exec(long)) != null) {
	  matches.push(match.index);
	}
	return matches;
}


function focusWord(word, onoff) {
	if(onoff==true) focusedWords = [word];
	else focusedWords = [];
	// UPDATE TOPIC WORDS
	$("div.term").removeClass("highlighted");
	$("div.term").filter(function() { return focusedWords.indexOf($(this).text())!=-1; })
		.addClass("highlighted");
	// SHOW WORDS IN THE DOCUMENTS
	if(focusedWords.length==0) {
		$(".keyPhrase").empty();
		$("li.document_item").removeClass("showingKeyPhrase");
	}
	// REMOVE ALL HIGHLIGHTS IN DOCUMENTS
	$(".keyPhrase").empty();
	$(".fulltext").each(function(i,el) {
		$(el).html($(el).text());
	});
	$("li.document_item").removeClass("showingKeyPhrase");
	// ADD NEW HIGHLIGHTS
	_.each(focusedWords, function(w) {
		$("li.document_item").each(function(i,el) {
			var w_reg_raw = new RegExp("("+w+")", 'ig');
			var w_reg_with_space_around = new RegExp("([^a-zA-Z]|^)("+w+")[^a-zA-Z]", 'ig');
			// HIGHLIGHTING TITLE
			var title = $(el).find(".title").text();
			title_with_highlight = title.replace(w_reg_with_space_around, " <span class='keyword'>$2</span> "); 
			$(el).find(".title").html(title_with_highlight);
			// HIGHLIGHTING FULLTEXT
			var fulltext = $(el).find(".fulltext").text();
			var indices = findAllIndicesOfSubstring(fulltext, w);
			
			if(indices.length>0) {
				var ind = indices[0];
				var phraseAroundWord = fulltext.substring(Math.max(0,ind-40), Math.min(fulltext.length,ind+40))
					.replace(/^[a-zA-Z0-9]+\s/i,"").replace(/\s[a-zA-Z0-9]+$/i,""); 
				phraseAroundWord= phraseAroundWord.replace(w_reg_with_space_around, " <span class='keyword'>$2</span> ");
				$(el).find(".keyPhrase").html("... "+phraseAroundWord+ " ...");
				$(el).addClass("showingKeyPhrase");
				// ALSO HIGHLIGHT THE WORD IN THE FULLTEXT
				text_with_highlight = fulltext.replace(w_reg_with_space_around, " <span class='keyword'>$2</span> "); 
				$(el).find(".fulltext").html(text_with_highlight);
			} 
		});
	});
}

$(document).ready(function() {
	ALPHABET = "abcdefghijklmnopqrstuvwxyz";
	focusedWords = [];
	refPhase1 = [];
	refPhase2 = [];
	events = [];

	// HIDE ALL TOPICS EXCEPT 10 
	// $("li.topic").hide();
	// $.each(_.sample($("li.topic").toArray(),10), function(i,el){ 
	// 	$(el).show(); 
	// });


	// GENERAL EVENT HANDLER
	//  	SELECTING TOPIC WHEN CLICKED
	$("li.topic").click(function() {
		if($(event.target).parents("li.topic").hasClass("selected")==true) return; 
		var topicIdx = $(this).attr('tid');
		var kID = $(this).attr('kid');
		showDocuments(parseInt(topicIdx));
		events.push({type:'click_topic',topicIdx:topicIdx,kID:kID,timestamp:new Date().getTime()});
	});
	$(".document_show").click(function(){
		$(this).hide();
		$("ul.document_list").show();
		$("li.topic.selected").attr("unlocked","true");
		events.push({type:'show_document',topicIdx:$("li.topic.selected").attr("tid"),kID:$("li.topic.selected").attr("kid"),timestamp:new Date().getTime()});
	});
	$(".document_hide_all").click(function() {
		$("li.topic").attr("unlocked","false");
		$("ul.document_list").hide();
		events.push({type:'show_all_documents',timestamp:new Date().getTime()});
	});
	$(".document_show_all").click(function() {
		$("li.topic").attr("unlocked","true");
		$("ul.document_list").show();
		$(".document_show").hide();
		events.push({type:'hide_all_documents',timestamp:new Date().getTime()});
	});
	showDocuments(parseInt($("li.topic:visible:first").attr('tid')));

	// WORD CLICK EVENT HANDLER
	$("ul.topic_list").on("mouseover", "div.term" ,function(event) {
		// WORKS FOR SELECTION TOPIC ONLY
		// if($(event.target).parents("li.topic").hasClass("selected")==false) return; 
		var tid = $(event.target).parents("li.topic").attr('tid');
		focusWord($(event.target).text(),true);
		//events.push({type:'focus_word',topicIdx:tid,kID:$("li.topic.selected").attr("kid"), word:$(event.target).text(), timestamp:new Date().getTime()});
		event.stopPropagation();
	});
	$("ul.topic_list").on("mouseout", "div.term" ,function(event) {
		// WORKS FOR SELECTION TOPIC ONLY
		// if($(event.target).parents("li.topic").hasClass("selected")==false) return; 
		// var tid = $(event.target).parents("li.topic").attr('tid');
		focusWord($(event.target).text(),false);
		//events.push({type:'focus_word',topicIdx:tid,kID:$("li.topic.selected").attr("kid"), word:$(event.target).text(), timestamp:new Date().getTime()});
		event.stopPropagation();
	});
	// LOG SUBMIT EVENT
	$("button.submit_log").click(function() {
		submitLog();
	});


	// PHASE1 : OPEN_ENDED REFINEMENT 
	function startPhase1() {
		$(".bottom_UI > .clock").show();
		// $("button.next_stage").show();
		openingPhase1 = new Date().getTime();
		updateClock(openingPhase1, 15, $(".bottom_UI").find(".clock"));
    	int_clock1 = setInterval(function() {updateClock(openingPhase1, 15, $(".bottom_UI").find(".clock"));  }, 1000); 
	}
	startPhase1();
	// $(".open_template > textarea").click(function() {
	// 	if (typeof openingPhase1 == "undefined") startPhase1();
	// });
	$("button.add_open_ref").click(function() {
		var ref_desc = $(".open_template").find("textarea.full-col-text").val();
		if(ref_desc=="") {
			showWarning("Cannot create an empty description.");
			return;
		} else {  
			showWarning("");
		}
		var new_open_ref = {
			'rid': makeid(),
			'ref_type':"open-refinement",
			'description' : ref_desc,
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