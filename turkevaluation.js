////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
TOTAL_NUM_THEME = 10
currentTheme = -1;
result = {"topics":[]};
log = [];
isInternal = false;
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////

// EDITING MODE RELATED STUFF
function disableEditing(cur_mode) {
	// MAYBE UNNECESSARY
}


function retrieveThemes() {
	numArticles = getURLParameter('numArticles'); 
	$.get("retrieveEvaluationData",{numArticles:numArticles},function(data) {
		$("span.loading_status").addClass("hidden");
		d = JSON.parse(data);
		material = JSON.parse(d["material"]);
		tutorialData = d["tutorial"];
		taskID = d["taskID"];
		refinedTopicID = d["refinedTopicID"];
		$("a.participate_button").removeClass("hidden");
	}).fail(function() {
		$("span.loading_status").text("Sorry. It failed to retrieve data from server. Please contact the administrator: reflect9@gmail.com").css("color","red");
	});
}
function replaceSubWords(e) {
	//  convert a[b,c] to  a<span class='sub_words'>b,c</span>
	return e.replace(/\[/g,"<span class='sub_words'>").replace(/\]/g,"</span>");
}

function populateTheme(data) {
	////// INITIALIZE SPLITTED THEME DATA
	$("button.undo").text("Undo the latest refinement");
	splittedTheme = $("");
	/////
	if (data['isTutorial']) {
		var topicID = parseInt(data['tid']);
		var words = _.map(data['words'], function(e) { return replaceSubWords(e); });
		var docs = data['articles'];   // 7 ARTICLES RANDOMLY CHOSEN
		var intruder = data['intruder'];	
	} else {
		var topicID = parseInt(data['tid']);
		var words = _.map(data['theme'], function(e){  return replaceSubWords(e); });
		var docs = data['articles'];   // 7 ARTICLES RANDOMLY CHOSEN
		var intruder = data['intruder'];	
	}
	////// WORDS FOR MAIN THEME
	$(".theme_container").attr("tid",topicID);
	var ul_words = $(".theme_container").find("ul.words");
	$(ul_words).empty();
	_.each(words, function(w) {
		$("<li class='word noselect'>"+w+"</li>")
			// .css("font-size",15+(w['freq']/200))  // ADDED / MERGED WORDS DO NOT HAVE FONT SIZES
			.appendTo(ul_words);
	});

	if (data['rid']=="original") {
		$(".document_wrapper label .smaller").text("Click an article to expand it.");
	} else {
		$(".document_wrapper label .smaller").text("Click an article to expand it");
	}
	
	////// BAKE DOCUMENTS
	var ul_documents = $(".theme_container").find("ul.documents")
		.empty()
		.removeClass("marker_active");
	docs.push(intruder);
	shuffle(docs);
	_.each(docs, function(doc, i) {
		var title = doc['content']['title'];
		var fulltext = doc['content']['text'];
		var other_topics = doc['other_topics'];
		var lastSpaceIdx = fulltext.substring(0,1500).search(/ [^ ]*$/);
		var trimmedFulltext = fulltext.substring(0,lastSpaceIdx);
		var weight = Math.round(doc['weight']*100);
		var current_weight_base = 100;
		// MARKING fulltext with theme words
		var markedHTML = trimmedFulltext;
		// _.each(words, function(w) {
		// 	// console.log(w);
		// 	// console.log(markedHTML);
		// 	var w_reg_with_space_around = new RegExp("([^a-zA-Z\>\<]|^)("+w['word']+")[^a-zA-Z\<\>]", 'ig');
		// 	markedHTML = markedHTML.replace(w_reg_with_space_around," <em>$2</em> " );
		// });
		var doc_el = $("<li class='document' nth='"+i+"' file='"+doc['file']+"'>\
			<img class='marker_inconsistent' src='images/x-rect-bl.png'>\
			<div class='title'>"+title+"</div>\
			<div class='keyPhrase'></div>\
			<div class='fulltext'>"+markedHTML+"</div>\
		</li>");
		$(ul_documents).append(doc_el);
	});
	/////// UPDATE NEXT THEME BUTTON TO SHOW PROGRESS
	// if(currentTheme == themeData.length-1) {  // SHOW FINALIZE
	// 	$("a.next_theme span").text("Finish");
	// } else {
	// 	$("a.next_theme span").text("Next theme ("+(currentTheme+1)+" of "+(themeData.length-1)+")");
	// }

	/////// UPDATE DOCUMENT SECTION HEIGHT
	matchDocumentSectionHeight();
}
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////

function openTutorial() {
	populateTheme(tutorialData);
	openPage("intro");	
}
function openTheme(topicNum) {
	// HIDE MAIN COMPONENTS AND SHOW LOADING MESSAGE
	$("div.main_container").hide();
	$("<div class='loading'>Loading the next theme and articles</div>").appendTo("body")
	.toggleClass("dimmed",1000).toggleClass("dimmed",1000)
	.queue(function() {
		$("div.loading").remove();
		$("div.main_container").show("fade");
		populateTheme(material[topicNum]);
		$(".topbar .top_title").text("Theme "+(currentTheme+1)+" out of 10");	
		openPage("real_task");
	});
}
function openPage(target) {
	disableEditing();
	$("div.page:visible").addClass("hidden");
	var page = $("div.page[pagetype='"+target+"']");
	///// CLEAN UP ALL THE INPUT AND TEXTAREA
	$(page).find("textarea, input").val("");
	$(page).find("input[type='radio']").prop('checked',false);
	///// MAKE THE PAGE VISIBLE
	$(page).removeClass("hidden");
	addLog("OPEN_PAGE",target);
	// HIDE SECTIONS AND NEXT THEME / PAGE BUTTON
	$(page).find("div.section").addClass("hidden");
	$(page).find(".next_theme, .next_page, .finalize_hit").addClass("hidden");
	$(page).find(".next_section").removeClass("hidden");
	$("div.information_container").animate({
		scrollTop: 0
	},'fast');
	$("div.theme_container").animate({
		scrollTop: 0
	},'fast');


	// OPEN THE FIRST SECTION
	openSection();

}
function openSection() {
	// WILL BE TRIGGERED WHEN A PAGE IS OPENEND OR CONTINUE BUTTON IS CLICKED
	// 0. REMOVE HIGHLIGHTS
	$(".castAura").removeClass("castAura");
	$(".dimmed").removeClass("dimmed");

	// 1. FIND CURRENTLY OPEN SECTION
	var current_page = $("div.page:visible");
	var invisible_sections = $(current_page).find("div.section.hidden");

	// 2. OPEN NEXT SECTION.  
	//	   case a. IF NEXT SECTION EXISTs, JUST OPEN IT
	if (invisible_sections.length>=1) {
		var section_to_show = invisible_sections[0];
		$(section_to_show).removeClass("hidden");
		addLog("OPEN_SECTION",$(section_to_show).attr("sectionID"));

		// SPECIAL CASES: IF THERE's highlight attribute, then highlight the element.
		if($(section_to_show).attr("highlight")) {
			var div_to_highlight = $(section_to_show).attr("highlight");
			$(div_to_highlight).addClass("castAura");
		}
		if($(section_to_show).attr("dim")) {
			var dim_to_dim = $(section_to_show).attr("dim");
			$(dim_to_dim).addClass("dimmed");
		}
		// // SPECIAL CASE:  HIDE NEXT BUTTON IF IT's ABOUT PRACTICING TOOL USAGE
		// if($(section_to_show).find("div.tool_practice_detail").length>0) {
		// 	$(section_to_show).parents(".page").find(".next_section").addClass("hidden");
		// }
	}
	// IF NO NEXT SECTION EXISTS, SHOW NEXT_THEME BUTTON
	else if (invisible_sections.length==0) {
		$(current_page).find(".next_theme, .next_page").trigger("click");
	}
	////// SPECIAL CASES
	/// OPENING TOOLS FOR PRACTICE
	var target = $(section_to_show).attr("sectionID");
	if(target=="read_over_the_theme" || target=="nested_words" || target=="explore_articles") {
		$(section_to_show).parents(".page").find(".next_section").addClass("hidden");
	}
	if(target=="read_over_the_theme" || target=="nested_words") { 
		$(section_to_show).find("textarea.mini_task").focus();
	}
	if(target=="explore_articles") {
		$(section_to_show).parents(".page").find(".next_section").addClass("hidden");
		// ACTIVATE DOCUMENT MARKER 
		$("div.documents_section ul.documents").addClass("marker_active");
		$("div.documents_section ul.documents img.marker_inconsistent").click(function(event){
			addLog("REMOVE_ARTICLES",$(this).parents("li.document").attr("nth"));
			// CLEAN ALL REMOVED ARTICLES STATES
			$("div.documents_section ul.documents li.document img.marker_inconsistent").removeClass("checked");
			$("div.documents_section ul.documents li.document").removeClass("removed");
			// SET THE CURRENT ONE REMOVED
			$(this).addClass("checked");
			$(this).parents("li.document").toggleClass("removed");
			validateSection();
			event.stopPropagation();
		});
	}
	if(target=="finding_unrelated_article") {
		$(section_to_show).parents(".page").find(".next_section").addClass("hidden");
		// ACTIVATE DOCUMENT MARKER 
		$("div.documents_section ul.documents").addClass("marker_active");
		$("div.documents_section ul.documents img.marker_inconsistent").click(function(event){
			addLog("REMOVE_ARTICLES",$(this).parents("li.document").attr("nth"));
			// CLEAN ALL REMOVED ARTICLES STATES
			$("div.documents_section ul.documents li.document img.marker_inconsistent").removeClass("checked");
			$("div.documents_section ul.documents li.document").removeClass("removed");
			// SET THE CURRENT ONE REMOVED
			$(this).addClass("checked");
			$(this).parents("li.document").toggleClass("removed");
			validateSection();
			event.stopPropagation();
		});
	}
	// ////////  ADD WORDS FOR SPLITTING THEME
	// if(target=="split_theme") { 	
	// 	_.each(["pasta","olive","fish"], function(w) {
	// 		$("<li class='word'>"+w+"</li>").appendTo("div.theme_container div.words_section ul.words");
	// 	});  
	// }
	// if(target=="remove_words") { 	
	// 	_.each(["york","west"], function(w) {
	// 		if ($("div.theme_container div.words_section ul.words li.word").filter(function(i,li){return $(li).text()==w; }).length==0) {
	// 			$("<li class='word'>"+w+"</li>").appendTo("div.theme_container div.words_section ul.words");	
	// 		}
	// 	});  
	// }
	// if(target=="change_word_order") { 	
	// 	_.each(["concert"], function(w) {
	// 		if ($("div.theme_container div.words_section ul.words li.word").filter(function(i,li){return $(li).text()==w; }).length==0) {
	// 			$("<li class='word'>"+w+"</li>").appendTo("div.theme_container div.words_section ul.words");	
	// 		}
	// 	});  
	// }
	// if(target=="add_words" || target=="remove_words" || target=="merge_words" || target=="change_word_order" || target=="split_theme" || target=="remove_articles"){
	// 	enableEditing(target.replace("practice_",""),true);
	// }
	////// START TIMER FOR THEME_IMPROVEMENTS
	// if(target=="theme_improvements") {
	// 	startTime = Math.floor(Date.now() / 1000);
	// }
	// if(target=="eval_after_improvements") {
	// 	// TELL WHAT WAS THE USER'S EVALUATION FOR THE ORIGINAL THEME AND ARTICLES
	// 	var improved_likert_el = $("div.section[sectionID='eval_after_improvements']");
	// 	//// 
	// 	var prev_answer_desc = $(improved_likert_el).find("div.likert_chart[name='theme_clarity'] div.likert_point[v='"+evaluation_before[0]+"']").attr('desc');
	// 	$(improved_likert_el).find("div.likert_chart[name='theme_clarity'] div.tiny_notice span").text(prev_answer_desc);	
	// 	//// 
	// 	var prev_answer_desc = $(improved_likert_el).find("div.likert_chart[name='article_consistency'] div.likert_point[v='"+evaluation_before[1]+"']").attr('desc');
	// 	$(improved_likert_el).find("div.likert_chart[name='article_consistency'] div.tiny_notice span").text(prev_answer_desc);
	// 	//// 
	// 	var prev_answer_desc = $(improved_likert_el).find("div.likert_chart[name='correlation'] div.likert_point[v='"+evaluation_before[2]+"']").attr('desc');
	// 	$(improved_likert_el).find("div.likert_chart[name='correlation'] div.tiny_notice span").text(prev_answer_desc);
	// }
}

function validateSection() {
	var current_page = $("div.page:visible"); 	var current_page_type = $(current_page).attr("pagetype");
	var current_section = $(current_page).find("div.section:not(.hidden):last");
	var html_goodjob = "<b>Good job!</b> Move on to the next refinement.";
	var html_badjob = "<b>Try again.</b> You can proceed after completing the task above.";
	if($(current_section).length==1) { 
		var cs = $(current_section).get(0);
		if(current_page_type=="intro" && $(cs).attr("sectionID")=="read_over_the_theme") {
			// CHECKING THE FIRST TUTORIAL QUESTION OF FIDNING THE MOST FREQUENT TOPIC WORD
			console.log($(cs).find("textarea.mini_task").val());
			var correctAnswer = $("div.theme_container div.words_section ul.words li.word:first").text();
			if ($.trim(correctAnswer).toLowerCase() == $.trim($(cs).find("textarea.mini_task").val().toLowerCase())) {
				$(cs).find(".mini_feedback").html("<b>Correct!</b> The first word is the most meaningful word in the theme.");	
				return true;
			} else {
				$(cs).find(".mini_feedback").html("<span style='color:red'>Try again. </span>The first word is the most meaningful word in the theme.");	
				return false;
			} 
		} else if(current_page_type=="intro" && $(cs).attr("sectionID")=="nested_words") {
			var correctAnswer = "hall";
			if ($.trim(correctAnswer).toLowerCase() == $.trim($(cs).find("textarea.mini_task").val().toLowerCase())) {
				$(cs).find(".mini_feedback").html("<b>Correct!</b> Theater and hall are in the same group under venue.");	
				return true;
			} else {
				$(cs).find(".mini_feedback").html("<span style='color:red'>Try again. </span> What word is under 'venue' with theater?");	
				return false;
			} 
		} else if(current_page_type=="intro" && $(cs).attr("sectionID")=="explore_articles") {
			var correctAnswer = "Iraqi Forces in Fierce Battle With Gunmen";
			var answer = $.makeArray($("ul.documents li.removed div.title").text())[0]; 
			if (answer == correctAnswer) {
				$(current_section).find(".tool_practice_result").addClass("correct").html("<b>Good job!</b>").css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
				return true;
			} else {
				$(current_section).find(".tool_practice_result").html("<b>Try again.</b>").css("background-color","#f69256").animate({"background-color":"#fff"},500);
				return false;
			}
		} else if(current_page_type=="real_task" && $(cs).attr("sectionID")=="finding_unrelated_article") {
			if ($("ul.documents li.removed").length==0) {
				return false;
			} else {
				$("div.page:visible a.next_section").removeClass("hidden");
				return true;
			}
		} 
		// // PRACTICE 
		// } else if($(current_section).attr("sectionID")=="eval_theme") {
		// 	var checkedInputs = $(current_section).find("input:checked");
		// 	if($(checkedInputs).length==3) {
		// 		evaluation_theme = $.makeArray($(checkedInputs).map(function(i,el){return $(el).attr("v");}));
		// 		return true;
		// 	} else {
		// 		alert("Please answer all the questions to proceed");
		// 		return false;
		// 	}
		// } 
	} else { // DO NOTHING
	}
	return true;
}
function capitalize(s) {
    // returns the first letter capitalized + the string from index 1 and out aka. the rest of the string
    return s[0].toUpperCase() + s.substr(1);
}
function matchDocumentSectionHeight() {
	var offset = $("div.documents_section").offset();
	$("div.documents_section").height($(window).height() - offset.top);
}
function getURLParameter(name) {
  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
}
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
function focusWord(word, onoff) {
	// CHECK WHETHER IT'S THE RIGHT SITUATION
	if($("div.documents_section").is(":visible") && $("div.words_section").is(":visible")) {} 
	else { return; }
	// JUST HANDLING SINGLE WORD
	if(onoff==true) focusedWords = [word];
	else focusedWords = [];
	// UPDATE TOPIC WORDS
	// $("div.term").removeClass("highlighted");
	// $("div.term").filter(function() { return focusedWords.indexOf($(this).text())!=-1; })
	// 	.addClass("highlighted");
	// SHOW WORDS IN THE DOCUMENTS
	if(focusedWords.length==0) {
		$(".keyPhrase").empty();
		$("li.document").removeClass("showingKeyPhrase");
	}
	// REMOVE ALL HIGHLIGHTS IN DOCUMENTS
	$(".keyPhrase").empty();
	// $(".fulltext").each(function(i,el) {
	// 	$(el).html($(el).text());	// REMOVE SPAN TAGS
	// });
	$("li.document").removeClass("showingKeyPhrase");
	$("li.document em").removeClass("kw");
	// ADD NEW HIGHLIGHTS
	_.each(focusedWords, function(w) {
		$("li.document").each(function(i,el) {
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
				var ind_context_start = ind-2;
				while(ind_context_start>0) {
					if(fulltext[ind_context_start]==" " || fulltext[ind_context_start]==".") break; 
					else ind_context_start=ind_context_start-1;
				}
				var ind_context_end = ind+w.length+2;
				if(w=="dr" || w=="mr" || w=="ms" || w=="st") ind_context_end++;
				while(ind_context_end<fulltext.length) {
					if(fulltext[ind_context_end]==" ") break; 
					else ind_context_end=ind_context_end+1;
				}
				var phraseAroundWord = fulltext.substring(ind_context_start, ind_context_end);
				phraseAroundWord= phraseAroundWord.replace(w_reg_with_space_around, " <span class='keyword'>$2</span> ");
				$(el).find(".keyPhrase").html(phraseAroundWord);
				//$(el).addClass("showingKeyPhrase");
			}
			// ALSO HIGHLIGHT THE WORD IN THE FULLTEXT
			$(el).find("em").filter(function(i,em){ 
				return $(em).text().toLowerCase()==w.toLowerCase(); 
			}).addClass("kw"); 
		});
	});
}
function findAllIndicesOfSubstring(long, short) {
	var reg = new RegExp("[^a-zA-Z]"+short+"[^a-zA-Z]", 'ig');
	var match, matches = [];
	while ((match = reg.exec(long)) != null) {
	  matches.push(match.index);
	}
	return matches;
}

Array.prototype.equals = function (array) {
    // if the other array is a falsy value, return
    if (!array)
        return false;
    // compare lengths - can save a lot of time 
    if (this.length != array.length)
        return false;
    for (var i = 0, l=this.length; i < l; i++) {
        // Check if we have nested arrays
        if (this[i] instanceof Array && array[i] instanceof Array) {
            // recurse into the nested arrays
            if (!this[i].equals(array[i]))
                return false;       
        }           
        else if (this[i] != array[i]) { 
            // Warning - two different object instances will never be equal: {x:20} != {x:20}
            return false;   
        }           
    }       
    return true;
}   
function shuffle(o){
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
}

function addLog(event, message) {
	log.push({
		"event": event,
		"message": (typeof message==="undefined")?"":message,
		"timestamp": Math.floor(Date.now() / 1000)
	});
	console.log(event, message);
}

////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////


function extractResultFromUI() {
	// EXTRACT USER'S INPUT FOR ONE THEME FROM ALL THE PAGES
	var resultForTheme = {"tid":$("div.theme_container").attr("tid")  };
	///// PICKED UNRELATED ARTICLE
	resultForTheme["file_list"]=$.makeArray($("ul.documents li").map(function(i,el){return $(el).attr("file"); }));
	resultForTheme["unrelated_article"]=$("ul.documents li.removed").attr("file");
	///// LOG DATA
	resultForTheme["log"]=JSON.parse(JSON.stringify(log));  // DEEP COPY LOG OBJECT
	log = [];
	// PUSH THEME RESULT TO THE OVERALL RESULT
	result["topics"].push(resultForTheme);
}
function submitResult() {
	///// SUBMISSION 
	var data = {
		'result':JSON.stringify(result),
		"taskID":taskID,
		"refinedTopicID":refinedTopicID
	};
	$.post("submitTurkEvaluation",data, function(res){
		$(".main_container").addClass("hidden");
		$(".final_feedback").html(res);
		//alert("Thank you! Submitted");
	});



}

////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
$(document).ready(function() {
	// NAV HANDLERS
	$("a.participate_button").click(function() {
		// minimizeIntroduction(); 	
		$(".introduction").addClass("hidden");
		$(".main_container").removeClass("hidden");
		openTutorial();
		addLog("START_TUTORIAL");
	});

	// NEXT THEME BUTTON IS CLICKED FOR SHOWING NEW THEME
	$("a.next_theme").click(function() {
		currentTheme+=1;
		disableEditing();
		if(currentTheme>0) extractResultFromUI();	// EXTRACT DATA FROM UI AND STORE IN VARIABLE
		if(currentTheme==TOTAL_NUM_THEME) {
			submitResult(); // FINALIZE
		} else {
			openTheme(currentTheme); // INITIALIZE TASK INFORMATION AND THEME, ARTICLES
			addLog("OPEN_THEME",currentTheme);	
		}
		// openPage("real_task");	
	});	

	// $("a.next_page").click(function() {
	// 	// VALIDATE IF THERE'S NO EMPTY TEXTAREA
	// 	var is_valid = true;
	// 	$(this).parents(".page").find("textarea.required").each(function(i,el){
	// 		if ($(el).val()=="") is_valid=false;
	// 	});
	// 	var pageType = ($(this).attr("target")==undefined)? $(this).parents("div.page").next("div.page").attr("pagetype") : $(this).attr("target");
	// 	openPage(pageType);
	// });
	$("a.next_section").click(function(event) {
		if(validateSection()) {
			disableEditing();
			openSection();
			$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');		
		}
	});

	// THEME AND DOCUMENTS HANDLERS
	$("ul.documents").on("click","li.document", function() {
		var mode = ($(this).hasClass("selected"))?"-off":"-on";
		$(this).toggleClass("selected",500);
		addLog("TOGGLE_DOCUMENT",$(this).attr("nth")+mode);
	});
	// $("div.theme_container div.words_section").on("mouseenter","ul.words li.word",function(){
	// 	focusWord($(this).text_without_children(),true);
	// 	event.stopPropagation();
	// });
	// $("div.theme_container div.words_section").on("mouseleave","ul.words li.word",function(){
	// 	focusWord($(this).text_without_children(),false);
	// 	event.stopPropagation();
	// });
	
	$("textarea.mini_task").on('input propertychange paste',function(){
		var isValid = validateSection();
		if (isValid) {
			$(this).parents("div.page").find("a.next_section").removeClass("hidden");
			$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
		}
	});

	// MAKING THEME STICKY AT THE TOP
	// $("div.theme_container").scroll(function(e) {
	// 	var el = $('div.theme_container div.words_wrapper'); 
	// 	if ($(this).scrollTop() > 62 && el.css('position') != 'fixed'){ 
	// 		$(el).css({'position': 'fixed', 'top': '-45px', 'margin-right':'8px', 'z-index':104}); 
	// 		$("div.theme_container div.documents_wrapper").css("padding-top",$(el).height());
	// 		$("div.theme_container div.documents_wrapper").css("padding-bottom",$(el).height());
	// 	} else if ($(this).scrollTop() < 62 && el.css('position') == 'fixed'){
	// 		$(el).css({'position': 'static', 'top': '-45px', 'margin-right':'0px'}); 
	// 		$("div.theme_container div.documents_wrapper").css("padding-top",0);
	// 		$("div.theme_container div.documents_wrapper").css("padding-bottom",0);
	// 	} 
	// });

	// UPDATE DOCUMENT SECTION HEIGHT FOR WINDOW RESIZE EVENT
	$(window).resize(function() {
		matchDocumentSectionHeight();
	});
	$(document).keydown(function(objEvent) {
	    if (objEvent.keyCode == 9) {  //tab pressed
	    	$("a.next_section:visible").trigger("click");
	        objEvent.preventDefault(); // stops its action
	    }
	    if (objEvent.which === 8 && !$(objEvent.target).is("input, textarea")) {
	        objEvent.preventDefault();
	    }
	})

	// SHORTCUT TO THE THEMEEDITOR VIEW
	$("button.shortcut").click(function() {
		$("a.participate_button").trigger("click");
		// openPage("improving");
		openPage($(this).attr("target"));
	});
	
	// GETTING TOP-LEVEL TEXT OF ELEMENT WITHOUT CHILDREN
	$.fn.text_without_children = function() {
    	return $(this).clone().children().remove().end().text(); 
  	}
  	// GETTING ARRAY Of CHILDREN TEXT
  	$.fn.children_text = function() {
    	return $.makeArray($(this).find("span").map(function(i,el){return $(el).text_with_gap();}));
  	}
  	$.fn.text_with_gap = function() {
    	var result =  $(this).text_without_children();
    	if ($(this).children_text().join(",")=="") return result;
    	else return result + "[" + $(this).children_text()  + "]";
  	}
	
	$.fn.shuffle = function() {
        var allElems = this.get(),
            getRandom = function(max) {
                return Math.floor(Math.random() * max);
            },
            shuffled = $.map(allElems, function(){
                var random = getRandom(allElems.length),
                    randEl = $(allElems[random]).clone(true)[0];
                allElems.splice(random, 1);
                return randEl;
           });
        this.each(function(i){
            $(this).replaceWith($(shuffled[i]));
        }); 
        return $(shuffled);
    };

	// SET AUTO-RESIZE TEXTAREA
	$.each($('textarea[data-autoresize]'), function() {
	    var offset = this.offsetHeight - this.clientHeight;
	    var resizeTextarea = function(el) {
	        $(el).css('height', 'auto').css('height', el.scrollHeight + offset);
	    };
	    $(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
	});

	retrieveThemes();

});