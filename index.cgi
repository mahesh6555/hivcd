#!/usr/bin/perl
  
  # index.pl
  use warnings;
  use strict;
  use CGI;
  use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
  use CGI::Session ( '-ip_match' );
  use lib '/home/shaned/webroot/html/HIV_Contamination_DetectionCopy/cgi/';
  use html_header;
  
  my $session = CGI::Session->load();
  my $q = new CGI;
  
  print "Hello World Welcome<br/>" ;
	if($session->is_expired){
		html_header->refreshHeader($q, "Your session has expired");
	}
	elsif($session->is_empty){
		html_header->refreshHeader($q, "You have not logged in");
	}
	else
	{
		print $q->header(-cache_control=>"no-cache, no-store, must-revalidate");
		print "here";
		html_header->head();
		html_header->html_title("");
		html_header->calendar();
		html_header->endHead();
	  
print <<HTML;
		<body>
		<div id="container"><!-- Start container -->
			
			<div id="pageHeader"><!-- Start page header -->
				<img src="rw_common/images/ARUP-logo-small.png" width="91" height="49" alt="Site logo"/>
				<h1>ARUP</h1>
				<h2>HIV Contamination Detection</h2>
				<a href='login.cgi?action=logout'>Logout</a>
			</div><!-- End page header -->
			
			<div id="sidebarContainer"><!-- Start Sidebar wrapper -->
				<div id="navcontainer"><!-- Start Navigation -->
					<ul><li><a href="index.cgi" rel="self" id="current">Upload Sequence Run</a></li>
					<li><a href="cgi/previousRuns.cgi" rel="self">Previous Runs</a></li></ul>
				</div><!-- End navigation --> 
				
				<div id="sidebar"><!-- Start sidebar content -->
					<h1 class="sideHeader">Some Valuable Information</h1><!-- Sidebar header -->
					 <br /><!-- sidebar content you enter in the page inspector -->
					 Here is some valuable information.
					 <!-- sidebar content such as the blog archive links -->
				</div><!-- End sidebar content -->
			</div><!-- End sidebar wrapper -->
			
			<div id="contentContainer"><!-- Start main content wrapper -->
				<div id="content"><!-- Start content -->
					<div id="breadcrumbcontainer"><!-- Start the breadcrumb wrapper -->
						
					</div><!-- End breadcrumb -->
					<h2>Upload Run Data</h2>
					<p>
						Choose a sequence run data file (.dat) to test for contamination. You may
						also choose a begin date for runs to compare against. Default date range is six months
						before today.
					</p>
					<br>
					<h3>Select a date range:</h3>
					<form action="cgi/upload.cgi" method="post" name="alignment" enctype="multipart/form-data">  
						Begin date:
						<INPUT TYPE="text" NAME="beginDate" id="beginDate" VALUE="" SIZE=10>

						<A HREF="#"
						   onClick="cal.select(document.forms['alignment'].beginDate,'anchor1','MM/dd/yyyy'); return false;"
							  NAME="anchor1" ID="anchor1"
							  style="margin-right: 21px;"
							  >select</A>
						End date:
						<INPUT TYPE="text" NAME="endDate" id="endDate" VALUE="" SIZE=10>
						
						<A HREF="#"
						   onClick="cal.select(document.forms['alignment'].endDate,'anchor2','MM/dd/yyyy'); return false;"
							  NAME="anchor2" ID="anchor2">select</A>
						<!-- <br/><br/>Percent ID cutoff:<select name="cutoff">
							<option  value="99">99</option>
							<option  value="98">98</option>
							<option  value="97">97</option>
							<option selected='true' value="96">96</option>
							<option  value="95">95</option>
							<option  value="94">94</option>
							<option  value="93">93</option>
							<option  value="92">92</option>
							<option  value="91">91</option>
							<option  value="90">90</option>
						</select> -->
						<br/><br/>Percent ID cutoff:
						<INPUT TYPE="text" NAME="cutoff" ID="cutoff" VALUE="96" SIZE=5>

					<!-- Set default dates -->
					<script type="text/javascript">
						
						
						getDate = function(el, number) 
						{
							var today = new Date();
							var dd = today.getDate();
							var mm = today.getMonth()+1;//January is 0!
							var yyyy = today.getFullYear();

							// Go back six months
							if(mm <= number){ mm += number; yyyy--; }
							else{ mm -= number }

							// Make sure dd & mm are two digits
							if(dd<10){dd='0'+dd}
							if(mm<10){mm='0'+mm}
							var USFormat = mm+'/'+dd+'/'+yyyy;
							el.value = USFormat;
						}
						getDate(document.getElementById('beginDate'),6);
						getDate(document.getElementById('endDate'),0);
					</script>

					<br>
					<h3>Select sequence data file:</h3>
						<input type="file" name="sequenceData" />
					<br>
					<br>
					<br>
						<input type="submit" name="Submit" value="Submit" /> 
					</form> 
				</div><!-- End content -->
			</div><!-- End main content wrapper -->
			<div class="clearer"></div>
			<div id="footer"><!-- Start Footer -->
				<p>Contact <a href="#" id="rw_email_contact">Mark Ebbert</a><script type="text/javascript">var _rwObsfuscatedHref0 = "mai";var _rwObsfuscatedHref1 = "lto";var _rwObsfuscatedHref2 = ":Ma";var _rwObsfuscatedHref3 = "rk.";var _rwObsfuscatedHref4 = "Ebb";var _rwObsfuscatedHref5 = "ert";var _rwObsfuscatedHref6 = "\@hc";var _rwObsfuscatedHref7 = "i.u";var _rwObsfuscatedHref8 = "tah";var _rwObsfuscatedHref9 = ".ed";var _rwObsfuscatedHref10 = "u";var _rwObsfuscatedHref = _rwObsfuscatedHref0+_rwObsfuscatedHref1+_rwObsfuscatedHref2+_rwObsfuscatedHref3+_rwObsfuscatedHref4+_rwObsfuscatedHref5+_rwObsfuscatedHref6+_rwObsfuscatedHref7+_rwObsfuscatedHref8+_rwObsfuscatedHref9+_rwObsfuscatedHref10; document.getElementById('rw_email_contact').href = _rwObsfuscatedHref;</script></p>
			</div><!-- End Footer -->

		</div><!-- End container -->
		</body>
		</html>
HTML
  }
