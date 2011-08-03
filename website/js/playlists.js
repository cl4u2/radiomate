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
				s += "<option value='" + tmp.id + "'>" + tmp.author + " -" + tmp.title + "[" + tmp.album + "] </option>";
		});

		return '<select id="filelist" multiple="multiple">' + s + '</select>';
}

$.fn.listFiles = function() {
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

$.fn.loadEditForm = function(curr) {
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
};

$.fn.registerFileAndLoad = function(mediafile){
		var r0 = {request: "registerfile", username: user, sessionid: session, mediafile: mediafile};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						var curr = data.mediafile;
						$.fn.loadEditForm(curr);
						$.fn.listFiles();
				} else {
						//TODO: handle this
				}
		});
};

$.fn.processfileupload = function (data){
		$.fn.log(data);
		if(data.responsen == 0) {
				// go on, scan the new file, register it and then load its data into edit form for registration
				var r0 = {request: "scanfile", username: user, sessionid: session, path: data.path};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						if(data.responsen == 0) {
								mf = data.mediafile
								$.fn.registerFileAndLoad(mf);
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

