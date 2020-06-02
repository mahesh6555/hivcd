#!/usr/bin/perl -w
use warnings;
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
use Data::Dumper;
use IO::Handle;
use CGI::Session ( '-ip_match' );

$Data::Dumper::Useqq = 1; #shows all non-printable characters

my $q = new CGI;
my $session = CGI::Session->load();

if($session->is_expired){
	html_header->refreshHeader($q, "Your session has expired");
}
elsif($session->is_empty){
	html_header->refreshHeader($q, "You have not logged in");
}
else{
	# Read in previousRunsBody and print it
	print $q->header();
	my $bodyFile = "previousRunsBody.html";
	open(BODY,"<$bodyFile") or die "Can't open $bodyFile: $!";
	while(<BODY>){
		print $_;
	}

	# Get previous runs list and add links
	updateElementById_append("prevRunList","<ul>");
	my $prevRunsDir = '../dropbox';
	opendir(PREVIOUS_RUNS,$prevRunsDir);
	my @runs = readdir(PREVIOUS_RUNS);
	@runs = sort(@runs);
	#while(my $fName = readdir(PREVIOUS_RUNS)){
	foreach(@runs){
		if($_ !~ /^\.+$/){ # exclude '.' and '..'
			if(-M "$prevRunsDir/$_" < 31){
				updateElementById_append("prevRunList","<li><a href=\\\"javascript:void(0);\\\" onclick=\\\"javascript:readResults('$prevRunsDir/$_/patient_seqs.results.html','#previousRunInfo');\\\">$_</a></li>");
			}
		}
	}
	closedir(PREVIOUS_RUNS);
	updateElementById_append("prevRunList","</ul>");

	print $q->end_html;
}

sub updateElementById_replace {
	my $element = shift;
	my $output = shift;
print <<END_HTML;
	<script type="text/javascript">jQuery("#$element").html("$output");</script>
END_HTML
}

sub updateElementById_append {
	my $element = shift;
	my $output = shift;
print <<END_HTML;
	<script type="text/javascript">jQuery("#$element").append("$output");</script>
END_HTML
}

