


function minimizeIntroduction() {
	$(".introduction").hide();
}

function startTask(num) {
	$(".turk_task[kid='"+num+"']").show();
	$(".refining_tool").show();

	$(".refining_tool").find("input[type='text']").val("");	
	$(".refining_tool").find("textarea").val("");	
	initThemeEditor();
}
//////////////////////////////
///  THEME EDITOR FUNCTIONS

function initThemeEditor() {
	// RESET
	$("ul.ref_theme_editor").empty().unbind();
	if($("ul.ref_theme_editor").hasClass("ui-sortable")) $("ul.ref_theme_editor").sortable("destroy");
	// GENERATE ref_theme_editor
	var el_terms = $(".turk_task:visible").find("div.term");
	$.each(el_terms, function(i,el){
		$("<li>"+$(el).text()+"</li>")
			.css("font-size",$(el).css("font-size"))
			.appendTo("ul.ref_theme_editor");
	});
	$("ul.ref_theme_editor").sortable({
		start: function(e, ui) {
			ui.placeholder.height(ui.helper.innerHeight()/2);
			ui.placeholder.width(ui.helper.innerWidth());
		}
	});
	$("ul.ref_theme_editor").find("li").click(function() {
		$(this).toggleClass("selected");
		updateThemeEditorButtons();
		event.stopPropagation();
	});
	$("ul.ref_theme_editor").click(function() {
		$(this).find("li").removeClass("selected");
		console.log("deselect");
	});
	$("ul.ref_theme_editor").disableSelection();
}

function updateThemeEditorButtons() {
	if($("ul.ref_theme_editor > li.selected").length==0) $("button.forSelection").prop('disabled',true);
	else $("button.forSelection").prop('disabled',false);
}
function removeSelectedWords() {
	$("ul.ref_theme_editor > li.selected").addClass("removed");
}
function mergeSelectedWords() {

}
function splitTopic() {

}


$(document).ready(function() {
	//startTask(1);

	// ASSIGNE EVENT HANDLERS
	$("button.start_button").click(function() {
		// minimizeIntroduction(); 	
		$(".introduction").hide();
		$(".turk_tasks").show();
		$(".refinement_container").show();

	});
	$("button.lets_begin").click(function() {
		$(".tutorial").hide();
		startTask(1);
	});
	$("button.next").click(function() {
		$(this).parents(".refining_stage").find("input, textarea").attr("disabled","disabled");
		var targetStage = $(this).attr("targetstage");
		$(this).parents(".refining_tool").find(".refining_stage[stage='"+targetStage+"']").show();
		$(this).hide();
	});
	$("button.ref_theme_remove_words").click(removeSelectedWords);
	$("button.ref_theme_merge_words").click(mergeSelectedWords);
	$("button.ref_theme_split_topic").click(splitTopic);
	$("button.ref_theme_reset").click(initThemeEditor);


	$("li.doc_item").click(function() {
		$(this).toggleClass("zoomed");

	});
});