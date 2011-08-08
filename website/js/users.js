/*
 * Users
 *
 */

var user = $.cookie("username");
var session = $.cookie("sessionid");
checkSession(user, session);

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

$.fn.editUser = function(e) {
		var thisbutton = $(this);
		if(thisbutton.hasClass('clickededit'))
		{
				$('#newuserform').slideUp();
				$(this).removeClass('clickededit');
				return true;
		}
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
				var y = e.pageY + 30;
				var x = e.pageX - 30;
				$('#newuserform').css('top', y + 'px').css('left', x + 'px');
				$('#newuserform').hide();
				$('#newuserform').slideDown();
				$('#newuserform input:first').focus();
				$('.clickededit').removeClass('clickededit');
				thisbutton.addClass('clickededit');
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
				if(data)
						return "<td>" + data + "</td>";
				else
						return "<td class='emptycell'></td>";
		}
		function avatar(md5sum) {
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
				appendtorow('avatar', avatar(tmp.emailsmd5), rows);
				if(tmp.name == "admin")
						appendtorow('Edit', incell(''), rows);
				else
						appendtorow('Edit', incell("<input type='button' class='edituser' id='e" + tmp.name + "' value='Edit' />"), rows);
		});
	    
		appendtorow('checkbox', '<td class="noborder"><input id="delbutton" type="button" value="del"></td>', rows);
	    appendtorow('Edit', '<td class="noborder"><input id="addbutton" type="button" value="new"></td>', rows);

		var s = "";
		for(var label in rows) {
				if(label in {Edit: 0, checkbox: 0, avatar: 0})
						s += "<tr><th class='emptycell'></th>";
				else
						s += "<tr><th>" + label + "</th>";
				for(var i=0; i<rows[label].length; i++) {
						s += rows[label][i];
				}
				s += "</tr>";
		}
		return '<table id="userlist">' + s + '</table>';
}

$.fn.listUsers = function() {
		$('#newuserform').hide();
		var r0 = {request: "listusers", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listofusers");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderUserTableVert(data.userlist));
						t.removeClass("redclass");
						
						/* Role management events */ 
						$("#delbutton").click($.fn.delUsers);
						$("#addbutton").click($.fn.addUser);
						$("input.edituser").click($.fn.editUser);
						/*
						$(".edituser").toggle($.fn.editUser, function(){
								$('#newuserform').slideUp(); 
								$(this).removeClass('open')}
						);
						*/
				} else {
						//TODO: handle this
				}
		});
};


$.fn.loadRoles = function(element) {
		var r0 = {request: "listroles", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				// TODO: check responsen code
				$.each(data.rolelist, function() {
						element.append('<option value="' + this.rolename + '">' + this.rolename + '</option>');
				});
		});
};


$.fn.addUser = function(e) {
		var thisbutton = $(this);
		if(thisbutton.hasClass('clickededit'))
		{
				$('#newuserform').slideUp();
				$(this).removeClass('clickededit');
				return true;
		}
		var y = e.pageY - 30;
		var x = e.pageX + 30;
		$('#newuserform').css('top', y + 'px').css('left', x + 'px');
		$('#newuserform').hide();
		$('#userreset').click();
		$('#newuserform').slideDown();
		$('#newuserform input:first').focus();
		$('.clickededit').removeClass('clickededit');
		thisbutton.addClass('clickededit');
};

$(document).ready(function(){
				$('#newuserform').hide();
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
												if (data.responsen == 0) {
														$.fn.listUsers();
												} else {
														// TODO: handle this
												}
										});
								}
						});
						e.preventDefault();
						return false;
				});
});



