package Patient;
use strict;
##################################################
## the object constructor (simplistic version)  ##
##################################################
sub new {
	my $self  = {};
	$self->{ACCESSION}		= undef;
	$self->{NAME}			= undef;
	$self->{RUN}			= undef;
	$self->{POSITION}	= undef;
	$self->{TEST} 			= undef;
	$self->{SEX}			= undef;
	$self->{AGE}			= undef;

	# This variable will be used to keep track of whether this patient is in the datbase. Patients
	# are not included in database if the sequence is 'indeterminate' (untraceable levels).
	$self->{IN_DATABASE}	= undef; 
	# Keep track of whether there are any invalid characters
	$self->{VALID_CHARS}	= undef; 

	bless($self);           # but see below
	return $self;
}
##############################################
## methods to access per-object data        ##
##                                          ##
## With args, they set the value.  Without  ##
## any, they only retrieve it/them.         ##
##############################################
sub accession {
	my $self = shift;
	if (@_) { $self->{ACCESSION} = shift }
	return $self->{ACCESSION};
}

sub name {
	my $self = shift;
	if (@_) { $self->{NAME} = shift }
	return $self->{NAME};
}

sub run {
	my $self = shift;
	if (@_) { $self->{RUN} = shift }
	return $self->{RUN};
}

sub position {
	my $self = shift;
	if (@_) { $self->{POSITION} = shift }
	return $self->{POSITION};
}

sub test {
	my $self = shift;
	if (@_) { $self->{TEST} = shift }
	return $self->{TEST};
}

sub sex {
	my $self = shift;
	if (@_) { $self->{SEX} = shift }
	return $self->{SEX};
}

sub age {
	my $self = shift;
	if (@_) { $self->{AGE} = shift }
	return $self->{AGE};
}

sub inDatabase {
	my $self = shift;
	if (@_) { $self->{IN_DATABASE} = shift }
	return $self->{IN_DATABASE};
}

sub validChars {
	my $self = shift;
	if (@_) { $self->{VALID_CHARS} = shift }
	return $self->{VALID_CHARS};
}
1;  # so the require or use succeeds
