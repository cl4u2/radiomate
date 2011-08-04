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

$(document).ready(function(){
		$("input[type='text'], input[type='checkbox'], select").each(function(){
				$(this).after("<br />");
		});
		$.fn.loadSlotTypes($('#slottype'));
		$.fn.loadDurations($('#duration'));
		$.fn.loadPlaylists($('#fallbackplaylist'));
		Protoplasm.use('datepicker').transform('input.datepicker');
		$('#calendar').fullCalendar({
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
								data: r0,
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
});

