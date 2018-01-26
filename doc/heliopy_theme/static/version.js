$.getJSON('https://pypi.python.org/pypi/heliopy/json', function(data) {
	ver= 'Current Version: ' + data.info.version;
	$('.version').html(ver);
});
