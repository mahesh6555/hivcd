#!/usr/bin/perl -w
use warnings;
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $q = new CGI;
my $filename = $q->param("filename");
open(RESULTS, $filename) or die "Can't open $filename: $!\n";
print "Content-type: text/html\n\n";
while(<RESULTS>){
	print $_;
}
close(RESULTS);
