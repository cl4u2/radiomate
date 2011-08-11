<html>
		<head>
				<link rel="stylesheet" href="3p/soundmanager/css/360player.css" type="text/css" />
				<link rel="stylesheet" href="3p/soundmanager/css/360player-visualization.css" type="text/css" />
				<script src="3p/soundmanager/script/berniecode-animator.js"></script>
				<script src="3p/soundmanager/script/soundmanager2-nodebug-jsmin.js"></script>
				<script src="3p/soundmanager/script/360player.js"></script>
				<script>
soundManager.url = '3p/soundmanager/swf/';
soundManager.flashVersion = 9; // optional: shiny features (default = 8)
soundManager.useFlashBlock = false; // optionally, enable when you're ready to dive in
soundManager.useFastPolling = true; // increased JS callback frequency, combined with useHighPerformance = true

threeSixtyPlayer.config.scaleFont = (navigator.userAgent.match(/msie/i)?false:true);
threeSixtyPlayer.config.showHMSTime = true;
// enable some spectrum stuffs
threeSixtyPlayer.config.useWaveformData = true;
threeSixtyPlayer.config.useEQData = true;
// enable this in SM2 as well, as needed
if (threeSixtyPlayer.config.useWaveformData) {
  soundManager.flash9Options.useWaveformData = true;
}
if (threeSixtyPlayer.config.useEQData) {
  soundManager.flash9Options.useEQData = true;
}
if (threeSixtyPlayer.config.usePeakData) {
  soundManager.flash9Options.usePeakData = true;
}
if (threeSixtyPlayer.config.useWaveformData || threeSixtyPlayer.flash9Options.useEQData || threeSixtyPlayer.flash9Options.usePeakData) {
  // even if HTML5 supports MP3, prefer flash so the visualization features can be used.
  soundManager.preferFlash = true;
}
// favicon is expensive CPU-wise, but can be enabled.
threeSixtyPlayer.config.useFavIcon = false;
				</script>
		</head>
		<body><div class="ui360 ui360-vis"><a href="<?=$_GET[url] ?>"></a></div></body>
</html>
