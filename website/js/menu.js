

$(document).ready(function(){
		var menu = '';
		menu += '<li><a href="login.html">login</a></li>';
		menu += '<li><a href="users.html">users</a></li>';
		menu += '<li><a href="roles.html">roles</a></li>';
		menu += '<li><a href="playlists.html">playlists</a></li>';
		menu += '<li><a href="transmissions.html">transmissions</a></li>';
		menu += '<li><a href="logout.html">logout</a></li>';

		$('#menu').html("");
		if(loggeduser) 
				$('#menu')
				.append('<img src="http://www.gravatar.com/avatar/'+ loggeduser.emailsmd5 +'?s=28"/>');
		$('#menu').append('<ul class="menuclass">'+menu+'</ul>');
});

