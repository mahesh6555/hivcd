sub headerInclude
{
	print <<HTML
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<meta name="robots" content="all" />
		<link rel="icon" href="http://hiv.aruplab.com/favicon.ico" type="image/x-icon" />
		<link rel="shortcut icon" href="http://hiv.aruplab.com/favicon.ico" type="image/x-icon" />
		
		<title>Upload Sequence Run</title>
		<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/styles.css"  />
		<link rel="stylesheet" type="text/css" media="print" href="rw_common/themes/magnesium/print.css"  />
		<link rel="stylesheet" type="text/css" media="handheld" href="rw_common/themes/magnesium/handheld.css"  />
		<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/css/styles/pink.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/css/width/width_1000.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="rw_common/themes/magnesium/css/sidebar/sidebar_right.css" />
		
		<script type="text/javascript" src="js/CalendarPopup.js"></script>
		<script type="text/javascript" src="rw_common/themes/magnesium/javascript.js"></script>
		<script type="text/javascript" src="js/CalendarPopup.js"></script>
		<script type="text/javascript">
			var cal = new CalendarPopup();
			cal.showYearNavigation();
			cal.showYearNavigationInput();
		</script>
		<title>Session Expired</title>
		<meta http-equiv="REFRESH" content="2;url=../login.cgi">
	</head>
}
