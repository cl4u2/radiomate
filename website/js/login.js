/*
 * Log-in management
*/

$(document).ready(function(){
				//$("#divlogin").addClass("floating");
				//$("input:submit").button();
				//$("input").each(function(){
				//		$(this).after("<br />");
				//});
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
								$.fn.log(data);
								if(data.responsen == 0) {
										$.cookie("sessionid", data.sessionid);
										$.cookie("username", username);
										location.href = "dashboard.html";
								} else {
										// TODO: message "try again"
										return false
								}
						});
						e.preventDefault();
						return false;
				});
});

