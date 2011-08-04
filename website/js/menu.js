
radiomatemenu = function () {
				var menu;
				menu = '<ul class="menuclass">';
				menu += '<li>home</li>';
				menu += '<li><a href="login.html">login</a></li>';
				menu += '<li><a href="dashboard.html">dashboard</a></li>';
				menu += '<li><a href="roles.html">roles</a></li>';
				menu += '<li><a href="users.html">users</a></li>';
				menu += '<li><a href="playlists.html">playlists</a></li>';
				menu += '<li><a href="transmissions.html">transmissions</a></li>';
				menu += '<li><a href="logout.html">logout</a></li>';
				menu += '</ul>';
				$('#menu').html(menu);
};

$(document).ready(function(){
				radiomatemenu();
});

