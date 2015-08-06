//////////////////////
///  THEME EDITOR FUNCTIONS

function removeThemeEditor() {
	$("img.marker_inconsistent").removeClass("checked");
	$("img.marker_inconsistent").unbind();
	$("ul.documents").removeClass("marker_active");
}
function removeSelectedWords() {
	$("ul.editable_words li.selected").remove();
	update_ui_for_word_selection();
}
function mergeSelectedWords(w) {
	if($("ul.editable_words li.selected").length==0) {
		alert("You must click words first."); return; 
	}
	// CHECK IF THE WORD EXISTS
	var words_el = $("ul.editable_words li").filter(function() { return $(this).text() === w; });
	if(words_el.length>0) { alert("The same word exists."); return false;  }
	//
	var words = [];
	$("ul.editable_words li.selected").each(function(i,w){  words.push($(w).html()); });
	removeSelectedWords();
	addWord(w+"<span class='sub_words'>"+words.join(",")+"</span>");
}
function addWord(w, size) {
	var words_el = $("ul.editable_words li").filter(function() { return $(this).text() === w; });
	if(words_el.length>0) { alert("The same word exists."); return false;  }

	var el = $("<li class='word noselect' style='font-size:16px'>"+w+"</li>").click(function() {
		$(this).toggleClass("selected");
		update_ui_for_word_selection();
	});
	if(typeof size !== "undefined") $(el).css("font-size",size);
	$(el).css("background","#00b3ca").appendTo("ul.editable_words");
	$(el).animate({"background-color":"#ddd"},1500,function() {
		$(this).css({"background":""});
	});
	return true;
}
// function splitSelectedWords() {
// 	if($("ul.words li.selected").length==0) {
// 		alert("You must click words first."); return; 
// 	}
// 	// ADD SPLITED WORDS TO ul.list_splited
// 	var newGroup = $("<li></li>");
// 	$("ul.words li.selected").each(function(i,li){
// 		$("<span>"+$(li).text()+"</span>")
// 			.appendTo(newGroup);
// 	});
// 	$(newGroup).click(function() {  // REVERT SPLITTING
// 		$(this).find("span").each(function(i,sp){
// 			var word_to_revive = $(sp).text();
// 			$("ul.words li.splitted").filter(function(){ return $(this).text()===word_to_revive;})
// 				.removeClass("splitted");
// 		});
// 		$(this).remove();
// 	});
// 	$(newGroup).appendTo("ul.edit_tools ul.list_splited");
// 	// HIDE SPLITED WORDS 
// 	$("ul.words li.selected").addClass("splitted");
// 	$("ul.words li.selected").removeClass("selected");
// }
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////

function retrieveThemes() {
	$.get("retrieveThemeData",function(data) {
		d = JSON.parse(data);
		themeData = _.values(d["topics"]);
		tutorialData = d["tutorial"];
		console.log("data loaded");
		$("a.participate_button").text("Participate");
	});
}
function update_ui_for_word_selection() {
	var selected_words = $(".theme_container div.editable_words_section ul.editable_words li.word.selected");
	$("div.ui_for_adding_words").addClass("hidden");
	$("div.ui_for_merging_words").addClass("hidden");
	if(selected_words.length>1) {
		$("div.editable_words_section span.add_word").addClass("hidden");
		$("div.editable_words_section span.merge_word").removeClass("hidden");
	} else {
		$("div.editable_words_section span.merge_word").addClass("hidden");
		$("div.editable_words_section span.add_word").removeClass("hidden");
	}
}

function populateTheme(data) {
	var topicID = parseInt(data['tid']);
	var words = data['words'].slice(0,20);
	var additional_words = data['words'].slice(20,40);
	var docs = data['documents'];
	
	////// WORDS FOR MAIN THEME
	var ul_words = $(".theme_container").find("ul.words");
	$(ul_words).empty();
	_.each(words, function(w) {
		$("<li class='word noselect'>"+w['word']+"</li>")
			.css("font-size",15+(w['freq']/200))
			.appendTo(ul_words);
	});
	$(ul_words).find("li").hover(function(event) {
		focusWord($(this).text(),true);
		event.stopPropagation();
	}, function(event) {
		focusWord($(this).text(),false);
		event.stopPropagation();
	});
	////// WORDS FOR EDITABLE THEME
	var ul_words = $(".theme_container").find("ul.editable_words");
	$(ul_words).empty();
	_.each(words, function(w) {
		$("<li class='word noselect'>"+w['word']+"</li>")
			.css("font-size",15+(w['freq']/200))
			.appendTo(ul_words);
	});
	$(ul_words).find("li").hover(function(event) {
		focusWord($(this).text(),true);
		event.stopPropagation();
	}, function(event) {
		focusWord($(this).text(),false);
		event.stopPropagation();
	});
	$(ul_words).find("li").click(function(event) {
		$(this).toggleClass("selected");
		update_ui_for_word_selection();
	});
	$(ul_words).sortable({
		appendTo:"body"
	});
	$(ul_words).disableSelection();
	// SETTING UP DROPPABLE EVENT FOR BUCKETS
	$("div.removed_words_bucket ul.ul_bucket").empty();
	$("div.removed_words_bucket").droppable({
		drop: function(e,f) {
			$("div.removed_words_bucket label.bucket_instruction").addClass("hidden");
			f.draggable.remove();
			update_ui_for_word_selection();
			$("<li class='word'>"+f.draggable.html()+"</li>")
				.attr("size",f.draggable.css("font-size"))
				.mousedown(function() { // ADD BACK TO THE WORD LIST
					addWord($(this).html(),$(this).attr("size"));
					$(this).parents("div.bucket").find(".bucket_instruction_bottom").addClass("hidden");  
					$(this).remove();
				})
				.hover(function() { 
					$(this).parents("div.bucket").find(".bucket_instruction_bottom").removeClass("hidden"); 
				}, function() { 
					$(this).parents("div.bucket").find(".bucket_instruction_bottom").addClass("hidden");  
				}).appendTo($(this).find("ul.ul_bucket"));
		}
	});
	$("div.removed_words_bucket").disableSelection();
	$("div.splitted_words_bucket ul.ul_bucket").empty();
	$("div.splitted_words_bucket").droppable({
		drop: function(e,f) {
			$("div.splitted_words_bucket label.bucket_instruction").addClass("hidden");
			f.draggable.remove();
			update_ui_for_word_selection();
			$("<li class='word'>"+f.draggable.html()+"</li>")
				.attr("size",f.draggable.css("font-size"))
				.mousedown(function() { // ADD BACK TO THE WORD LIST
					addWord($(this).html(),$(this).attr("size"));
					$(this).parents("div.bucket").find(".bucket_instruction_bottom").addClass("hidden");  
					$(this).remove();
				})
				.hover(function() { 
					$(this).parents("div.bucket").find(".bucket_instruction_bottom").removeClass("hidden"); 
				}, function() { 
					$(this).parents("div.bucket").find(".bucket_instruction_bottom").addClass("hidden");  
				}).appendTo($(this).find("ul.ul_bucket"));
		}
	});
	$("div.splitted_words_bucket").disableSelection();

	// SETTING UP ADDTIONAL WORDS
	var ul_additional_words = $(".theme_container .editable_words_section ul.additional_words");
	$(ul_additional_words).empty();
	_.each(additional_words, function(w) {
		$("<li class='word noselect'>"+w['word']+"</li>")
			.click(function() {
				addWord($(this).text());
			})
			.appendTo(ul_additional_words);
	});
	// MAKING DOCUMENTS SELECTABLE
	$("ul.documents").addClass("marker_active");
	$("img.marker_inconsistent").removeClass("checked");
	$("img.marker_inconsistent").unbind();
	$("img.marker_inconsistent").click(function(event){
		$(this).toggleClass("checked");
		$(this).parents("li.document").toggleClass("removed");
		event.stopPropagation();
	});
	////// WORDS FOR QUESTIONS
	$("div.page ul.topic_words").each(function(i,ul) {
		$(ul).empty();
		_.each(words, function(w) {
			$("<li class='word'>"+w['word']+"</li>").appendTo(ul);
		});
	});
	////// BAKE DOCUMENTS
	var ul_documents = $(".theme_container").find("ul.documents");
	$(ul_documents).empty().removeClass("marker_active");
	_.each(docs, function(doc, i) {
		var title = doc['content']['title'];
		var fulltext = doc['content']['text'];
		var other_topics = doc['other_topics'];
		var lastSpaceIdx = fulltext.substring(0,1500).search(/ [^ ]*$/);
		var trimmedFulltext = fulltext.substring(0,lastSpaceIdx);
		var weight = Math.round(doc['weight']*100);
		var current_weight_base = 100;
		while(weight<=current_weight_base) {
			current_weight_base-=10;
			$("<div class='separation'>"+current_weight_base+"-"+(current_weight_base+10)+
				"% association to the theme</div>").appendTo("ul.document_list");
		}
		var doc_el = $("<li class='document' docID='"+topicID+"-"+i+"'>\
			<img class='marker_inconsistent' src='images/x.png'>\
			<div class='title'>"+title+"</div>\
			<div class='keyPhrase'></div>\
			<div class='fulltext'>"+trimmedFulltext+"</div>\
			<div class='relevancyScore'>"+weight+"% associated to this theme.</div>\
			<div class='otherTopics'></div>\
		</li>");
		$(ul_documents).append(doc_el);
	});

	/////// UPDATE NEXT THEME BUTTON TO SHOW PROGRESS
	if(currentTheme == themeData.length-1) {  // SHOW FINALIZE
		$("a.next_theme span").text("Finish");
	} else {
		$("a.next_theme span").text("Next theme ("+(currentTheme+1)+" of "+(themeData.length-1)+")");
	}
	
}




////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////

function openTutorial() {
	// POPULATE THEME WITH DEMO TOPIC DATA
	populateTheme(tutorialData);

	// TUTORIAL PAGE IS ALWAYS THE FIRST PAGE OF DEMO
	openPage("tutorial");	
}

function openTheme(topicNum) {
	// O/W OPEN A NEW THEME
	populateTheme(themeData[topicNum]);
	$(".topbar .top_title").text("Task : Theme "+(currentTheme+1));	

	// DISABLE THEME EDITING MODE
	$("div.words_wrapper").removeClass("hidden");
	$("div.editable_words_wrapper").addClass("hidden");
	// DISABLE MARKABLE DOCUMENTS
	$("ul.documents").removeClass("marker_active");
	$("img.marker_inconsistent").unbind();

}

function openPage(target) {
	$("div.page:visible").addClass("hidden");
	var page = $("div.page[pagetype='"+target+"']");
	$(page).removeClass("hidden");
	// $("div.page").hide();
	// setTimeout(function(){
	// 	$("div.page[pagetype='"+target+"']").show();
	// },500);

	// RESET INPUT AND TEXTAREA
	$(page).find("textarea,input").val("");
	$(page).find("input[type='radio']").prop('checked',false);
	$(page).find("input[v='3']").prop('checked',true);

	// HIDE SECTIONS AND NEXT THEME / PAGE BUTTON
	$(page).find("div.section").addClass("hidden");
	$(page).find(".next_theme, .next_page").addClass("hidden");
	$(page).find(".next_section").removeClass("hidden");

	// SPECIAL CASES.  
	// 1. INCONSISTENT ARTICLES
	if(target=="document-questions") {
		$("ul.documents").addClass("marker_active");
		$("img.marker_inconsistent").unbind();
		$("img.marker_inconsistent").click(function(event){
			$(this).toggleClass("checked");
			var docID = $(this).parents("li.document").attr("docID");
			var cur_val_list = $("input.answer_inconsistent_articles").val().trim().split(" ");
			if(_.indexOf(cur_val_list, docID)!=-1) {
				cur_val_list = _.without(cur_val_list,docID);
			} else {
				cur_val_list.push(docID)
			}
			$("input.answer_inconsistent_articles").val(cur_val_list.join(" "));
			console.log(cur_val_list);
			event.stopPropagation();
		});
	} else if(target=="correlation-questions") {
		// SHOW QUOTES FROM THEME AND DOCUMENTS MEANING
		$("span.theme_meaning").text($("textarea[role='theme_meaning']").val());
		$("span.document_meaning").text($("textarea[role='document_meaning']").val());
	} else if(target=="improving") {
		// TOPIC IMPROVING TASK
		$("div.words_wrapper").addClass("hidden");
		$("div.editable_words_wrapper").removeClass("hidden");
		// MARKING UNRELATED DOCUMENTS
		$("ul.documents").addClass("marker_active");
		$("img.marker_inconsistent").unbind();
		$("img.marker_inconsistent").click(function(event){
			$(this).toggleClass("checked");
			//var docID = $(this).parents("li.document").attr("docID");
			event.stopPropagation();
		});
		//initThemeEditor();
	} else {
		removeThemeEditor();
	}

	// OPEN THE FIRST SECTION
	openSection();

}
function openSection() {
	// WILL BE TRIGGERED WHEN A PAGE IS OPENEND OR CONTINUE BUTTON IS CLICKED
	// 0. REMOVE HIGHLIGHTS
	$(".castAura").removeClass("castAura");

	// 1. FIND CURRENTLY OPEN SECTION
	var current_page = $("div.page:visible");
	var invisible_sections = $(current_page).find("div.section.hidden");
	//var first_invisible_section = $(current_page).find("div.section.hidden").filter(":first");
	
	// 2. OPEN NEXT SECTION.  
	//	   case a. IF NEXT SECTION EXISTs, JUST OPEN IT
	if (invisible_sections.length>=1) {
		$(invisible_sections[0]).removeClass("hidden");
		// SPECIAL CASES: IF THERE's highlight attribute, then highlight the element.
		if($(invisible_sections[0]).attr("highlight")) {
			var div_to_highlight = $(invisible_sections[0]).attr("highlight");
			$(div_to_highlight).addClass("castAura");
		}
	}
	// if (invisible_sections.length==1) {
	// 	$(current_page).find(".next_section").addClass("hidden");
	// 	$(current_page).find(".next_theme, .next_page").removeClass("hidden");
	// }
	// 		case b. IF NO NEXT SECTION EXISTS, SHOW NEXT_THEME BUTTON
	if (invisible_sections.length==0) {
		$(current_page).find(".next_section").addClass("hidden");
		$(current_page).find(".next_theme, .next_page").removeClass("hidden");
	}

}

function validateSection() {
	var current_page = $("div.page:visible"); 	var current_page_type = $(current_page).attr("pagetype");
	var current_section = $(current_page).find("div.section:not(.hidden):last");
	if($(current_section).length==1) { 
		var cs = $(current_section).get(0);
		if(current_page_type=="tutorial" && $(cs).attr("secnum")==2) {
			// CHECKING THE FIRST TUTORIAL QUESTION OF FIDNING THE MOST FREQUENT TOPIC WORD
			console.log($(cs).find("textarea.mini_task").val());
			var correctAnswer = $("div.theme_container div.words_section ul.words li.word:first").text();
			if ($.trim(correctAnswer) == $.trim($(cs).find("textarea.mini_task").val())) {
				$(cs).find(".mini_feedback").html("That's a correct answer. Good job!");	
				return true;
			} else {
				$(cs).find(".mini_feedback").html("The correct answer is <b>"+correctAnswer+"</b>. The first and biggest word is the most common word in the theme.");	
				return true;
			} 
		} else if(current_page_type=="tutorial" && $(cs).attr("secnum")==3) {
			var correctAnswer = "THE WEEK AHEAD: Jan. 21 - 27; CLASSICAL";
			if ($.trim(correctAnswer) == $.trim($(cs).find("textarea.mini_task").val())) {
				$(cs).find(".mini_feedback").html("That's a correct answer. Good job!");	
				return true;
			} else {
				$(cs).find(".mini_feedback").html("The correct answer is <b>"+correctAnswer+"</b>. Hover the mouse over <i>music</i> in the theme. You will see 'Classical music often' is the phrase of the first article that contains the word 'music'.");	
				return true;
			} 
		} else if(current_page_type=="theme-questions" && $(cs).attr("secnum")==1) {
		// ASKING THEME_MEANING
			if ($.trim($(cs).find("textarea[role='theme_meaning']").val())=="") {
				alert("Please answer the question to proceed");
				return false;
			} else { return true;}
		}
	} else { // DO NOTHING
	}
	return true;
}

function extractResultFromUI() {
	// EXTRACT USER'S INPUT FOR ONE THEME FROM ALL THE PAGES
	var resultForTheme = {};
	$("textarea.answer").each(function(i,el) {
		var role = $(el).attr("role");  
		var textAnswer = $(el).val();  
		resultForTheme[role]=textAnswer;
	});
	$("input.answer").each(function(i,el) {
		var role = $(el).attr("role");  
		var textAnswer = $(el).val();  
		resultForTheme[role]=textAnswer;
	});
	$("ul.topic_words").each(function(i,el) {
		var role = $(el).attr("role");  
		var clickedWords = $(el).find("li.selected").map(function(i,el){return $(el).text();});
		resultForTheme[role]=$.makeArray(clickedWords);
	});
	resultForTheme["inconsistent_documents"] = $.makeArray($("input.answer_inconsistent_articles").val());
	resultForTheme["correlation"] = $("input[name='cor']:checked").attr('v');
	// EXTRACT DATA FROM MODIFIED THEME
	resultForTheme["modified_theme"] = $.makeArray($("ul.words li:not(.removed,.splitted)").map(function(i,el){
		return $(el).text();
	}));
	resultForTheme["theme_removed"] = $.makeArray($("ul.words li.removed").map(function(i,el){
		return $(el).text();
	}));
	resultForTheme["theme_splitted"] = $.makeArray($("ul.words li.splitted").map(function(i,el){
		return $(el).text();
	}));
	resultForTheme["documents_removed"] = $.makeArray($("ul.documents li.removed").map(function(i,el){
		return $(el).attr('docid');
	}));
	// PUSH THEME RESULT TO THE OVERALL RESULT
	result.push(resultForTheme);
}
function submitResult() {
	var data = {
		'result':JSON.stringify(result)
	};
	$.post("submitTurkerResult",data, function(res){
		$(".main_container").addClass("hidden");
		$(".final_feedback").html(res);
		//alert("Thank you! Submitted");
	});



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
	$(".fulltext").each(function(i,el) {
		$(el).html($(el).text());	// REMOVE SPAN TAGS
	});
	$("li.document").removeClass("showingKeyPhrase");
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
				// ALSO HIGHLIGHT THE WORD IN THE FULLTEXT
				text_with_highlight = fulltext.replace(w_reg_with_space_around, " <span class='keyword'>$2</span> "); 
				$(el).find(".fulltext").html(text_with_highlight);
			} 
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
	});

	// NEXT THEME BUTTON IS CLICKED FOR SHOWING NEW THEME
	$("a.next_theme").click(function() {
		if(currentTheme>0) extractResultFromUI();	// EXTRACT DATA FROM UI AND STORE IN VARIABLE
		openTheme(currentTheme); // INITIALIZE TASK INFORMATION AND THEME, ARTICLES
		openPage("theme-questions");	
	});	
	$("a.finalize_hit").click(function() {
		submitResult(); // FINALIZE
	});

	$("a.next_page").click(function() {
		// VALIDATE IF THERE'S NO EMPTY TEXTAREA
		var is_valid = true;
		$(this).parents(".page").find("textarea.required").each(function(i,el){
			if ($(el).val()=="") is_valid=false;
		});
		// if (!is_valid) {
		// 	alert("One or more textarea is still empty. Please fill in them before proceeding.");
		// 	return;
		// }
		openPage($(this).attr("target"));
	});
	$("a.next_section").click(function(event) {
		// var target = $(this).attr("target");
		// if(target=="next_page") $(this).parents("div.page").find("a.next_page").show();
		// else if(target=="next_theme") $(this).parents("div.page").find("a.next_theme").show(); 
		// else openSection($(this).parents("div.page").attr("pagetype"), parseInt(target));
		if (validateSection()){
			openSection();	
		}
	});

	// THEME AND DOCUMENTS HANDLERS
	$("ul.documents").on("click","li.document", function() {
		$(this).toggleClass("selected");
	});
	$("div.theme_container div.editable_words_section span.add_word").click(function(event){
		if($("div.ui_for_adding_words").hasClass("hidden")) {
			$("div.ui_for_adding_words").removeClass("hidden");
			$('body').off('click').on('click', function(event){ 
				if (!$(event.target).closest('div.ui_for_adding_words').length) {
	    			$("div.ui_for_adding_words").addClass("hidden");
					$('body').off('click');
	  			}
			});
			$("div.ui_for_adding_words input.text_to_be_added").focus();
		} else {
			$("div.ui_for_adding_words").addClass("hidden");
			$('body').off('click');
		}
		event.stopPropagation();
	});
	$("div.theme_container div.editable_words_section span.merge_word").click(function(event){
		if($("div.ui_for_merging_words").hasClass("hidden")) {
			$("div.ui_for_merging_words").removeClass("hidden");
			$('body').off('click').on('click', function(event){ 
				if (!$(event.target).closest('div.ui_for_merging_words').length) {
	    			$("div.ui_for_merging_words").addClass("hidden");
					$('body').off('click');
	  			}
			});
			var selected_words = $("ul.editable_words li.selected").map(function(i,el){
				return $(el).clone().children().remove().end().text();
			});
			$("div.ui_for_merging_words input.text_to_merge_to").val($.makeArray(selected_words).join(" "));
			$("div.ui_for_merging_words input.text_to_merge_to").focus();
			$("div.ui_for_merging_words input.text_to_merge_to").select();
		} else {
			$("div.ui_for_merging_words").addClass("hidden");
			$('body').off('click');
		}
		event.stopPropagation();
	});
	// QUESTION HANDLERS
	$("div.page ul.topic_words").on("click","li.word", function() {
		$(this).toggleClass("selected");
	});


	// THEME EDITING TOOLS HANDLERS
	$("input.text_to_be_added").keypress(function(e) {
		if(e.which == 13) { 	
			if(addWord($(this).val())) {
				$(this).val("");	
			}
		}
	});
	$("input.text_to_merge_to").keypress(function(e) {
		if(e.which == 13) { 	
			mergeSelectedWords($(this).val());	
			$(this).val("").blur();	
			update_ui_for_word_selection();
		}
	});
	$(".remove_words").click(function() {   removeSelectedWords(); });
	$(".split_words").click(function() {   splitSelectedWords(); });
	$("a.revert_changes").click(function() {   
		populateTheme(themeData[currentTheme]);
		initThemeEditor(); 
	});


	// $("button.next").click(function() {
	// 	$(this).parents(".refining_stage").find("input, textarea").attr("disabled","disabled");
	// 	$(".refining_stage:visible").hide();
	// 	var targetStage = $(this).attr("targetstage");
	// 	if (targetStage=="2") {
	// 		$(".turk_task:visible").find(".doc_rep").show();
	// 	}
	// 	$(this).parents(".refining_tool").find(".refining_stage[stage='"+targetStage+"']").show();
	// 	$(this).hide();
	// });

	$("a.topic_add_words").click(function() {
		$(this).parent().find(".dummy_new_words").addClass("hidden");
		$(this).parent().find("input.topic_add_words").removeClass("hidden");;
	});

	// $(window).resize(resizeDocumentPadding);


	// $(".theme_container").scroll(function() {
	// 	console.log($(this).scrollTop());
	// 	if($(this).scrollTop()>106) {
	// 		$("div.words_section").css("position","fixed");
	// 		$("div.words_section").css("top","0");
	// 	} else {
	// 		$("div.words_section").css("position","relative");
	// 	}
	// });

	// DOCUMENT RELATED EVENT HANDLING

	$("li.doc_item").click(function() {
		$(this).toggleClass("zoomed");

	});

	// SHOWING HINTS FOR THEME IMPROVING TOOLS
	$("div.page span.hint").hover(function() {
		var target_selector = $(this).attr("target");
		var target_el = $(target_selector);
		if($(target_el).length>0) {
			$(target_el).css("border","1px solid #f00");
		}
	},function(){
		var target_selector = $(this).attr("target");
		var target_el = $(target_selector);
		if($(target_el).length>0) {
			$(target_el).css("border","");
		}
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
	$("button.dummy_shortcut").click(function() {
		$("a.participate_button").trigger("click");
		openPage("improving");
	});
	

	// SET AUTO-RESIZE TEXTAREA
	$.each($('textarea[data-autoresize]'), function() {
	    var offset = this.offsetHeight - this.clientHeight;
	    var resizeTextarea = function(el) {
	        $(el).css('height', 'auto').css('height', el.scrollHeight + offset);
	    };
	    $(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
	});

	// HIDE ELEMENTS NOT READY
	//$("div.page").hide();
	//$("div.page[pagetype='tutorial']").show();

	currentTheme = 0;
	result = [];
	//ALPHABET = "abcdefghijklmnopqrstuvwxyz";

	// RETRIEVE THEME DATA FROM SERVER
	retrieveThemes();


});