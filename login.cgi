#!/usr/bin/perl
  
  # login.cgi
  use CGI;
  use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
  use CGI::Session ( '-ip_match' );
  use lib 'cgi/';
  use html_header;
  
  $q = new CGI;

  $usr = $q->param('usr');
  $pwd = $q->param('pwd');

  my $user="user";
  my $pass="pass";
  
  if($usr ne '')
  {
      # process the form
      if($usr eq $user and $pwd eq $pass)
      {
          $session = new CGI::Session();
          print $session->header(-location=>'index.cgi');
      }
      else
      {
          print $q->header(-type=>"text/html",-location=>"login.cgi");
      }
  }
  elsif($q->param('action') eq 'logout')
  {
      $session = CGI::Session->load() or die CGI::Session->errstr;
      $session->delete();
      print $session->header(-location=>'login.cgi');
  }
  else
  {
	  print $q->header();
	  html_header->head();
	  html_header->html_title();
	  html_header->endHead();
	  
print <<HTML;
		<body>
		<div id="container"><!-- Start container -->
			<div id="pageHeader"><!-- Start page header -->
				<img src="rw_common/images/ARUP-logo-small.png" width="91" height="49" alt="Site logo"/>
				<h1>ARUP</h1>
				<h2>HIV Contamination Detection</h2>
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
					<h2>Please login:</h2>
				  <form method="post">
					  <table>
						  <tr>
							<td>Username:</td><td>
							<input type="text" name="usr"></td>
						  </tr>
						  <tr>
							<td>Password:</td><td>
							<input type="password" name="pwd"></td>
						  </tr>
						  <tr>
							<td><input type="submit"></td>
						  </tr>
					  </table>
				  </form>
				</div><!-- End content -->
			</div><!-- End main content wrapper -->
			<div class="clearer"></div>
			<div id="footer"><!-- Start Footer -->
				<p>Contact <a href="#" id="rw_email_contact">Mark Ebbert</a><script type="text/javascript">var _rwObsfuscatedHref0 = "mai";var _rwObsfuscatedHref1 = "lto";var _rwObsfuscatedHref2 = ":Ma";var _rwObsfuscatedHref3 = "rk.";var _rwObsfuscatedHref4 = "Ebb";var _rwObsfuscatedHref5 = "ert";var _rwObsfuscatedHref6 = "@hc";var _rwObsfuscatedHref7 = "i.u";var _rwObsfuscatedHref8 = "tah";var _rwObsfuscatedHref9 = ".ed";var _rwObsfuscatedHref10 = "u";var _rwObsfuscatedHref = _rwObsfuscatedHref0+_rwObsfuscatedHref1+_rwObsfuscatedHref2+_rwObsfuscatedHref3+_rwObsfuscatedHref4+_rwObsfuscatedHref5+_rwObsfuscatedHref6+_rwObsfuscatedHref7+_rwObsfuscatedHref8+_rwObsfuscatedHref9+_rwObsfuscatedHref10; document.getElementById('rw_email_contact').href = _rwObsfuscatedHref;</script></p>
			</div><!-- End Footer -->
		</div><!-- End container -->
		</body>
		</html>
HTML
  }
