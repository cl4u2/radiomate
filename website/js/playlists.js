/*
 * Playlists and Media Files management
 *
 */

var user = $.cookie("username");
var session = $.cookie("sessionid");
checkSession(user, session);

$.fn.renderFileList = function(filelist) {
		/* Render list */
		var s = "";
		$.each(filelist, function(){
				var tmp = this;
				s += "<option value='" + tmp.id + "'>" + tmp.author + " -" + tmp.title + "[" + tmp.album + "] </option>";
		});

		return '<select id="filelist" size="30" multiple="multiple">' + s + '</select>';
}

$.fn.renderPlayListContent = function(filelist) {
		/* Render list */
		var s = "";
		$.each(filelist, function(){
				var tmp = this;
				s += "<option value='"+ tmp.id +"' id='" + tmp.position + "'>" + tmp.author + " -" + tmp.title + "[" + tmp.album + "] </option>";
		});

		return '<select id="playlistcontentlist" size="30" multiple="multiple">' + s + '</select>';
}

$.fn.delSearch = function() {
		this.value = "";
		$(this).unbind('focus');
};

$.fn.changeSearch = function() {
		searchterm = this.value;
		$.fn.listFiles(searchterm);
};

$.fn.getAndLoadFile = function(v) {
		var r0 = {request: "getfile", username: user, sessionid: session, mediafileid: v};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				$.fn.loadFileEditForm(data.mediafile);
		});
};

$.fn.removeFile = function() {
		var fileids = Array(); 
		$('#filelist option:selected').each(function() {
				fileids.push(this.value);
		});
		if(fileids.length == 0) 
			return false; // do nothing and do it quiet
		if(!confirm("Are you sure that you want do delete " + fileids.length + " items?"))
					return false;
		for(fileidindex in fileids) {
				var fileid = fileids[fileidindex];
				var r0 = {request: "unregisterfile", username: user, sessionid: session, mediafileid: fileid};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						if(data.responsen != 0) {
								// TODO display error message
						}
						$.fn.listFiles("");
				});
		}
};

$.fn.listFiles = function(searchterm) {
		$('.opendiv').fadeOut();
		$('.opendiv').removeClass('opendiv');
		var r0 = {request: "fullsearchfiles", username: user, sessionid: session, q: searchterm};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listoffiles");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderFileList(data.mediafilelist));
						$('#filelist option').dblclick(function(){ $.fn.getAndLoadFile(this.value); });
						$('#fileremovebutton').click($.fn.removeFile);
						$('#filelist').resizable({ handles: 'e, s' });
				} else {
						//TODO: handle this
				}
		});
};

$.fn.loadFileEditForm = function(obj) {
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
		/* the inline player */
		var url = "player.php?url=" + encodeURIComponent(obj.path) + "";
		$('#player').attr('src', url);

		$('#fileedit').addClass('opendiv'); 
		$('#fileedit').slideDown();
};

$.fn.registerFileAndLoad = function(mediafile){
		var r0 = {request: "registerfile", username: user, sessionid: session, mediafile: mediafile};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var mf = {};
				if(data.responsen == 0) {
						mf = data.mediafile;
				} else {
						//TODO: display error message
						mf = mediafile;
				}
				$.fn.listFiles("");
				$.fn.loadFileEditForm(mf);
		});
};

$.fn.processfileupload = function (data){
		$.fn.log(data);
		var path = data.path;
		if(data.responsen == 0) {
				// go on, scan the new file, register it and then load its data into edit form for registration
				var r0 = {request: "scanfile", username: user, sessionid: session, path: data.path};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						var mf = data.mediafile;
						$.fn.registerFileAndLoad(mf);
				});
		} else {
				//TODO: handle failed upload
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
						$.fn.listFiles("");
				} else {
						$.fn.registerFileAndLoad(mediafile);
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
						$.fn.loadFileEditForm(mf);
				} else {
						//TODO: handle this
				}
		});
};

$.fn.renderPlayLists = function(playlists) {
		/* Render list */
		var s = "";
		$.each(playlists, function(){
				var tmp = this;
				s += "<option value='" + tmp.id + "'>" + tmp.title + "[" + tmp.description + "] </option>";
		});

		return '<select id="playlistlist" size="30" multiple="multiple">' + s + '</select>';
};

$.fn.loadPlaylistEditForm = function(obj) {
		for(var i in obj) {
				if(obj[i]+"" == "true") {
						$('#playlisteditform input[id="'+i+'"]').attr('checked','checked');
				} else {
						if(obj[i]+"" == "false")
								$('#playlisteditform input[id="'+i+'"]').removeAttr('checked');
						else
								$('#playlisteditform input[id="'+i+'"]').val(obj[i]);
				}
		}
};

$.fn.playlistMetaEditing = function(e) {
		var y = e.pageY+30;
		var x = e.pageX-80;
		var r0 = {request: "getplaylist", username: user, sessionid: session, playlistid: this.value};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						$.fn.loadPlaylistEditForm(data.playlist);
						$('#playlistedit').css('top', y + 'px').css('left', x + 'px');
						$('#playlistedit').slideDown();
						$('#playlistedit').addClass('opendiv');
						var t = $("#playlistcontent");
						t.html("");
						filelist = $.fn.renderPlayListContent(data.playlist.mediafilelist);
						t.append(filelist);
						$('#playlistcontentlist option').dblclick(function() {
								$.fn.getAndLoadFile(this.value); 
						});
						$('#playlistcontentlist').resizable({ handles: 'e, s' });
				} else {
						// TODO: handle this
				}
		});
};

$.fn.playlistEditing = function(e) {
		var r0 = {request: "getplaylist", username: user, sessionid: session, playlistid: this.value};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						var t = $("#playlistcontent");
						t.html("");
						filelist = $.fn.renderPlayListContent(data.playlist.mediafilelist);
						t.append(filelist);
						$('#playlistcontentlist option').dblclick(function() {
								$.fn.getAndLoadFile(this.value); 
						});
						$('#playlistcontentlist').resizable({ handles: 'e, s' });
				} else {
						// TODO: handle this
				}
		});
};

$.fn.listPlaylists = function() {
		$('.opendiv').fadeOut();
		$('.opendiv').removeClass('opendiv');
		var r0 = {request: "listuserplaylists", username: user, sessionid: session, user: user};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listofplaylists");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderPlayLists(data.playlistlist));
						$('#listofplaylists option').click($.fn.playlistEditing);
						$('#listofplaylists option').dblclick($.fn.playlistMetaEditing);
						$('#playlistlist').resizable({ handles: 'e, s' });
				} else {
						//TODO: handle this
				}
		});
};

$.fn.updateplaylist = function (e){
		var sa = $(this).serializeArray();
		var obj = {};
		$.each(sa, function(){
				if(this.value == "on") 
						v = true;
				else 
						v = this.value;

				if(v)
					obj[this.name] = v;
		});
		var r0 = {request: "editplaylist", username: user, sessionid: session, playlist: obj};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						$.fn.listPlaylists();
				} else {
						var r0 = {request: "createplaylist", username: user, sessionid: session, playlist: obj};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								$.fn.log(data)
								if(data.responsen == 0) {
										$.fn.listPlaylists();
								} else {
										// TODO: handle this
								}
						});
				}
		});
		e.preventDefault();
		return false;
};

$.fn.addFiles2Playlist = function() {
		var playlistid = $('#listofplaylists option:selected').val();
		if(!playlistid) {
			// TODO: remove this alert
			alert('no valid playlist selected');
			return false;
		}
		var fileids = Array();
		$('#listoffiles option:selected').each(function() {
						fileid = $(this).val();
						fileids.push(fileid);
		});
		var r0 = {request: "addfilestoplaylist", username: user, sessionid: session, playlistid: playlistid, mediafileidlist: fileids};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						//reload the playlist
						var r0 = {request: "getplaylist", username: user, sessionid: session, playlistid: playlistid};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								$.fn.log(data);
								if(data.responsen == 0) {
										var t = $("#playlistcontent");
										filelist = $.fn.renderPlayListContent(data.playlist.mediafilelist);
										t.html(filelist);
								} else {
										// TODO: handle this
								}
						});
				} else {
					// TODO 
				}
		});
};

$.fn.removeFilesFromPlaylist = function() {
		var playlistid = $('#listofplaylists option:selected').val();
		if(!playlistid) {
			// TODO: remove this alert
			alert('no valid playlist selected');
			return false;
		}
		var filepos = Array();
		$('#playlistcontent option:selected').each(function() {
						fileposition = $(this).attr('id');
						filepos.push(fileposition);
		});
		var r0 = {request: "removefilesfromplaylist", username: user, sessionid: session, playlistid: playlistid, mediafilepositionlist: filepos};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						//reload the playlist
						var r0 = {request: "getplaylist", username: user, sessionid: session, playlistid: playlistid};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								$.fn.log(data);
								if(data.responsen == 0) {
										var t = $("#playlistcontent");
										filelist = $.fn.renderPlayListContent(data.playlist.mediafilelist);
										t.html(filelist);
								} else {
										// TODO: handle this
								}
						});
				} else {
					// TODO
				}
		});
};

$.fn.filemove = function(direction) {
		var playlistid = $('#listofplaylists option:selected').val();
		if(!playlistid) {
			// TODO: remove this alert
			alert('no valid playlist selected');
			return false;
		}
		var fileposition = $('#playlistcontent option:selected').attr('id');
		var newfileposition = parseInt(fileposition) + direction;
		var r0 = {request: "movefilesinplaylist", username: user, sessionid: session, playlistid: playlistid, oldmediafileposition: fileposition, newmediafileposition: newfileposition};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						//reload the playlist
						var r0 = {request: "getplaylist", username: user, sessionid: session, playlistid: playlistid};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								$.fn.log(data);
								if(data.responsen == 0) {
										var t = $("#playlistcontent");
										filelist = $.fn.renderPlayListContent(data.playlist.mediafilelist);
										t.html(filelist);
								} else {
										// TODO: handle this
								}
						});
				} else {
					// TODO
				}
		});
};

$.fn.removePlaylist = function() {
		var ids = Array(); 
		$('#playlistlist option:selected').each(function() {
				ids.push(this.value);
		});
		if(ids.length == 0) 
			return false; // do nothing and do it quiet
		if(!confirm("Are you sure that you want do delete " + ids.length + " items?"))
					return false;
		for(idindex in ids) {
				var id = ids[idindex];
				var r0 = {request: "removeplaylist", username: user, sessionid: session, playlistid: id};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						if(data.responsen != 0) {
								// TODO display error message
						}
						$.fn.listPlaylists();
				});
		}
};


$(document).ready(function(){
		$("input[type='text'], input[type='checkbox'], select").each(function(){
				$(this).after("<br />");
		});
		$.fn.listFiles("");
		$('#fileuploadform').ajaxForm({
				dataType: 'json', 
				success: $.fn.processfileupload, 
				resetForm: true
		});
		$('#fileeditform').submit($.fn.updatefile);
		$('#filerescan').click($.fn.rescanfile);
		$('#search1').focus($.fn.delSearch);
		$('#search1').keyup($.fn.changeSearch);
		$('#playlisteditform').submit($.fn.updateplaylist);
		$('#addbutton').click($.fn.addFiles2Playlist);
		$('#removebutton').click($.fn.removeFilesFromPlaylist);
		$('#upbutton').click(function() { return $.fn.filemove(-1); });
		$('#downbutton').click(function() { return $.fn.filemove(+1); });
		$('#fileaddbutton').click(function(e) { 
				if($('#fileuploaddiv').hasClass('opendiv')) {
						$('#fileuploaddiv').fadeOut(); 
						$('#fileuploaddiv').removeClass('opendiv'); 
				} else {
						var y = e.pageY-120;
						var x = e.pageX-300;
						$('#fileuploaddiv').css('top', y + 'px').css('left', x + 'px');
						$('#fileuploaddiv').slideDown(); 
						$('#fileuploaddiv').addClass('opendiv'); 
				} 
		});
		$('#playlistclose').click(function() { 
				$('.opendiv').fadeOut(); 
				$('.opendiv').removeClass('opendiv');
		});
		$('#fileclose').click(function() { 
				$('.opendiv').fadeOut(); 
				$('.opendiv').removeClass('opendiv');
		});
		$('#cancelupload').click(function() { 
				$('#fileuploaddiv').fadeOut(); 
				$('#fileuploaddiv').removeClass('opendiv'); 
		});
		$('#pladdbutton').click(function(e) {
				if($('#playlistedit').hasClass('opendiv')) {
						$('#playlistedit').fadeOut(); 
						$('#playlistedit').removeClass('opendiv'); 
				} else {
						var y = e.pageY;
						var x = e.pageX;
						//$('#playlistedit').css('top', y + 'px').css('left', x + 'px');
						$('#playlistreset').click(); 
						$('#playlistedit').slideDown(); 
						$('#playlistedit').addClass('opendiv'); 
				} 
		});
		$('#plremovebutton').click($.fn.removePlaylist);
		$.fn.listPlaylists();
});

