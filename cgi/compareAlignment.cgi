#!/usr/bin/perl -w
use warnings;
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
use Data::Dumper;
use IO::Handle;
use Text::Chomp;
use CGI::Session ( '-ip_match' );


$Data::Dumper::Useqq = 1; #shows all non-printable characters

# Read in compareAlignmentBody and print it
my $q = new CGI;
my $session = CGI::Session->load();

if($session->is_expired){
	print $q->header(-cache_control=>"no-cache, no-store, must-revalidate");
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
	<body>
		Your session has expired. Redirecting to login page.
	</body>
HTML
}

elsif($session->is_empty){
	print $q->header(-cache_control=>"no-cache, no-store, must-revalidate");
print <<HTML
	<head>
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<meta name="robots" content="all" />
		<link rel="icon" href="http://hiv.aruplab.com/favicon.ico" type="image/x-icon" />
		<link rel="shortcut icon" href="http://hiv.aruplab.com/favicon.ico" type="image/x-icon" />
		
		<title>Previous Runs</title>
		<link rel="stylesheet" type="text/css" media="screen" href="../rw_common/themes/magnesium/styles.css"  />
		<link rel="stylesheet" type="text/css" media="print" href="../rw_common/themes/magnesium/print.css"  />
		<link rel="stylesheet" type="text/css" media="handheld" href="../rw_common/themes/magnesium/handheld.css"  />
		<link rel="stylesheet" type="text/css" media="screen" href="../rw_common/themes/magnesium/css/styles/pink.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../rw_common/themes/magnesium/css/width/width_1000.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../rw_common/themes/magnesium/css/sidebar/sidebar_right.css" />
		
		<script type="text/javascript" src="../rw_common/themes/magnesium/javascript.js"></script>

		<!--script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script-->
		<script type="text/javascript" src="../js/jquery-1.3.2.min.js"></script>
		<script> <!-- Make jQuery not conflict with prototype. Gives \$ to prototype. -->
			jQuery.noConflict();
		</script>

		<!-- read any results file from server -->
		<script type="text/javascript" src="../js/readResults.js"></script>

		<meta http-equiv="REFRESH" content="2;url=../login.cgi">
	</head>

	<body>
		You have not logged in.. Redirecting to login page.
	</body>
HTML
}


else{

	print $q->header();
	my $bodyFile = "compareAlignmentBody.html";
	open(BODY,"<$bodyFile") or die "Can't open $bodyFile: $!";
	while(<BODY>){
		print $_;
	}

	my $alignmentFileName = $q->param("filename");
	my $header = $q->param("header");
	updateElementById_append("alignmentComparisonHeader",$header);

	open(ALIGNMENT,"<$alignmentFileName") or die "Can't open $alignmentFileName: $!" . $q->br();
	while(<ALIGNMENT>){
		$_ = tchomp($_);
		updateElementById_append("alignmentComparison",$_);
	}

	print $q->end_html;
}

sub updateElementById_append {
	my $element = shift;
	my $output = shift;
print <<END_HTML;
	<script type="text/javascript">jQuery("#$element").append("$output");</script>
END_HTML
}
