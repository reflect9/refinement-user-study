

//////////////////////////////////////////////////////////////////
///  THEME EDITOR FUNCTIONS
//////////////////////////////////////////////////////////////////
function addWord(html) {
	// CHECKING WHETHER THE WORD ALREADY EXISTS
	var new_word_text = text_only($("<li class='word'>"+html+"</li>"));
	var existing_word_with_same_text = $(".theme_container div.words_section ul.words li.word")
		.filter(function(i,el){ 
			return $(el).text_without_children()==new_word_text; 
		});
	if(existing_word_with_same_text.length>0) {
		alert(new_word_text+" alrealy exists in the theme.");
		return false;
	}
	// CREATING WORD
	$("<li class='word'>"+html+"</li>")
		.appendTo(".theme_container div.words_section ul.words")
		.css({"background-color":"#aaa"})
		.animate({"background-color":"white"},1500, 
			function(){ $(this).css("background-color",""); });
}
function removeWord(text) {
	$(".theme_container div.words_section ul.words li.word")
		.filter(function(i,el){ 
			return $(el).text_without_children()==text; 
		}).remove();
}
function mergeWord(targetEl,newText) {
	if(targetEl.length==0) { alert("You must select multiple words first."); return; }
	_.each(targetEl, function(t){ removeWord($(t).text_without_children()); });
	// IF IT IS SIMPLY JOINING TARGET, THEN DO NOT SHOW WHAT MERGED WORDS ARE. 
	addWord(newText + "<span class='sub_words'>"+$.makeArray($(targetEl).map(function(i,el){return $(el).html();})).join(", ")+"</span>");
}
function text_only(el) {
	return $(el).text_without_children();
}
// UNDO RELATED STUFF
function pushCurrentStateToHistory(desc, ul_words_backup) {
	var words = (typeof ul_words_backup=="undefined")? $(".theme_container div.words_section ul.words").clone() : ul_words_backup;
	stateHistory.push({
		"mode": $(".theme_container div.words_section").attr("mode"),
		"message": desc,
		"words": words,
		"documents": $.makeArray($("div.documents_section ul.documents li.document").map(function(i,li){return $(li).hasClass("removed")==false;})),
		"splittedTheme": $(splittedTheme).clone()
	});
	// UPDATE UNDO BUTTON TEXT
	if (stateHistory.length>0) {
		$("button.undo").text("Undo "+stateHistory[stateHistory.length-1]["message"]);	
	} else $("button.undo").text("Nothing to undo");
	//
	console.log(_.map(stateHistory,function(s){return s['message'];}));
}
function revertToTheLatestState() {
	disableEditing();
	console.log(_.map(stateHistory,function(s){return s['message'];}));
	var state_to_restore = stateHistory.pop();
	// var state_to_restore = stateHistory[stateHistory.length-1];
	if(typeof state_to_restore=="undefined") return;
	$("div.theme_container div.words_section ul.words").replaceWith(state_to_restore["words"]);
	// CLEAN UP SOME CSS AND CLASS
	$("div.theme_container div.words_section ul.words li.word")
		.css("z-index","").css("background-color","")
		.removeClass("selected").removeClass("splitted").removeClass("temporary").removeClass("removed");
	$("div.theme_container div.documents_section ul.documents li.document").each(function(i,el){
		if(state_to_restore["documents"][i]==true) { 
			$(el).removeClass("removed");  
			$(el).find(".marker_inconsistent").removeClass("checked");
		} else {
			$(el).addClass("removed");  
			$(el).find(".marker_inconsistent").addClass("checked");
		}
	});
	splittedTheme = state_to_restore["splittedTheme"];
	// UPDATE UNDO BUTTON TEXT
	if (stateHistory.length>0) {
		$("button.undo").text("Undo "+ stateHistory[stateHistory.length-1]["message"]);	
	} else $("button.undo").text("Nothing to undo");

	// ADD LOG
	addLog("UNDO",state_to_restore["message"]);
}


// EDITING MODE RELATED STUFF
function disableEditing(cur_mode) {
	// WHAT IS THE CURRENT EDITING MODE?
	cur_mode = (typeof cur_mode=="undefined") ? $(".theme_container div.words_section").attr("mode"): cur_mode;
	switch(cur_mode) {
		case "add_words":
			$(".theme_container div.words_section ul.words li.word.temporary").removeClass("temporary");
			$(".theme_container div.words_section ul.words li.word").unbind("click");
			break;
		case "remove_words":
			$(".theme_container div.words_section ul.words li.word.removed").remove();
			$(".theme_container div.words_section ul.words li.word").unbind("click");
			break;
		case "merge_words":
			$(".theme_container div.words_section ul.words li.word").unbind("click");
			$(".theme_container div.words_section ul.words li.word.temporary").removeClass("temporary");
			$(".theme_container div.words_section ul.words li.word.selected").removeClass("selected");
			break;
		case "change_word_order":
			// DESTROY DRAGGABLE
			$(".theme_container div.words_section ul.words li.word.temporary").removeClass("temporary");
			$(".theme_container div.words_section ul.words").sortable("destroy");
			// TBD
			break;
		case "remove_articles":
			$("div.documents_section ul.documents img.marker_inconsistent").unbind("click");
			$("div.documents_section ul.documents").removeClass("marker_active");
			// 
			break;
		case "split_theme":
			splittedTheme = $("ul.words_for_splitting").clone();
			$(".theme_container div.words_section ul.words li.word.selected").removeClass("selected");
			$(".theme_container div.words_section ul.words li.word").draggable("destroy");
			break;
		case "other_ideas":
			break;
		default:
			break;
	}
	$("div.page:visible ul.edit_tools li.active").removeClass("active",300);
	$(".theme_container div.edit_ui").remove();
	$(".theme_container div.words_section").attr("mode","");
			
}
function enableEditing(mode, isPractice) {
	switch(mode) {
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////
		case "add_words":
			var el = $("<div class='edit_ui add_words clearfix'>\
				<span class='tool_inst'>Type a word to add, and press Enter:</span>\
				<input type='text' class='text_to_be_added'>\
			</class>");
			// INPUT BOX HANDLER
			$(el).find("input.text_to_be_added").keydown(function(e){
				if(e.keyCode == 13 && $(this).val()!="") {
					var word_to_add = $(this).val();
					if (isPractice) pushCurrentStateToHistory("adding \""+word_to_add+"\"");
					addWord(word_to_add);		$(this).val("");
					addLog("ADD_WORDS",word_to_add);
					if(isPractice) validateSection();
				}
			});
			$(el).appendTo("div.words_section");
			$(el).find("input.text_to_be_added").focus();
			break;
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////	
		case "remove_words":
			var el = $("<div class='edit_ui remove_words clearfix'>\
				<span class='tool_inst'>To remove a word, click the icon left to it.</span>\
			</class>");
			// ATTACH CLICK EVENT HANDLER TO EXISTING WORDS
			$(".theme_container div.words_section ul.words li.word").click(function() {
				pushCurrentStateToHistory("removing \""+$(this).text_without_children()+"\"");
				$(this).hide(1000,function(){
					var textToDelete = $(this).text_without_children();
					removeWord(textToDelete);	
					addLog("REMOVE_WORDS",textToDelete);
					if(isPractice) validateSection();
				});
			});
			$(el).appendTo("div.words_section");
			break;
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////	
		case "merge_words":
			var el = $("<div class='edit_ui merge_words clearfix'>\
				<span class='tool_inst'>(1) Click words to merge, (2) Type a new word and press Enter.</span><br>\
				<ul class='words_for_merging'></ul> will be merged to \
				<input type='text' class='text_to_merge_to' placeholder='a new word'>\
			</class>");
			// CLICK EVENT HANDLER FOR EXISTING WORDS
			$(".theme_container div.words_section ul.words li.word").click(function() {
				$(this).toggleClass("selected");
				var text_selected = $(this).text_without_children();
				// REMOVE IF THE WORD EXISTS, O/W ADD WORD
				var word_already_selected = $("div.edit_ui ul.words_for_merging li").filter(function(i,li){return $(li).text_without_children()==text_selected;});
				if($(word_already_selected).length>0) $(word_already_selected).remove();
				else {
					$("<li>"+$(this).html()+"</li>").appendTo("div.edit_ui ul.words_for_merging");
				}
			});
			$(el).find("input.text_to_merge_to").keydown(function(e){
				if(e.keyCode == 13) {
					if($(this).val()!="") {
						var el_to_be_merged = $("div.edit_ui ul.words_for_merging li");
						var text_to_be_merged = $.makeArray($("div.edit_ui ul.words_for_merging li").map(function(i,el){ return $(el).text_with_gap(); })).join(",");
						var new_word = $(this).val();
						pushCurrentStateToHistory("merging words to "+new_word);
						mergeWord(el_to_be_merged, new_word);
						addLog("MERGE_WORDS",text_to_be_merged + "->" + new_word);
						$(this).val("");
						$("div.edit_ui ul.words_for_merging li").remove();
						////// REASSIGN CLICK EVENt HANDLERS FOR THE WORDS
						$(".theme_container div.words_section ul.words li.word").unbind("click").click(function() {
							$(this).toggleClass("selected");
							var text_selected = $(this).text_without_children();
							// REMOVE IF THE WORD EXISTS, O/W ADD WORD
							var word_already_selected = $("div.edit_ui ul.words_for_merging li").filter(function(i,li){return $(li).text_without_children()==text_selected;});
							if($(word_already_selected).length>0) $(word_already_selected).remove();
							else {
								$("<li>"+$(this).html()+"</li>").appendTo("div.edit_ui ul.words_for_merging");
							}
						});
						////////
						if(isPractice) validateSection();
					} else {
						alert("Try again after typing a new word in the input box.");
						// $(this).parents("div.edit_ui").find("span.simple_feedback").text("Type ");
					}
				}
			});
			$(el).appendTo("div.words_section");
			break;
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////	
		case "change_word_order":
			var el = $("<div class='edit_ui change_word_order clearfix'>\
				<span class='tool_inst'>Drag words to change their order.</span>\
			</class>");
			// MAKING WORDS DRAGGABLE
			var words_el = $(".theme_container div.words_section ul.words");
			temp_ul_words = $(".theme_container div.words_section ul.words").clone();
			$(words_el).sortable({	
				appendTo:"body",
				update:function(event,ui){
					var movedWord = $(ui.item).text_without_children();
					pushCurrentStateToHistory("changing position of \""+movedWord+"\"", temp_ul_words);
					addLog("CHANGE_WORD_ORDER",movedWord);
					if(isPractice) validateSection();
					temp_ul_words = $(".theme_container div.words_section ul.words").clone();
				}
			});
			$(words_el).disableSelection();
			$(el).appendTo("div.words_section");
			break;
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////	
		case "split_theme":
			var el = $("<div class='edit_ui split_theme clearfix'>\
				<span class='tool_inst'>Drag words into the box below to split them into a new theme.</span><br>\
				<ul class='words_for_splitting'></ul>\
			");
			// RESUME EXISTING SPLIT BUCKET
			if (typeof splittedTheme!=="undefined" && $(splittedTheme).length>0) {
				$(el).find("ul.words_for_splitting").replaceWith(splittedTheme);
				$(el).find("ul.words_for_splitting li").mousedown(function(){
					pushCurrentStateToHistory("returning \""+$(this).text_without_children()+"\"");
					$(this).unbind("mousedown").appendTo(".theme_container div.words_section ul.words");
					$(".theme_container div.words_section ul.words li.word").draggable("destroy");
					$(".theme_container div.words_section ul.words li.word").draggable( { revert:"invalid" } );
					temp_ul_words = $(".theme_container div.words_section ul.words").clone();
				});		
			}
			// MAKE DRAGGABLE BUCKETS
			temp_ul_words = $(".theme_container div.words_section ul.words").clone();
			$(".theme_container div.words_section ul.words li.word").draggable( { revert:"invalid" } );
			$(el).find("ul.words_for_splitting").droppable({
				accept: "li.word",
				drop:function(event,ui) {
					console.log("dropped");
					var split_word = $(ui.draggable).text_without_children();
					pushCurrentStateToHistory("splitting \""+split_word+"\"", temp_ul_words);
					addLog("SPLIT_THEME",split_word);
					$(ui.draggable)
						.css("position","").css("top","").css("left","")
						.mousedown(function() {
							// RETURN TO THE WORD
							pushCurrentStateToHistory("returning \""+$(this).text_without_children()+"\"");
							addLog("UN_SPLIT_THEME",$(this).text_without_children());
							$(this).unbind("mousedown").appendTo(".theme_container div.words_section ul.words");
							$(".theme_container div.words_section ul.words li.word").draggable("destroy");
							$(".theme_container div.words_section ul.words li.word").draggable( { revert:"invalid" } );
							temp_ul_words = $(".theme_container div.words_section ul.words").clone();
						})
						.appendTo(this);
						if(isPractice) validateSection();
						temp_ul_words = $(".theme_container div.words_section ul.words").clone();
				}
			});
			$(el).appendTo("div.words_section");
			break;
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////	
		/////////////////////////////////////////////////////////////////////////////////////
		/////////////////////////////////////////////////////////////////////////////////////	
		case "remove_articles":
			var el = $("<div class='edit_ui remove_documents clearfix'>\
				<span class='tool_inst'>Click <img class='marker_inconsistent' src='images/x-rect.png'> of articles to remove .</span>\
			</class>");
			// ACTIVATE DOCUMENT MARKER 
			$("div.documents_section ul.documents").addClass("marker_active");
			$("div.documents_section ul.documents img.marker_inconsistent").click(function(event){
				pushCurrentStateToHistory("removing articles");
				addLog("REMOVE_ARTICLES",$(this).parents("li.document").attr("docid"));
				$(this).toggleClass("checked");
				$(this).parents("li.document").toggleClass("removed");
				if(isPractice) validateSection();
				event.stopPropagation();
			});
			// UPDATE MARKER STATE
			$("div.documents_section ul.documents li.document.removed").find("img.marker_inconsistent").addClass("checked");
			$("div.documents_section ul.documents li.document:not(.removed)").find("img.marker_inconsistent").removeClass("checked");
			$(el).prependTo("div.documents_section");
			break;
		case "other_ideas":
		default:
			break;
	}
	$(".theme_container div.words_section").attr("mode",mode);
}

function retrieveThemes() {
	$.get("retrieveThemeData",function(data) {
		d = JSON.parse(data);
		themeData = _.values(d["topics"]);
		tutorialData = d["tutorial"];
		console.log("data loaded");
		$("a.participate_button").text("Participate");
		$("a.participate_button").removeClass("hidden");
	});
}
function populateTheme(data) {
	////// INITIALIZE SPLITTED THEME DATA
	stateHistory = [];
	evaluation_before = []; evaluation_after = [];
	$("button.undo").text("Undo the latest refinement");
	splittedTheme = $("");
	/////
	var topicID = parseInt(data['tid']);
	var words = data['words'].slice(0,20);
	var additional_words = data['words'].slice(20,40);
	var docs = data['documents'];
	////// WORDS FOR MAIN THEME
	$(".theme_container").attr("tid",topicID);
	var ul_words = $(".theme_container").find("ul.words");
	$(ul_words).empty();
	_.each(words, function(w) {
		$("<li class='word noselect'>"+w['word']+"</li>")
			.css("font-size",15+(w['freq']/200))
			.appendTo(ul_words);
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
		// MARKING fulltext with theme words
		var markedHTML = trimmedFulltext;
		_.each(words, function(w) {
			// console.log(w);
			// console.log(markedHTML);
			var w_reg_with_space_around = new RegExp("([^a-zA-Z\>\<]|^)("+w['word']+")[^a-zA-Z\<\>]", 'ig');
			markedHTML = markedHTML.replace(w_reg_with_space_around," <em>$2</em> " );
		});
		// CALCULATING TOPIC DISTRIBUTION FOR EACH DOC
		while(weight<=current_weight_base) {
			current_weight_base-=10;
			$("<div class='separation'>"+current_weight_base+"-"+(current_weight_base+10)+
				"% association to the theme</div>").appendTo("ul.document_list");
		}
		var doc_el = $("<li class='document' docID='"+topicID+"-"+i+"'>\
			<img class='marker_inconsistent' src='images/x-rect-bl.png'>\
			<div class='title'>"+title+"</div>\
			<div class='keyPhrase'></div>\
			<div class='fulltext'>"+markedHTML+"</div>\
			<div class='relevancyScore'>"+weight+"% associated to this theme.</div>\
			<div class='otherTopics'></div>\
		</li>");
		$(ul_documents).append(doc_el);
	});

	/////// UPDATE NEXT THEME BUTTON TO SHOW PROGRESS
	// if(currentTheme == themeData.length-1) {  // SHOW FINALIZE
	// 	$("a.next_theme span").text("Finish");
	// } else {
	// 	$("a.next_theme span").text("Next theme ("+(currentTheme+1)+" of "+(themeData.length-1)+")");
	// }
	
}

function openTutorial() {
	populateTheme(tutorialData);
	openPage("intro");	
}
function openTheme(topicNum) {
	// HIDE MAIN COMPONENTS AND SHOW LOADING MESSAGE
	$("div.main_container").hide();
	$("<div class='loading'>Loading the next theme</div>").appendTo("body")
	.toggleClass("dimmed",1000).toggleClass("dimmed",1000)
	.queue(function() {
		$("div.loading").remove();
		$("div.main_container").show("fade");
		populateTheme(themeData[topicNum]);
		$(".topbar .top_title").text("Theme "+(currentTheme+1)+" out of 3");	
		openPage("task-intro");
	});
}
function openPage(target) {
	disableEditing();
	$("div.page:visible").addClass("hidden");
	var page = $("div.page[pagetype='"+target+"']");
	///// CLEAN UP ALL THE INPUT AND TEXTAREA
	$(page).find("textarea, input").val("");
	$(page).find("input[type='radio']").prop('checked',false);
	/////
	$(page).removeClass("hidden");
	addLog("OPEN_PAGE",target);
	// if(target=="theme-questions") {
	// 	$(page).find("input[v='3']").prop('checked',true);	
	// }
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
		// SPECIAL CASE:  HIDE NEXT BUTTON IF IT's ABOUT PRACTICING TOOL USAGE
		if($(section_to_show).find("div.tool_practice_detail").length>0) {
			$(section_to_show).parents(".page").find(".next_section").addClass("hidden");
		}
	}
	// IF NO NEXT SECTION EXISTS, SHOW NEXT_THEME BUTTON
	else if (invisible_sections.length==0) {
		$(current_page).find(".next_theme, .next_page, .finalize_hit").trigger("click");
	}
	////// SPECIAL CASES
	/// OPENING TOOLS FOR PRACTICE
	var target = $(section_to_show).attr("sectionID");
	if(target=="read_over_the_theme" || target=="explore_articles") {
		$(section_to_show).parents(".page").find(".next_section").addClass("hidden");
	}
	////////  ADD WORDS FOR SPLITTING THEME
	if(target=="split_theme") { 	
		_.each(["pasta","olive","fish"], function(w) {
			$("<li class='word'>"+w+"</li>").appendTo("div.theme_container div.words_section ul.words");
		});  
	}
	if(target=="remove_words") { 	
		_.each(["york","west"], function(w) {
			if ($("div.theme_container div.words_section ul.words li.word").filter(function(i,li){return $(li).text()==w; }).length==0) {
				$("<li class='word'>"+w+"</li>").appendTo("div.theme_container div.words_section ul.words");	
			}
		});  
	}
	if(target=="change_word_order") { 	
		_.each(["concert"], function(w) {
			if ($("div.theme_container div.words_section ul.words li.word").filter(function(i,li){return $(li).text()==w; }).length==0) {
				$("<li class='word'>"+w+"</li>").appendTo("div.theme_container div.words_section ul.words");	
			}
		});  
	}
	if(target=="add_words" || target=="remove_words" || target=="merge_words" || target=="change_word_order" || target=="split_theme" || target=="remove_articles"){
		enableEditing(target.replace("practice_",""),true);
	}
	if(target=="eval_after_improvements") {
		// TELL WHAT WAS THE USER'S EVALUATION FOR THE ORIGINAL THEME AND ARTICLES
		var original_likert_el = $("div.section[sectionid='likert_evaluation']");
		var theme_clarity = $(original_likert_el).find("input[name='theme_clarity']:checked").parents(".likert_point").text();
		var article_consistency = $(original_likert_el).find("input[name='article_consistency']:checked").parents(".likert_point").text();
		var correlation = $(original_likert_el).find("input[name='correlation']:checked").parents(".likert_point").text();
		var improved_likert_el = $("div.section[sectionID='eval_after_improvements']");
		$(improved_likert_el).find("div.likert_chart[name='theme_clarity'] div.tiny_notice span").text(theme_clarity);
		$(improved_likert_el).find("div.likert_chart[name='article_consistency'] div.tiny_notice span").text(article_consistency);
		$(improved_likert_el).find("div.likert_chart[name='correlation'] div.tiny_notice span").text(correlation);
	}
}

function validateSection() {
	var current_page = $("div.page:visible"); 	var current_page_type = $(current_page).attr("pagetype");
	var current_section = $(current_page).find("div.section:not(.hidden):last");
	var html_goodjob = "<b>Good job!</b> Let's move on to the next practice.";
	var html_badjob = "<b>Try again.</b> You can proceed after completing the task above.";
	if($(current_section).length==1) { 
		var cs = $(current_section).get(0);
		if(current_page_type=="intro" && $(cs).attr("sectionID")=="read_over_the_theme") {
			// CHECKING THE FIRST TUTORIAL QUESTION OF FIDNING THE MOST FREQUENT TOPIC WORD
			console.log($(cs).find("textarea.mini_task").val());
			var correctAnswer = $("div.theme_container div.words_section ul.words li.word:first").text();
			if ($.trim(correctAnswer).toLowerCase() == $.trim($(cs).find("textarea.mini_task").val().toLowerCase())) {
				$(cs).find(".mini_feedback").html("That's correct! The first and biggest word is the most common word in the theme.");	
				return true;
			} else {
				$(cs).find(".mini_feedback").html("Try again. The first and biggest word is the most common word in the theme.");	
				return false;
			} 
		} else if(current_page_type=="intro" && $(cs).attr("sectionID")=="explore_articles") {
			var correctAnswer = "a season";
			var answer = $.trim($(cs).find("textarea.mini_task").val().toLowerCase()); 
			if (answer.indexOf(correctAnswer) != -1) {
				$(cs).find(".mini_feedback").html("That's correct!");	
				return true;
			} else {
				$(cs).find(".mini_feedback").html("Try again. Hover the mouse over <i>ballet</i> in the theme, and find the article that contains 'City Ballet opened'.");	
				return false;
			} 
		// PRACTICE 
		} else if($(current_section).attr("sectionID")=="add_words") {
			// CHECK ADD_WORDS RESULT : CHECKING classical and program in the THEME WORDS
			var words = $.map($("div.theme_container div.words_section ul.words li.word"),function(li,i){
				return $(li).text();
			});
			if(_.contains(words,"classical")) { 
				$(current_section).find(".tool_practice_result").addClass("correct").html(html_goodjob).css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
			}
			else {  
				$(current_section).find(".tool_practice_result").html(html_badjob).css("background-color","#f69256").animate({"background-color":"#fff"},500);;
				//alert("Two words are not in the theme. Make sure that you added both, and confirmed the change.");
			}
		} else if($(current_section).attr("sectionID")=="remove_words") {
			// CHECK REMOVE_WORDS RESULT : CHECKING york is still in the THEME WORDS
			var words = $.map($("div.theme_container div.words_section ul.words li.word"),function(li,i){ return $(li).text(); });
			if(!_.contains(words,"york") && !_.contains(words,"west")) { 
				$(current_section).find(".tool_practice_result").addClass("correct").html(html_goodjob).css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
			} else { 
				$(current_section).find(".tool_practice_result").html(html_badjob).css("background-color","#f69256").animate({"background-color":"#fff"},500);
				//alert("The word 'york' or 'west' is still in the theme. Make sure the word is crossed and you confirmed the change.");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="merge_words") {
			// CHECK MERGE_WORDS RESULT : CHECKING SONG AND SONGS
			var words = $.map($("div.theme_container div.words_section ul.words li.word"),function(li,i){ return $(li).text(); });
			if(!_.contains(words,"opera") && !_.contains(words,"jazz") && !_.contains(words,"rock") 
				&& _.filter(words,function(ww){return ww.indexOf("genre")!=-1;}).length>0 ) { 
				$(current_section).find(".tool_practice_result").addClass("correct").html(html_goodjob).css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
			} else { 
				$(current_section).find(".tool_practice_result").html(html_badjob).css("background-color","#f69256").animate({"background-color":"#fff"},500);
				//alert("Make sure that song and songs are not in the theme, and song(s) is in.");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="change_word_order") {
			// CHECK WORD_ORDER RESULT : CHECKING WHETHER CONCERT IS AT FRONT
			var words = $.map($("div.theme_container div.words_section ul.words li.word"),function(li,i){ return $(li).text(); });
			if(words[0]=="concert") { 
				$(current_section).find(".tool_practice_result").addClass("correct").html(html_goodjob).css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
			} else { 
				$(current_section).find(".tool_practice_result").html(html_badjob).css("background-color","#f69256").animate({"background-color":"#fff"},500);
				//alert("Make sure that concert is at front of the theme, and you confirmed the changes.");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="split_theme") {
			// CHECK SPLIT_THEME RESULT : CHECKING WHETHER PASTA, OLIVE and FISH ARE there
			var words = $.map($("div.theme_container ul.words_for_splitting li"),function(li,i){ return $(li).text(); });
			if(_.contains(words,"pasta") && _.contains(words,"olive") && _.contains(words,"fish")) {
				$(current_section).find(".tool_practice_result").addClass("correct").html(html_goodjob).css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
			} else { 
				$(current_section).find(".tool_practice_result").html(html_badjob).css("background-color","#f69256").animate({"background-color":"#fff"},500);
				//alert("Make sure that pasta, oil, and fish are not in the theme.");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="remove_articles") {
			// CHECK REMOVE_ARTICLES RESULT : CHECKING WHETHER "ASKING TOO MUCH" IS STILL IN THE ARTICLES
			var title = $("div.theme_container div.documents_section ul.documents li.document.removed div.title")
				.filter(function(i,el){ return $(el).text()=="Asking Too Much"; });
			if($(title).length==1) { 
				$(current_section).find(".tool_practice_result").addClass("correct").html(html_goodjob).css("background-color","#00b3ca").animate({"background-color":"#fff"},500);
				$("div.page:visible a.next_section").removeClass("hidden");
				$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
			} else { 
				$(current_section).find(".tool_practice_result").html(html_badjob).css("background-color","#f69256").animate({"background-color":"#fff"},500);
				//alert("Make sure that the article 'Asking Too Much' is marked to be removed, and you clicked 'Apply this change' button.");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="meaning_of_the_theme") {
			// ASKING THEME_MEANING
			if ($.trim($(cs).find("textarea[role='theme_meaning']").val())=="") {
				alert("Please answer the question to proceed");
				return false;
			} else { return true;}
		} else if($(current_section).attr("sectionID")=="likert_evaluation") { 
			var checkedInputs = $(current_section).find("input:checked");
			if($(checkedInputs).length==3) {
				evaluation_before = $.makeArray($(checkedInputs).map(function(i,el){return $(el).attr("v");}));
				return true;
			} else {
				alert("Please answer all the questions to proceed");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="eval_after_improvements") {
			var checkedInputs = $(current_section).find("input:checked");
			if($(checkedInputs).length==3) {
				evaluation_after = $.makeArray($(checkedInputs).map(function(i,el){return $(el).attr("v");}));
				return true;
			} else {
				alert("Please answer all the questions to proceed");
				return false;
			}
		} else if($(current_section).attr("sectionID")=="eval_tools") {
			// EVALUATION AFTER IMPROVEMENTS
			if($(current_section).find("input:checked").length!=6) {
				alert("Please answer all the questions to proceed");
				return false;
			} else { return true; }
		} 
	} else { // DO NOTHING
	}
	return true;
}

function extractResultFromUI() {
	// EXTRACT USER'S INPUT FOR ONE THEME FROM ALL THE PAGES
	var resultForTheme = {"tid":$("div.theme_container").attr("tid")  };
	///// THEME MEANING
	resultForTheme["theme_meaning"] = $("div.page[pagetype='theme-questions'] textarea[role='theme_meaning']").val();
	///// IMPROVED THEME AND ARTCLES
	resultForTheme["improved_theme"]=$.makeArray($("div.theme_container div.words_section ul.words li.word").map(function(i,li){return $(li).text_with_gap();}));   
	resultForTheme["improved_articles"]=$.makeArray($("div.documents_section ul.documents li.document").map(function(i,li){return $(li).hasClass("removed")==false;}));
	///// LOG DATA
	resultForTheme["log"]=JSON.parse(JSON.stringify(log));  // DEEP COPY LOG OBJECT
	///// EVALUATION OF THEME AND ARTICLES BEFORE IMPROVEMENT
	resultForTheme["evaluation_before"]=evaluation_before;
	///// EVALUATION OF AFTER 
	resultForTheme["evaluation_after"]=evaluation_after;
	
	// PUSH THEME RESULT TO THE OVERALL RESULT
	result["topics"].push(resultForTheme);
}
function submitResult() {
	///// EXTRACTING FROM CLOSING SURVEY
	var eval_tools = {};
	$("table.table_tool_eval tbody tr").each(function(i,tr){
		var tid = $(tr).attr("toolID");
		var checked_value = $(tr).find("input:checked").attr("v");
		eval_tools[tid]=checked_value;
	});
	result["general"]["eval_tools"]=eval_tools;
	result["general"]["other_idea"] = $("div.section[sectionID='other_ideas'] textarea[role='other_refinements']").val();
	///// SUBMISSION 
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
////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////
$(document).ready(function() {

	/////////////////  SHUFFLE REFINEMENTS
	tool_order = shuffle(["add_words","remove_words","merge_words","change_word_order","split_theme","remove_articles"]);
	$("div.information_container div.page[pagetype='practice'] div.section.practice").sort(function(a,b) {
		return tool_order.indexOf($(a).attr("sectionID")) > tool_order.indexOf($(b).attr("sectionID"));
	}).each(function() {
		var el = $(this);
		el.remove();
		$(el).insertBefore("div.information_container div.page[pagetype='practice'] div.section.outro");
	});
	$("ul.edit_tools li").sort(function(a,b) {
		return tool_order.indexOf($(a).attr("toolID")) > tool_order.indexOf($(b).attr("toolID"));
	}).each(function() {
		var el = $(this);
		el.remove();
		$(el).appendTo("ul.edit_tools");
	});
	$("table.table_tool_eval tbody tr").sort(function(a,b) {
		return tool_order.indexOf($(a).attr("toolID")) > tool_order.indexOf($(b).attr("toolID"));
	}).each(function() {
		var el = $(this);
		el.remove();
		$(el).appendTo("table.table_tool_eval tbody");
	});



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
		if(currentTheme==3) {
			openPage("closing-survey");
		} else {
			openTheme(currentTheme); // INITIALIZE TASK INFORMATION AND THEME, ARTICLES
			addLog("OPEN_THEME",currentTheme);	
		}
		
		// openPage("theme-questions");	
	});	
	$("a.finalize_hit").click(function() {
		addLog("FINALIZE");
		submitResult(); // FINALIZE
	});

	$("a.next_page").click(function() {
		// VALIDATE IF THERE'S NO EMPTY TEXTAREA
		var is_valid = true;
		$(this).parents(".page").find("textarea.required").each(function(i,el){
			if ($(el).val()=="") is_valid=false;
		});
		var pageType = ($(this).attr("target")==undefined)? $(this).parents("div.page").next("div.page").attr("pagetype") : $(this).attr("target");
		openPage(pageType);
	});
	$("a.next_section").click(function(event) {
		var conf = true;
		if($(this).hasClass("require_confirmation")) {
			var conf = confirm("Are you sure you are done improving?");
		}
		if (conf && validateSection()){
			disableEditing();
			openSection();
			$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
		}
	});

	// THEME AND DOCUMENTS HANDLERS
	$("ul.documents").on("click","li.document", function() {
		$(this).toggleClass("selected",500);
		addLog("TOGGLE_DOCUMENT",$(this).attr("docid"));
	});
	$("div.theme_container div.words_section").on("mouseenter","ul.words li.word",function(){
		focusWord($(this).text_without_children(),true);
		event.stopPropagation();
	});
	$("div.theme_container div.words_section").on("mouseleave","ul.words li.word",function(){
		focusWord($(this).text_without_children(),false);
		event.stopPropagation();
	});
	// EDITING TOOLS HANDLER
	$("ul.edit_tools li").click(function() {
		// TOOL VISIBILITY CONTROL
		$(this).parents("ul.edit_tools").find("li").not(this).removeClass("active",300);
		$(this).toggleClass("active",300);
		// ENABLE DISABLE TOOL UI IF 
		disableEditing();
		enableEditing($(this).attr("class"));
	});
	$("button.undo").click(function() {
		revertToTheLatestState();
	})

	// PRACTICE TOOL HANDLERS
	$(".tool_name").click(function(){
		enableEditing($(this).attr("tool"),true);
		$(this).parent().find("div.tool_practice_detail").removeClass("hidden");
	});

	$("textarea.mini_task").on('input propertychange paste',function(){
		var isValid = validateSection();
		if (isValid) {
			$(this).parents("div.page").find("a.next_section").removeClass("hidden");
			$("div.information_container").animate({ scrollTop: $("div.page:visible").height() },'slow');	
		}
	});

	// MAKING THEME STICKY AT THE TOP
	$("div.theme_container").scroll(function(e) {
		var el = $('div.theme_container div.words_wrapper'); 
		if ($(this).scrollTop() > 62 && el.css('position') != 'fixed'){ 
			$(el).css({'position': 'fixed', 'top': '-45px', 'margin-right':'8px', 'z-index':104}); 
			$("div.theme_container div.documents_wrapper").css("margin-top",$(el).height());
		}	
		if ($(this).scrollTop() < 62 && el.css('position') == 'fixed'){
			$(el).css({'position': 'static', 'top': '-45px', 'margin-right':'0px'}); 
			$("div.theme_container div.documents_wrapper").css("margin-top",0);
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
	$("button.shortcut").click(function() {
		$("a.participate_button").trigger("click");
		// openPage("improving");
		openPage($(this).attr("target"));
	});
	$("button.shortcut_task").click(function() {
		$("a.participate_button").trigger("click");
		currentTheme= parseInt($(this).attr("target_theme"));
		openTheme(currentTheme);
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

	// HIDE ELEMENTS NOT READY
	//$("div.page").hide();
	//$("div.page[pagetype='tutorial']").show();

	currentTheme = -1;
	result = {"topics":[], "general":{}};
	log = [];

	
	// RETRIEVE THEME DATA FROM SERVER
	retrieveThemes();


});