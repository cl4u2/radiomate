/*
 * Log-in management
*/

$(document).ready(function(){
				$("#formlogin").addClass("floating");
				$("input").each(function(){
						$(this).after("<br />");
				});
				$('#loginform').submit(function(e){
						var credentials = $(this).serializeArray();
						var credential = {};
						$.each(credentials, function () {
								credential[this.name] = this.value;
						});
						var username = credential['username'];
						var password = credential['password'];
						var r0 = {request: "login", username: username, password: password};
						$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
								if(data.responsen == 0) {
										$.cookie("sessionid", data.sessionid);
										$.cookie("username", username);
										location.href = "dashboard.html";
								} else {
										//try again
										return false
								}
						});
						e.preventDefault();
						return false;
				});
});
