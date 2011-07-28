/*
 * Users
 *
 */

var user = '';
var session = '';

$.fn.log = function(resp) {
		console.log(resp.responsen + "|" + resp.requested + "|" + resp.response + "|" + resp.description);
}

$.fn.delUsers = function() {
		var rcount = $('.delusers:checked').length;
		if(rcount == 0)
					return false;
		if(!confirm("Are you sure that you want do delete " + rcount + " elements?"))
					return false;
		$('.delusers:checked').each(function(index) {
				var r0 = {request: "removeuser", username: user, sessionid: session, name: this.value};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						/* When elements are deleted, retrieve the updated list */
						if(index == rcount-1) $.fn.listUsers();
				});
		});
};

$.fn.editUser = function() {
		rname = this.id.slice(1);
		var r0 = {request: "getuser", username: user, sessionid: session, name: rname};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen != 0)
						return false; /* TODO: handle error condition */

				curr = data.user;
				for(var i in curr) {
						if(curr[i]+"" == "true") {
								$('input[id="'+i+'"]').attr('checked','checked');
						} else {
								if(curr[i]+"" == "false")
										$('input[id="'+i+'"]').removeAttr('checked');
								else
										$('input[id="'+i+'"]').val(curr[i]);
						}
				}

		});
}

$.fn.renderUserTableVert = function(userlist) {
		/* Render list as a table, vertical layout */
		function truefalse(el) {
				if(el) 
					return '<td class="greenclass"> yes </td>';
				else 
					return '<td class="redclass"> no </td>';
		}
		function deletioncheckbox(name) {
				if(name == "admin")
					return '<td></td>'
				return '<td><input type="checkbox" class="delusers" id="del' + name + '" value="'+name+'" /></td>'
		}
		function appendtorow(label, htmlcode, rows) {
				if(label == "role")
						return true;
				if(label in rows) {
						rows[label].push(htmlcode);
				} else {
						rows[label] = new Array();
						rows[label].push(htmlcode);
				}
		}
		function incell(data) {
				return "<td>" + data + "</td>";
		}
		function gravatar(md5sum) {
				return "<td><img src='http://www.gravatar.com/avatar/" + md5sum + "?s=40'></td>";
		}
		var rows = new Array();
		$.each(userlist, function(){
				var tmp = this;
				appendtorow('checkbox', deletioncheckbox(tmp.name), rows);
				appendtorow('name', incell(tmp.name), rows);
				for(var i in tmp) {
						if(i == 'name' || i =='emailsmd5')
							continue;
						if(tmp[i] == true || tmp[i] == false) {
								appendtorow(i, truefalse(tmp[i]), rows);
						} else {
								appendtorow(i, incell(tmp[i]), rows);
						}
				}
				appendtorow('', gravatar(tmp.emailsmd5), rows);
				if(tmp.name == "admin")
						appendtorow('Edit', incell(''), rows);
				else
						appendtorow('Edit', incell("<input type='button' class='edituser' id='e" + tmp.name + "' value='Edit' />"), rows);
		});

		var s = "";
		for(var label in rows) {
				s += "<tr><th>" + label + "</th>";
				for(var i=0; i<rows[label].length; i++) {
						s += rows[label][i];
				}
				s += "</tr>";
		}
		return '<table id="userlist">' + s + '<tr><td><input id="delbutton" type="button" value="del"></td></tr></table>';
}

$.fn.listUsers = function() {
		var r0 = {request: "listusers", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listofusers");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderUserTableVert(data.userlist));
						t.removeClass("redclass");
						
						/* Role deletion event */ 
						$("#delbutton").click($.fn.delUsers);

						/* Role editing event */
						$(".edituser").click($.fn.editUser);
				} else {
						//TODO: handle this
				}
		});
};


$.fn.loadRoles = function(element) {
		var r0 = {request: "listroles", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				$.each(data.rolelist, function() {
						element.append('<option value="' + this.rolename + '">' + this.rolename + '</option>');
				});
		});
}

$(document).ready(function(){
				user = $.cookie("username");
				session = $.cookie("sessionid");

				$("input, select").each(function(){
						$(this).after("<br />");
				});
				$.fn.loadRoles($("#rolename"));

				$.fn.listUsers();
				$('#newuser').submit(function(e){
						var nusers = $(this).serializeArray();
						var nuser = {};
						$.each(nusers, function(){
								if(this.value == "on") 
										v = true;
								else 
										v = this.value;

								if(v)
									nuser[this.name] = v;
						});
						$('#newuser > input:checkbox').not(":checked").each(function () {
								nuser[this.name] = false;
						});
						var r0 = {request: "edituser", username: user, sessionid: session, user: nuser};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								$.fn.log(data)
								$.fn.listUsers();
								if(data.responsen != 0) {
										var r0 = {request: "createuser", username: user, sessionid: session, user: nuser};
										$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
												$.fn.log(data)
												$.fn.listUsers();
										});
								}
						});
						e.preventDefault();
						return false;
				});
});



