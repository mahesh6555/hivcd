#!/usr/bin/perl -w
use warnings;
use strict;
use CGI; 
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
use DBI;
use Data::Dumper;
use IO::Handle;
use Time::Local;
use DateTime;
use lib '/var/www/html/HIV_Contamination_Detection/cgi';
use Patient;
use html_header;
use Text::Chomp;
use CGI::Session ( '-ip_match' );

STDOUT->autoflush;
$Data::Dumper::Useqq = 1; # shows all non-printable characters
$CGI::POST_MAX = 1024 * 15000;

my $q = new CGI; 
my $session = CGI::Session->load();
my %allPatientsHash;

if($session->is_expired){
	html_header->refreshHeader($q, "Your session has expired");
}
elsif($session->is_empty){
	html_header->refreshHeader($q, "You have not logged in");
}
else{

	print $q->header(); 

	###################
	# Print html body #
	###################
	my $bodyFile = "alignmentBody.html";
	open(BODY,"<$bodyFile") or die "Can't open $bodyFile: $!";
	while(<BODY>){
		print $_;
	}


	#################
	# Setup time... #
	#################
	my @months = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);
	my @weekDays = qw(Sun Mon Tue Wed Thu Fri Sat Sun);
	my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime();
	my $year = 1900 + $yearOffset;

	###########################
	# Create upload directory #
	###########################
	#my $upload_dir = "../dropbox/$dayOfMonth$months[$month]$year\.$hour\.$minute\.$second";
	my $upload_dir = "../dropbox/$months[$month].$dayOfMonth.$year.$hour:" . (($minute < 10) ? "0$minute" : "$minute") . ":" . (($second < 10) ? "0$second" : "$second");
	mkdir($upload_dir);
	chmod(0755,$upload_dir);

	fileparse_set_fstype("MSWin32"); # set file path type to Windows since most users will be using windows
	my ( $filename, $filePath, $fileExt) = fileparse ( $q->param("sequenceData"), qr/\.[^.]*/ );
	fileparse_set_fstype("Unix"); # set back to unix

	my $fullFileName = "$filename$fileExt";
	my $currPatientsFile = "$filename-curr_patients.txt";
	#my $filename = $q->param("sequenceData"); 

	# If file does not upload correctly, fail
	if(!$fullFileName){
		print $q->header();
		print "Error uploading file: $!<br>";
		exit;
	}

	clean_file_name($fullFileName);

	#################################################
	# Get handle on the temp file created by CGI.pm #
	#################################################
	my $upload_filehandle = $q->upload("sequenceData");
	open ( PATIENTFILE, ">$upload_dir/$fullFileName" ) or die "$!";  
	binmode PATIENTFILE;  # binmode tells Perl to write the file in binary rather than text to avoid corruption on non-UNIX servers


	########################
	# Extract patient data #
	########################
	my ($patient,$accession);
	my $runNum;
	while ( <$upload_filehandle> ){  
		# patient data is delimited by pipes ('|')
		my @tmp = split (/\|/, $_);
		$accession = $tmp[0];
		$accession =~ s/-//g; # remove dashes from accession
		if($accession =~ /\d{11}/){ # omit QC wells from patient data

			$patient = Patient->new();
			$patient->accession($accession);
			$patient->name($tmp[2]);
			$patient->run($runNum);
			$patient->position($tmp[1]);
			$patient->test($tmp[3]);
			$patient->age($tmp[6]);
			$patient->sex($tmp[7]);
			$patient->inDatabase("False"); # Will use this value to determine if each patient's sequence is included in the sequences downloaded from database
			$patient->validChars("True"); # Assume sequence has only valid characters

			$allPatientsHash{$accession} = $patient;

		}
		elsif($tmp[1] =~ /SEQID_HIV_(\d+)/){
			$runNum = $1;
		}
		print PATIENTFILE;
	}  
	close PATIENTFILE;

	############
	# Get date #
	############
	my $beginDate = $q->param("beginDate"); 
	my $endDate = $q->param("endDate"); 
	
	my $cutoff = $q->param("cutoff");

	my $dt = createDateTimeObjectFromMMDDYYYY($beginDate);
	$dt =~ /^(\d{4}-\d{2}-\d{2})T.+$/;
	my $stDate = $1;
	
	my $dt2 = createDateTimeObjectFromMMDDYYYY($endDate);
	$dt2 =~ /^(\d{4}-\d{2}-\d{2})T.+$/;
	my $enDate = $1;

	updateElementById_append("progressText","Accessing sequence database ($stDate - $enDate) ... ");

	######################
	# Open DB connection #
	######################
	# Server settings stored in /private/etc/odbc.ini
	my $data_source = q/DBI:ODBC:<SERVER_NAME>/;  # Production server
	my $user = q/<DB_USER_NAME>/;
	my $pass = q/<DB_PASSWORD>/;
	my $db = DBI->connect($data_source,$user,$pass,{PrintError => 1, RaiseError => 1, LongTruncOk=>1}) or die "Can't connect to $data_source: $db::errstr";
	my $sqlQuery = $db->prepare('SELECT * from <INSERT_TABLE_NAME> where sequence_date >= ? and sequence_date <= ?');

	$sqlQuery->execute($dt, $dt2) or die "Couldn't execute statement: " . $sqlQuery->errstr;

	updateElementById_append("progressText","Done.");
	updateElementById_append("progressText","<br>Preparing data ... ");


	#####################################
	# Print query results to file--This #
	# is the data to be aligned. Also   #
	# check if the patient data	    	#
	# uploaded is included in the	    #
	# database.		            		#
	#			            			#
	# Finally, generate a file of       #
	# patients from this run that also  #
	# have data in the database. This   #
	# information will be passed to the #
	# percent identity calculator       #
	#####################################
	open ( PATIENTFILE1, ">$upload_dir/$currPatientsFile" ) or die "$!";
	binmode PATIENTFILE1;

	my $dataToAlign = "$upload_dir/patient_seqs.fa";
	open(SEQFILE, ">$dataToAlign") or die "Can't open file ($dataToAlign): $!<br>";
	my $safe_sequence_characters = "atgcurykmswbdhvn"; # allowed sequence values -- includes ambiguous characters
	my $recordCount = 0;
	while(my @data = $sqlQuery->fetchrow_array()){
		my ($seq,$accession);
		$recordCount++;
		$accession = $data[1];
		$seq = $data[4];
		if($seq =~ /^([$safe_sequence_characters]+)$/i){ # if only allowed characters, save sequence. 'i' = Ignore case.
			print SEQFILE ">$accession\n$seq\n";
			if(exists $allPatientsHash{$accession}){
				$allPatientsHash{$accession}->inDatabase("True");
				print PATIENTFILE1 "$accession\n"; # Write accession numbers from current run to file if data is in database
			}
		}
		else{
			if(exists $allPatientsHash{$accession}){
				$allPatientsHash{$accession}->validChars("False");
				$allPatientsHash{$accession}->inDatabase("True");
				print PATIENTFILE1 "$accession\n"; # Write accession numbers from current run to file if data is in database
			}
			updateElementById_replace("warningHeader","<h3>Warnings</h3>");
			updateElementById_append("warningText","<span style=color:red;font-size:.450em>Warning: \'$accession\' contains invalid nucleotide characters. Removing.</span><br>");
		}
	}
	close SEQFILE;
	close PATIENTFILE1;

	$db->disconnect();

	###################################################
	# If no data received from database, throw error. #
	###################################################
	my $canAlign = 1;
	if($recordCount == 0){
		updateElementById_replace("warningHeader","<h3>Warnings</h3>");
		updateElementById_append("warningText","<span style=color:red;font-size:.450em>ERROR: No data retrieved from database. Check your date range.</span><br>");
		updateElementById_append("warningText","<span style=color:red;font-size:.450em>Stopping ...</span><br>");
		$canAlign = 0;
	}

	my ( $dataToAlignName, $dataToAlignPath, $dataToAlignExtension ) = fileparse ( $dataToAlign, '\..*' );  
	my $alignedData = "$dataToAlignPath$dataToAlignName.aligned.fa";
	my $output = "$dataToAlignPath$dataToAlignName-percIds.txt";
	updateElementById_append("progressText","Done.");
	if($canAlign){
		my $startTime = time();
		my $currAlignTime = 0;

		updateElementById_append("progressText","<br>Creating multiple sequence alignment (MSA) ... ");
		$currAlignTime = alignSequences($dataToAlign,$alignedData,$startTime,$currAlignTime);
		updateElementById_append("progressText","Done.");

		updateElementById_append("progressText","<br>Calculating percent identities ... ");
		$currAlignTime = calculatePercentIds($alignedData,$output,$startTime,$currAlignTime,"$upload_dir/$currPatientsFile", $cutoff);
		updateElementById_append("progressText","Done.");
	}
	else{
		updateElementById_replace("warningHeader","<h3>Warnings</h3>");
		updateElementById_append("warningText","<span style=color:red;font-size:.450em>Stopped.</span><br>");
	}

	# Finish the page
	print $q->end_html;
}

sub calculatePercentIds {
	my $alignedDataFile = shift;
	my $output = shift;
	my $startTime = shift;
	my $currAlignTime = shift;
	my $currPatientsFile = shift;
	my $cutoff = shift;
	open(CALC_PERC_IDS,"java -classpath ../java/ CalculatePercentIdentityEngine $alignedDataFile $currPatientsFile $cutoff |") or die "Could not calculate percent identities: $!<br>";

	removeElementById("dmatrix2");
	removeElementById("upgma2");
	removeElementById("progAlignment2");
	updateElementById_replace("step","<h3>Calculating % IDs</h3>");

	my ($readLength,$output);
	my $currTime;
	my ($percent,$currentPercent) = (0,0);
	my @splitOutput;
	my @results;
	create_alignment_progress_bar("alignmentPercentIdAlignmentProgressBar","percentIdProgBar"); # Need unique identifier
	while($readLength = sysread(CALC_PERC_IDS,$output,300)){
		@splitOutput = split(/[\r\n]/,$output);
		foreach(@splitOutput){
			$currTime = time();
			$currAlignTime = update_alignment_timer(($currTime-$startTime),$currAlignTime);
			if($_ =~ /(\d+) \/ (\d+)/){
				if($1 > 0 && $2 > 0){
					$percent = int($1/$2 * 100);
					$currentPercent = update_progress_bar($percent, $currentPercent);
				}
				updateElementById_replace("alignmentPercentIdAlignmentProgressText","$1 / $2");
			}
			elsif($_ =~ /^(\d{11}),(\d{11}),(\d+\.*\d*)/){
				if(exists $allPatientsHash{$1} || exists $allPatientsHash{$2}){
					push (@results, "$1,$2,$3"); # push array of 'accession1','accession2','percentIdentity'
				}
			}
		}
	}
	close CALC_PERC_IDS;
	printResults($alignedDataFile,@results);
	return $currAlignTime;
}

sub alignSequences {
	my $filein = shift;
	my $fileout = shift;
	my $startTime = shift;
	my $currAlignTime = shift;

	my ( $fileOutName, $fileOutPath, $fileOutExtension ) = fileparse ( $fileout, '\..*' );  
	open(OUTFILE,">$fileOutPath/Dump.txt");
	open(MSA,"/home/markebbert/bin/mafft --retree 2 2>&1 $filein 1> $fileout |") or die "MSA failed: $!<br>";
	my ($data, $percent);
	my $readLength;

	# Start timer
	my $currTime;
	my @splitOutput;
	my $currentPercent=0; # progress bar percentage.
	my ($dmatrixNum, $upgmaNum, $progAlignmentNum) = (0,0,0);
	my $currElement;
	$currAlignTime = update_alignment_timer("0",$currAlignTime);
	while($readLength = sysread(MSA,$data,300)){
		@splitOutput = split(/[\r\n]/,$data);
		foreach(@splitOutput){
			$currTime = time();
			$currAlignTime = update_alignment_timer(($currTime-$startTime),$currAlignTime);
			print OUTFILE Dumper($_);
			if($_ =~ /\s*(\d+)\s*\/\s*(\d+)/){
				print OUTFILE Dumper("1: $1, 2: $2");
				if($1 > 0 && $2 > 0){
					$percent = int($1/$2 * 100);
					$currentPercent = update_progress_bar($percent,$currentPercent);
				}
				print OUTFILE Dumper($percent);
				updateElementById_replace($currElement."AlignmentProgressText","$1 / $2");
			}
			elsif($_ =~ /Making a distance matrix \.\./){ # mafft only prints two periods here.
				++$dmatrixNum;
				if($dmatrixNum == 1){
					updateElementById_replace("step","<h3>MSA - Step 1</h3>");
				}
				else{
					removeElementById("dmatrix1");
					removeElementById("upgma1");
					removeElementById("progAlignment1");
					updateElementById_replace("step","<h3>MSA - Step 2</h3>");
				}
				$currElement = "dmatrix" . $dmatrixNum;
				$currentPercent=0; # reset progress bar percentage.
				updateElementById_append($currElement."Text","Making a distance matrix ...");
				create_alignment_progress_bar($currElement."AlignmentProgressBar","dmatrix$currTime"); # Need unique identifier
			}
			elsif($_ =~ /Constructing a UPGMA tree \.\.\./){
				++$upgmaNum;
				$currElement = "upgma" . $upgmaNum;
				$currentPercent=0; # reset progress bar percentage.
				updateElementById_append($currElement."Text","Constructing UPGMA tree ...");
				create_alignment_progress_bar($currElement."AlignmentProgressBar","upgmaTree$currTime"); # Need unique identifier
			}
			elsif($_ =~ /Progressive alignment \.\.\./){
				++$progAlignmentNum;
				$currElement = "progAlignment" . $progAlignmentNum;
				$currentPercent=0; # reset progress bar percentage.
				updateElementById_append($currElement."Text","Progressive alignment ...");
				create_alignment_progress_bar($currElement."AlignmentProgressBar","progAlignment$currTime"); # Need unique identifier
			}
		}
	}
	if(!defined $readLength){
		die "Error reading MAFFT output: $!";
	}
	close MSA;
	return $currAlignTime;
}

sub printResults {
	my $alignedDataFile = shift;
	my @results = @_;
	my @accResults;
	my @line;
	my ($acc1,$acc2,$percId);
	my ($run,$patientName,$patientAcc,$position);

	my ( $alignedDataFileName, $alignedDataFilePath, $alignedDataFileExtension ) = fileparse ( $alignedDataFile, '\..*' );  
	open(RESULTS_OUTPUT,">$alignedDataFilePath/$alignedDataFileName.results.html") or die "Could not open $alignedDataFilePath/$alignedDataFileName.results.txt: $!<br>";

	# Create directory for individual comparisons
	my $individualComparisonsPath = "$alignedDataFilePath/IndividualComparisons";
	mkdir($individualComparisonsPath);
	chmod(0755,$individualComparisonsPath);

	my %alignedDataHash = readAlignedData($alignedDataFile); # Aligned Data hashed by accession number

	##############################
	# Order patients by position #
	##############################
	my %patientsByPositionHash;
	while( my($acc, $patient) = each %allPatientsHash){
		$patientsByPositionHash{$patient->position()} = $patient;
		if(!defined $run){
			$run = $patient->run();
		}
	}

	updateElementById_append("results","<h3>Results</h3>");
	updateElementById_append("results","<table id=\\\"resultsTable\\\" border=\\\"1\\\" rules=\\\"rows\\\" frame=\\\"hsides\\\" cellpadding=\\\"5\\\">");
	updateElementById_append("resultsTable","<tr><th style=\\\"color:#ffadf8\\\">Accession (Run $run)</th><th style=\\\"color:#ffadf8\\\">Patient Name</th><th style=\\\"color:#ffadf8\\\">Position</th><th>Matching Accession</th><th>% ID</th></tr>");
	print RESULTS_OUTPUT "<table id=\"resultsTable\" border=\"1\" rules=\"rows\" frame=\"hsides\" cellpadding=\"5\">\n";
	print RESULTS_OUTPUT "\t<tr><th style=\"color:#ffadf8\">Accession (Run $run)</th><th style=\"color:#ffadf8\">Patient Name</th><th style=\"color:#ffadf8\">Position</th><th>Matching Accession</th><th>% ID</th></tr>\n";


	#####################
	# Print out results #
	#####################
	my $patient;
	for my $position (sort {$a <=> $b} keys %patientsByPositionHash){
		$patient = $patientsByPositionHash{$position};
		$patientName = $patient->name();
		$patientAcc = $patient->accession();
		$position = $patient->position();
		@accResults = getResults($patientAcc,@results);


		foreach(@accResults){
			@line = split(/,/);
			$acc1 = $line[0];
			$acc2 = $line[1];
			$percId = $line[2];

			printComparison($individualComparisonsPath,$acc1,$acc2,$percId,$alignedDataHash{$acc1},$alignedDataHash{$acc2});

			my $individualComparisonFile = $acc1 . "_vs_" . $acc2 . ".fa";
			my $header = "<h3>$patientName ($patientAcc) vs $acc2 - $percId%</h3>";

			if(exists $allPatientsHash{$acc1} && exists $allPatientsHash{$acc2}){
				updateElementById_append("resultsTable",
					"<tr>" .
						"<td style=\\\"color:red\\\">$patientAcc</td>" .
						"<td style=\\\"color:red\\\">$patientName</td>" .
						"<td style=\\\"color:red\\\">$position</td>" .
						"<td style=\\\"color:red\\\">$acc2</td>" .
						"<td style=\\\"color:red\\\">$percId</td>" .
						"<td><a href=\\\"javascript:void(0);\\\" onclick=\\\"javascript:compareAlignment('$individualComparisonsPath/$individualComparisonFile','$header');\\\">Compare</a></td>" .
					"</tr>");
				print RESULTS_OUTPUT 
					"\t<tr>" .
						"<td style=\"color:red\">$patientAcc</td>" .
						"<td style=\"color:red\">$patientName</td>" .
						"<td style=\"color:red\">$position</td>" .
						"<td style=\"color:red\">$acc2</td>" .
						"<td style=\"color:red\">$percId</td>" .
						"<td><a href=\"javascript:void(0);\" onclick=\"javascript:compareAlignment('$individualComparisonsPath/$individualComparisonFile','$header');\">Compare</a></td>" .
					"</tr>\n";
			}

			elsif(exists $allPatientsHash{$acc1}){
				updateElementById_append("resultsTable",
					"<tr>" .
						"<td style=\\\"color:#ffadf8\\\">$patientAcc</td>" .
						"<td style=\\\"color:#ffadf8\\\">$patientName</td>" .
						"<td style=\\\"color:#ffadf8\\\">$position</td>" .
						"<td>$acc2</td>" .
						"<td>$percId</td>" .
						"<td><a href=\\\"javascript:void(0);\\\" onclick=\\\"javascript:compareAlignment('$individualComparisonsPath/$individualComparisonFile','$header');\\\">Compare</a></td>" .
					"</tr>");
				print RESULTS_OUTPUT 
					"\t<tr>" .
						"<td style=\"color:#ffadf8\">$patientAcc</td>" .
						"<td style=\"color:#ffadf8\">$patientName</td>" .
						"<td style=\"color:#ffadf8\">$position</td>" .
						"<td>$acc2</td>" .
						"<td>$percId</td>" .
						"<td><a href=\"javascript:void(0);\" onclick=\"javascript:compareAlignment('$individualComparisonsPath/$individualComparisonFile','$header');\">Compare</a></td>" .
					"</tr>\n";
			}
			elsif(exists $allPatientsHash{$acc2}){
				updateElementById_append("resultsTable",
					"<tr>" .
						"<td style=\\\"color:#ffadf8\\\">$patientAcc</td>" .
						"<td style=\\\"color:#ffadf8\\\">$patientName</td>" .
						"<td style=\\\"color:#ffadf8\\\">$position</td>" .
						"<td>$acc1</td>" .
						"<td>$percId</td>" .
						"<td><a href=\\\"javascript:void(0);\\\" onclick=\\\"javascript:compareAlignment('$individualComparisonsPath/$individualComparisonFile','$header');\\\">Compare</a></td>" .
					"</tr>");
				print RESULTS_OUTPUT 
					"\t<tr>" .
						"<td style=\"color:#ffadf8\">$patientAcc</td>" .
						"<td style=\"color:#ffadf8\">$patientName</td>" .
						"<td style=\"color:#ffadf8\">$position</td>" .
						"<td>$acc1</td>" .
						"<td>$percId</td>" .
						"<td><a href=\"javascript:void(0);\" onclick=\"javascript:compareAlignment('$individualComparisonsPath/$individualComparisonFile','$header');\">Compare</a></td>" .
					"</tr>\n";
			}
		}
		if($#accResults < 0){ # if there are no results
			if($patient->inDatabase() eq "False"){ # if data is not in database
				updateElementById_append("resultsTable",
					"<tr>" .
						"<td style=\\\"color:red\\\"><span style=\\\"color:#ffadf8\\\">$patientAcc</span>-<b>Data Unavailable</b></td>" .
						"<td style=\\\"color:red\\\"><span style=\\\"color:#ffadf8\\\">$patientName</span>-<b>Data Unavailable</b></td>" .
						"<td style=\\\"color:#ffadf8\\\">$position</td>" .
						"<td style=\\\"color:red\\\">NA</td>" .
						"<td style=\\\"color:red\\\">NA</td>" .
					"</tr>");
				print RESULTS_OUTPUT 
					"\t<tr>" .
						"<td style=\"color:red\"><span style=\\\"color:#ffadf8\\\">$patientAcc</span>-<b>Data Unavailable</b></td>" .
						"<td style=\"color:red\"><span style=\\\"color:#ffadf8\\\">$patientName</span>-<b>Data Unavailable</b></td>" .
						"<td style=\"color:#ffadf8\">$position</td>" .
						"<td style=\"color:red\">NA</td>" .
						"<td style=\"color:red\">NA</td>" . 
					"</tr>\n";
			}
			elsif($patient->inDatabase() eq "True"){ # if is in database
				if($patient->validChars() eq "False"){ # The data is there, but contains invalid characters
					updateElementById_append("resultsTable",
						"<tr>" .
							"<td style=\\\"color:red\\\"><span style=\\\"color:#ffadf8\\\">$patientAcc</span>-<b>Invalid Sequence Characters</b></td>" .
							"<td style=\\\"color:red\\\"><span style=\\\"color:#ffadf8\\\">$patientName</span>-<b>Invalid Sequence Characters</b></td>" .
							"<td style=\\\"color:#ffadf8\\\">$position</td>" .
							"<td style=\\\"color:red\\\">NA</td>" .
							"<td style=\\\"color:red\\\">NA</td>" .
						"</tr>");
					print RESULTS_OUTPUT 
						"\t<tr>" .
							"<td style=\"color:red\"><span style=\\\"color:#ffadf8\\\">$patientAcc</span>-<b>Invalid Sequence Characters</b></td>" .
							"<td style=\"color:red\"><span style=\\\"color:#ffadf8\\\">$patientName</span>-<b>Invalid Sequence Characters</b></td>" .
							"<td style=\"color:#ffadf8\">$position</td>" .
							"<td style=\"color:red\">NA</td>" .
							"<td style=\"color:red\">NA</td>" .
						"</tr>\n";
				}
				else{ # There were no hits.
					updateElementById_append("resultsTable",
						"<tr>" .
							"<td style=\\\"color:#ffadf8\\\">$patientAcc</td>" .
							"<td style=\\\"color:#ffadf8\\\">$patientName</td>" .
							"<td style=\\\"color:#ffadf8\\\">$position</td>" .
							"<td>No Hits</td>" .
							"<td>NA</td>" .
						"</tr>");
					print RESULTS_OUTPUT 
						"\t<tr>" .
							"<td style=\"color:#ffadf8\">$patientAcc</td>" .
							"<td style=\"color:#ffadf8\">$patientName</td>" .
							"<td style=\"color:#ffadf8\">$position</td>" .
							"<td>No Hits</td>" .
							"<td>NA</td>" .
						"</tr>\n";
				}
			}
			else{
				updateElementById_append("resultsTable",
					"<tr>" .
						"<td style=\\\"color:red\\\">UNEXPECTED ERROR: Contact Admin!</td>" .
						"<td style=\\\"color:red\\\">UNEXPECTED ERROR: Contact Admin!</td>" .
						"<td style=\\\"color:red\\\">UNEXPECTED ERROR: Contact Admin!</td>" .
						"<td>No Hits</td>" .
						"<td>NA</td>" .
					"</tr>");
			}
		}
	}
	updateElementById_append("results","</table>");
	print RESULTS_OUTPUT "</table>\n";

	###############################################
	# Remove all result files older than 60 days! #
	###############################################
	system("find ../dropbox -mtime +60 -exec rm -r {} \\;");
}

#######################################################
# Each value is a string 'acc1,acc2,percentId'. Check #
# if 'accession' is the first acc in the string.      #
#######################################################
sub getResults {
	my $accession = shift;
	my @accResults;
	foreach(@_){
		if($_ =~ /^$accession/i){
			push(@accResults, $_);
		}
	}
	return @accResults;
}

############################
# Read aligned data into a #
# hash by accession number #
############################
sub readAlignedData {
	my $alignedDataFile = shift;

	my $accession;
	my $seq;
	my %seq_hash;

	open(ALIGNEDDATA, "<$alignedDataFile") or die "Can't open $alignedDataFile: $!\n";
	while(<ALIGNEDDATA>){
		$_ = tchomp($_);
		if($_ =~ /^>(.+)$/){
			if(defined($accession)){ # if I already have a value (this isn't the first seq)
				$seq_hash{$accession} = $seq;
				$seq = ""; 
			}   
			$accession = $1; # get the Sequence name
		}   
		elsif($_ =~ /^\s*$/){ # check for blank lines (or just whitespace)
			next;
		}   
		else{ # collect the sequence
			$seq .= $_; 
		} 
	}
	close(ALIGNEDDATA);
	return %seq_hash;
}

sub printComparison {
	my $individualComparisonsPath = shift;
	my $acc1 = shift;
	my $acc2 = shift;
	my $percId = shift;
	my @acc1AlignedSequence = split(//,shift);
	my @acc2AlignedSequence = split(//,shift);

	for(my $i = 0; $i <= $#acc1AlignedSequence; $i++){
		if($acc1AlignedSequence[$i] ne $acc2AlignedSequence[$i]){
			$acc1AlignedSequence[$i] = "<b style='color:red'>$acc1AlignedSequence[$i]</b>";
			$acc2AlignedSequence[$i] = "<b style='color:red'>$acc2AlignedSequence[$i]</b>";
		}
	}

	my $file = "$individualComparisonsPath/$acc1" . "_vs_" . "$acc2.fa";
	open(INDIVIDCOMP,">$file") or die "Can't open $file: $!\n";
	#print INDIVIDCOMP "$acc1 $acc2 $percId" . $q->br();
	#print INDIVIDCOMP "$acc1: @acc1AlignedSequence\n$acc1: @acc2AlignedSequence\n";
	#print INDIVIDCOMP "$acc1" . $q->br();
	my $lineLength = 100;
	my $posInterval= 10; # How frequenty to print position number

	my $j = 0;
	my $i = 0;
	for(my $k = 0; $k <=$#acc1AlignedSequence; $k++){
		if($k > 0 && ($k+1) % $posInterval == 0){
			print INDIVIDCOMP "<font style='color:#ffadf8'>|</font>";
		}
		else{
			print INDIVIDCOMP "&nbsp;";
		}
		if( ($k > 0 && ($k+1) % $lineLength == 0) || $k == $#acc1AlignedSequence){
			print INDIVIDCOMP $q->br();

			for(; $i <= $#acc1AlignedSequence; $i++){
				print INDIVIDCOMP "$acc1AlignedSequence[$i]";
				if( ($i > 0 && ($i+1) % $lineLength == 0) || $i == $#acc1AlignedSequence){ 
					print INDIVIDCOMP $q->br();

					for(; $j <= $#acc2AlignedSequence;$j++){
						print INDIVIDCOMP "$acc2AlignedSequence[$j]";
						if($j > 0 && ($j+1) % $lineLength == 0){
							print INDIVIDCOMP $q->br() . $q->br();
							$j++;
							last;
						}
					}
					$i++;
					last;
				}
			}
		}
	}
	close(INDIVIDCOMP);
}

sub updateElementById_replace {
	my $element = tchomp(shift);
	my $output = tchomp(shift);
print <<END_HTML;
	<script type="text/javascript">jQuery("#$element").html("$output");</script>
END_HTML
}

sub updateElementById_append {
	my $element = tchomp(shift);
	my $output = tchomp(shift);
print <<END_HTML;
	<script type="text/javascript">jQuery("#$element").append("$output");</script>
END_HTML
}

sub removeElementById {
	my $element = shift;
print <<END_HTML;
	<script type="text/javascript">jQuery("#$element").remove();</script>
END_HTML
}

sub update_progress_bar {
	my $output = tchomp(shift);
	my $currentPercent = tchomp(shift);
	if($output > $currentPercent){
		$currentPercent = $output;
print <<END_HTML;
		<script type="text/javascript">alignmentProgBar.setPercentage($output);</script>
END_HTML
	}
	return $currentPercent;
}

sub update_alignment_timer {
	my $output = shift;
	my $currAlignTime = shift;
	if($output > $currAlignTime){
		$currAlignTime = $output;
		my $minutes = int($currAlignTime / 60);
		my $seconds = $currAlignTime % 60;
		if($seconds < 10){
			$seconds = "0$seconds";
		}
		if($minutes < 10){
			$minutes = "0$minutes";
		}
print <<END_HTML;
		<script type="text/javascript">jQuery("#alignmentTimer").html("Elapsed Time: $minutes:$seconds");</script>
END_HTML
	}
	return $currAlignTime;
}

sub create_alignment_progress_bar {
	my $elementId = shift;
	my $progBarId = shift;
print <<END_HTML;
	<script type="text/javascript">jQuery("#$elementId").append('<span id="$progBarId"></span>');</script>
	<script type="text/javascript">
		// multicolor (take all other default parameters)
		alignmentProgBar = new JS_BRAMUS.jsProgressBar(
					\$('$progBarId'),
					0,
					{
						barImage	: Array(
							'../images/bramus/percentImage_back4.png',
							'../images/bramus/percentImage_back3.png',
							'../images/bramus/percentImage_back2.png',
							'../images/bramus/percentImage_back1.png'
						),
					}
				);
	</script>
END_HTML
}

sub clean_file_name {
	my $filename = shift;
	# Split the filename into name, path and extension
	my ( $name, $path, $extension ) = fileparse ( $filename, '\..*' );  
	$filename = $name . $extension;

	my $safe_filename_characters = "a-zA-Z0-9_.-";
	$filename =~ tr/ /_/; # replace spaces with underscore for ease in URL
	$filename =~ s/[^$safe_filename_characters]//g; # Remove any 'unsafe' characters

	# Just double check that there are no 'unsafe' characters
	if ( $filename =~ /^([$safe_filename_characters]+)$/ ){  
		$filename = $1;  
	}else{  
		# Should never execute since all of the 'unsafe' characters have been
		# removed, but just in case...
		die "Filename contains invalid characters";  
	}
}

sub createDateTimeObjectFromMMDDYYYY {
	my $beginDate = shift;
	my @mmddyyyy = split(/[\/-]/,$beginDate);
	my $mm = $mmddyyyy[0] - 1; # subtract one. timelocal uses months since january, so january is month 0;
	my $dd = $mmddyyyy[1]; # dd is the actual day of the month. It is not zero-indexed;
	my $yyyy = $mmddyyyy[2];
	my $epochBeginDate = timelocal(0,0,0,$dd,$mm,$yyyy); # timelocal($sec,$min,$hours,$day,$month,$year);
	my $dt = DateTime->from_epoch( epoch => $epochBeginDate );
	return $dt;
}

=cut
sub tchomp {
	my $text = shift;
	# Matching with the hex values for the various line separators
	$text =~ s/^(.*?)(?:\x0D\x0A|\x0A|\x0D|\x0C|\x{2028}|\x{2029})*$/$1/s;
	return $text;
}
=cut

