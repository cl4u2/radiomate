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

		return '<select id="filelist" size="50" multiple="multiple">' + s + '</select>';
}

$.fn.listFiles = function() {
		var r0 = {request: "searchfiles", username: user, sessionid: session, mediafile: {}};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listoffiles");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderFileList(data.mediafilelist));
						$('#filelist option').dblclick(function(){
								var r0 = {request: "getfile", username: user, sessionid: session, mediafileid: this.value};
								$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
										$.fn.log(data);
										$.fn.loadEditForm(data.mediafile);
								});
						});
				} else {
						//TODO: handle this
				}
		});
};

$.fn.loadEditForm = function(obj) {
		for(var i in obj) {
				if(obj[i]+"" == "true") {
						$('#fileeditform input[id="'+i+'"]').attr('checked','checked');
				} else {
						if(obj[i]+"" == "false")
								$('#fileeditform input[id="'+i+'"]').removeAttr('checked');
						else
								$('#fileeditform input[id="'+i+'"]').val(obj[i]);
				}
		}
};

$.fn.registerFileAndLoad = function(mediafile){
		var r0 = {request: "registerfile", username: user, sessionid: session, mediafile: mediafile};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						var mf = data.mediafile;
						$.fn.loadEditForm(mf);
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
								var mf = data.mediafile
								$.fn.loadEditForm(mf);
						} else {
								//TODO: handle this
						}
				});
		} else {
				//TODO: handle this
		}
};

$.fn.updatefile = function (e){
		var nfiles = $(this).serializeArray();
		var mediafile = {};
		$.each(nfiles, function(){
				if(this.value == "on") 
						v = true;
				else 
						v = this.value;

				if(v)
					mediafile[this.name] = v;
		});
		var r0 = {request: "editfile", username: user, sessionid: session, mediafile: mediafile};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						$.fn.listFiles();
				} else {
						//TODO: handle this
				}
		});
		e.preventDefault();
		return false;
};

$.fn.rescanfile = function() {
		var nfiles = $('#fileeditform').serializeArray();
		var mediafile = {};
		$.each(nfiles, function(){
				if(this.value == "on") 
						v = true;
				else 
						v = this.value;

				if(v)
					mediafile[this.name] = v;
		});
		var r0 = {request: "scanfile", username: user, sessionid: session, path: mediafile.path};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						mf = data.mediafile
						mf.id = mediafile.id
						$.fn.loadEditForm(mf);
				} else {
						//TODO: handle this
				}
		});
};

$(document).ready(function(){
		user = $.cookie("username");
		session = $.cookie("sessionid");

		$("input, select").each(function(){
				$(this).after("<br />");
		});
		$.fn.listFiles();
		$('#fileuploadform').ajaxForm({dataType: 'json', success: $.fn.processfileupload, resetForm: true});
		$('#fileeditform').submit($.fn.updatefile);
		$('#filerescan').click($.fn.rescanfile);
});

