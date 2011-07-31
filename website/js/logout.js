/* Log out */

$(document).ready(function(){ 
		user = $.cookie("username");
		session = $.cookie("sessionid");
		var r0 = {request: "logout", username: user, sessionid: session};
		$.getJSON('/cgi-bin/radiomatejson.cgi', {"req": JSON.stringify(r0)}, function(data){
				$.fn.log(data);
				if(data.responsen == 0) {
						$.cookie('username',null);
						$.cookie('sessionid',null);
						location.href = "index.html";
				} else {
						// TODO: handle this
				}
		});
});

