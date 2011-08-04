/*
 * Playlists and Media Files management
 *
 */

var user = $.cookie("username");
var session = $.cookie("sessionid");
checkSession(user, session);

$.fn.loadSlotTypes = function(element) {
		var r0 = {request: "listslottypes", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				// TODO: check responsen code
				$.each(data.slottypeslist, function() {
						element.append('<option value="' + this + '">' + this + '</option>');
				});
				$('#slottype').change();
		});
};

$.fn.loadDurations = function(element) {
		var r0 = {request: "getuser", username: user, sessionid: session, name: user};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				// TODO: check responsen code
				var role = data.user.role;
				// TODO: transform select into textbox if fixedSlotTimes = false
				$.each(role.fixedSlotTimesList.split(","), function() {
						element.append('<option value="' + this + '">' + this + '</option>');
				});
		});
};

$.fn.loadPlaylists = function(element) {
		var r0 = {request: "listuserplaylists", username: user, sessionid: session, user: user};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				// TODO: check responsen code
				$.each(data.playlistlist, function() {
						element.append('<option value="' + this.id + '">' + this.title + '</option>');
				});
		});
};

$.fn.updateTransmission = function(e) {
		var sa = $(this).serializeArray();
		var obj = {};
		obj['slotparams'] = {};
		$.each(sa, function(){
				if(this.value == "on") 
						v = true;
				else 
						v = this.value;

				if(v) {
						if(this.name.substring(0,3) == "sp_"){
								var tmpname = this.name.split('_')[1];
								if(tmpname == "playlistid") // really awful. FIXME!!!
										obj['slotparams'][tmpname] = parseInt(v);
								else
										obj['slotparams'][tmpname] = v;
						} else {
								obj[this.name] = v;
						}
				}
		});
		var d = new Date(obj.beginningtimepicker);
		var dnew = {
				year: d.getFullYear(),
				month: d.getMonth() + 1,
				day: d.getDate(),
				hour: d.getHours(),
				minute: d.getMinutes()
		};
		obj.beginningtime = dnew;
		delete obj.beginningtimepicker;
		var r0 = {request: "reservetimeslot", username: user, sessionid: session, timeslot: obj};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						// reload the calendar
				} else {
						// TODO: handle by printing an error somewhere
				}
		});
		e.preventDefault();
		return false;
};

$.fn.loadParams = function(slotname) {
		var r0 = {request: "getslotreqparameters", username: user, sessionid: session, slottype: slotname};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						t = $('#slotparamdiv');
						t.html("");
						$.each(data.parameters, function(){
								var pname0 = this.split(':')[0];
								pname = "sp_" + pname0;
								var ptype = this.split(':')[1];
								switch(ptype) {
									case 'text':
										t.append('<label for="'+pname+'">'+pname0+': </label>');
										t.append('<input type="text" name="'+pname+'" id="'+pname+'">');
										t.append('<br/>');
										break;
									case 'playlist':
										t.append('<label for="'+pname+'">'+pname0+': </label>');
										t.append('<select name="'+pname+'" id="'+pname+'">');
										t.append('</select>');
										t.append('<br/>');
										$.fn.loadPlaylists($('#'+pname));
										break;
									default:
										//do nothing
								}
						});
				} else {
				}
		});
};

$(document).ready(function(){
		$("input[type='text'], input[type='checkbox'], select").each(function(){
				$(this).after("<br />");
		});
		$.fn.loadSlotTypes($('#slottype'));
		$.fn.loadDurations($('#duration'));
		$.fn.loadPlaylists($('#fallbackplaylist'));
		$('#beginningtimepicker').datetimepicker({
				firstday: 1,
				dateFormat: 'default',
				showButtonPanel: true
		});
		$('#calendar').fullCalendar({
				firstDay: 1,
				events: function(start, end, callback) {
						var r0 = {
								request: "listtimeslots", 
								username: user, 
								sessionid: session, 
								timeslot: {
										from: {
												year: start.getFullYear(),
												month: start.getMonth(),
												day: start.getDate(),
												hour: start.getHours(),
												minute: start.getMinutes()
										},
										to: {
												year: end.getFullYear(),
												month: end.getMonth(),
												day: end.getDate(),
												hour: end.getHours(),
												minute: end.getMinutes()
										}
								}
						};
						$.ajax({
								url: '/cgi-bin/radiomatejson.cgi',
								dataType: 'json',
								data: {"req": JSON.stringify(r0)},
								success: function(doc) {
										var events = [];
										$(doc).find('event').each(function() {
												events.push({
														title: $(this).attr('title'),
														description: $(this).attr('description'),
														start: $(this).attr('start') // will be parsed
												});
										});
										callback(events);
								}
						});
				}
		});
		$('#transmissioneditform').submit($.fn.updateTransmission);
		$('#slottype').change(function() { $.fn.loadParams($('#slottype').val()) });
});

