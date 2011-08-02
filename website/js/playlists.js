/*
 * Playlists and Media Files management
 *
 */

var user = '';
var session = '';

$.fn.renderFileList = function(filelist) {
		/* Render list */
		var s = "";
		$.each(filelist, function(){
				var tmp = this;
				s += "<option value='" + tmp.id + "'>" + tmp.title + " [" + tmp.author + "] </option>";
		});

		return '<select id="filelist" multiple="multiple">' + s + '</select>';
}

$.fn.listFiles= function() {
		var r0 = {request: "searchfiles", username: user, sessionid: session, mediafile: {}};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listoffiles");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderFileList(data.mediafilelist));
				} else {
						//TODO: handle this
				}
		});
};

$.fn.processfileupload = function (data){
		$.fn.log(data);
		if(data.responsen == 0) {
				// go on, register the new file and then load its data into edit form
				var r0 = {request: "registerfile", username: user, sessionid: session, mediafile: {path: data.path}};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						if(data.responsen == 0) {
								var curr = data.mediafile;
								for(var i in curr) {
										if(curr[i]+"" == "true") {
												$('#fileeditform input[id="'+i+'"]').attr('checked','checked');
										} else {
												if(curr[i]+"" == "false")
														$('#fileeditform input[id="'+i+'"]').removeAttr('checked');
												else
														$('#fileeditform input[id="'+i+'"]').val(curr[i]);
										}
								}
						} else {
								//TODO: handle this
						}
				});
		} else {
				//TODO: handle this
		}
};

$(document).ready(function(){
				user = $.cookie("username");
				session = $.cookie("sessionid");

				$("input, select").each(function(){
						$(this).after("<br />");
				});
				$.fn.listFiles();
				$('#fileuploadform').ajaxForm({dataType: 'json', success: $.fn.processfileupload, resetForm: true});
});

