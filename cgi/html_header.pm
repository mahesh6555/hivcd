package html_header;
@EXPORT = qw(refreshHeader head calendar noConflict html_title endHead);


sub refreshHeader($q, $refreshType)
{
	print $q->header(-cache_control=>"no-cache, no-store, must-revalidate");
	head();
	refresh();
	endHeader();
	redirectMessage($refreshType);
}
sub head
{
	print <<HTML;
		<head>
			<meta http-equiv="content-type" content="text/html; charset=utf-8" />
			<meta name="robots" content="all" />
			<link rel="icon" href="http://hiv.aruplab.com/favicon.ico" type="image/x-icon" />
			<link rel="shortcut icon" href="http://hiv.aruplab.com/favicon.ico" type="image/x-icon" />
			
			<!-- CSS related files -->
			<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/styles.css"  />
			<link rel="stylesheet" type="text/css" media="print" href="rw_common/themes/magnesium/print.css"  />
			<link rel="stylesheet" type="text/css" media="handheld" href="rw_common/themes/magnesium/handheld.css"  />
			<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/css/styles/pink.css" />
			<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/css/width/width_1000.css" />
			<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/css/sidebar/sidebar_right.css" />
			<script type="text/javascript" src="rw_common/themes/magnesium/javascript.js"></script>
			
			<!-- Javascript files -->
			<script type="text/javascript" src="../js/readResults.js"></script>
			<script type="text/javascript" src="js/CalendarPopup.js"></script>
			<script type="text/javascript" src="rw_common/themes/magnesium/javascript.js"></script>
			<script type="text/javascript" src="js/CalendarPopup.js"></script>
HTML
}

sub calendar
{
	print <<HTML
		<script type="text/javascript">
			var cal = new CalendarPopup();
			cal.showYearNavigation();
			cal.showYearNavigationInput();
		</script>	
HTML
}

sub noConflict
{
	print <<HTML
		<script> <!-- Make jQuery not conflict with prototype. Gives \$ to prototype. -->
			jQuery.noConflict();
		</script>
HTML
}

sub refresh
{
	print <<HTML
			<meta http-equiv="REFRESH" content="2;url=../login.cgi">
HTML
}

sub html_title($docTitle)
{
	if($docTitle eq "expired")
	{
		print <<HTML
			<title>Session Expired</title>
HTML
	}
	elsif ($docTitle eq "previous")
	{
		print <<HTML
			<title>Previous Runs</title>
HTML
	}
	else
	{
		print <<HTML
			<title>Upload Sequence Run</title>
HTML
	}
}

sub endHead
{
	print <<HTML
		</head>
HTML
}

sub redirectMessage($message)
{
	print <<HTML
		<body>
		<br /><br /><br /><br />
		<h1> $message . Redirecting to login page.</h1>
		</body>
HTML
}