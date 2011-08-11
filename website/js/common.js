/* common functions */

$.fn.log = function(resp) {
		console.log(resp.responsen + "|" + resp.requested + "|" + resp.response + "|" + resp.warning + "|" + resp.description);
}

var loggeduser = null;

function checkSession(username, sessionid) {
		/* check if session is alive, otherwise go to login */
		var r0 = {request: "getuser", username: user, sessionid: sessionid, name: username};
		successf = function(data){
				$.fn.log(data);
				if(data.responsen != 0) {
						if (window.stop !== undefined) {
								window.stop();
						} else if (document.execCommand !== undefined) {
								document.execCommand("Stop", false);
						}   
						location.href = "login.html";
				} else {
						loggeduser = data.user;
				}
		};
		$.ajax({
				    type: 'GET',
				    url: '/cgi-bin/radiomatejson.cgi',
				    dataType: 'json',
				    success: successf,
				    data: {"req": JSON.stringify(r0)},
				    async: false
		});
}
