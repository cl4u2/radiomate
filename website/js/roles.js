/*
 * Roles
 *
 */

var user = $.cookie("username");
var session = $.cookie("sessionid");
checkSession(user, session);

$.fn.delRoles = function() {
		var rcount = $('.delroles:checked').length;
		if(rcount == 0)
					return false;
		if(!confirm("Are you sure that you want do delete " + rcount + " elements?"))
					return false;
		$('.delroles:checked').each(function(index) {
				var r0 = {request: "removerole", username: user, sessionid: session, rolename: this.value};
				$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
						$.fn.log(data);
						/* When roles are deleted, retrieve the updated list */
						if(index == rcount-1) $.fn.listRoles();
				});
		});
};

$.fn.editRole = function() {
		rname = this.id.slice(1);
		var r0 = {request: "getrole", username: user, sessionid: session, rolename: rname};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen != 0)
						return false; /* TODO: handle error condition */

				curr = data.role;
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

$.fn.renderRolesTableVert = function(rolelist) {
		/* Render rolelist as a table, vertical layout */
		function truefalse(el) {
				if(el) 
					return '<td class="greenclass"> yes </td>';
				else 
					return '<td class="redclass"> no </td>';
		}
		function deletioncheckbox(name) {
				if(name == "admin")
					return '<td></td>'
				return '<td><input type="checkbox" class="delroles" id="del' + name + '" value="'+name+'" /></td>'
		}
		function appendtorow(label, htmlcode, rows) {
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
		var rows = new Array();
		$.each(rolelist, function(){
				var tmp = this;
				appendtorow('checkbox', deletioncheckbox(tmp.rolename), rows);
				appendtorow('rolename', incell(tmp.rolename), rows);
				for(var i in tmp) {
						if(i == "rolename" || i == "fixedSlotTimesList")
								continue;
						if(tmp[i] == true || tmp[i] == false) {
								appendtorow(i, truefalse(tmp[i]), rows);
						} else {
								appendtorow(i, incell(tmp[i]), rows);
						}
				}
				if(tmp.rolename == "admin")
						appendtorow('Edit', incell(''), rows);
				else
						appendtorow('Edit', incell("<input type='button' class='editrole' id='e" + tmp.rolename + "' value='Edit' />"), rows);
		});

		var s = "";
		for(var label in rows) {
				s += "<tr><th>" + label + "</th>";
				for(var i=0; i<rows[label].length; i++) {
						s += rows[label][i];
				}
				s += "</tr>";
		}
		return '<table id="rolelist">' + s + '<tr><td><input id="delbutton" type="button" value="del"></td></tr></table>';
}

$.fn.listRoles = function() {
		var r0 = {request: "listroles", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				var t = $("#listofroles");
				t.html("");
				if(data.responsen == 0) {
						t.append($.fn.renderRolesTableVert(data.rolelist));
						
						/* Role deletion event */ 
						$("#delbutton").click($.fn.delRoles);

						/* Role editing event */
						$(".editrole").click($.fn.editRole);
				} else {
						// TODO: handle this
				}
		});
};

$(document).ready(function(){
				$("input").each(function(){
						$(this).after("<br />");
				});

				$.fn.listRoles();
				$('#newrole').submit(function(e){
						var nroles = $(this).serializeArray();
						var nrole = {};
						$.each(nroles, function(){
								if(this.value == "on") 
										v = true;
								else 
										v = this.value;

								if(v)
									nrole[this.name] = v;
						});
						$('#newrole > input:checkbox').not(":checked").each(function () {
								nrole[this.name] = false;
						});
						var r0 = {request: "editrole", username: user, sessionid: session, role: nrole};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								$.fn.log(data)
								$.fn.listRoles();
								if(data.responsen != 0) {
										var r0 = {request: "createrole", username: user, sessionid: session, role: nrole};
										$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
												$.fn.log(data)
												$.fn.listRoles();
										});
								}
						});
						e.preventDefault();
						return false;
				});
});



