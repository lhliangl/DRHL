<?php
/*
    This file is a part of Basic PHP Event Lister.  Copyright (c) 2008 Mark MacCollin, Mevin Productions, www.mevin.com

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/ 

include('common.php');
checkUser();

if ((!isset($_SESSION['validUser'])) || ($_SESSION['validUser'] != true)) {
    exit;
}

?>


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="admin.css" rel="stylesheet" type="text/css">
<title>Database setup</title>
</head>
<body>
<center>


<script Language="JavaScript">
			<!--			
function form_val(form1)
{
   var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
   var address = form1.uname.value;
   if(reg.test(address) == false) {   //test() 方法用于检测一个字符串是否匹配某个模式.
      alert('Please enter a valid email address');
	  form1.uname.focus();
      return false;
   }
	
	if ((form1.pword.value.length < 6) || (form1.pword.value.length > 10))
	{
		alert("Your password must be between 6 and 10 characters");
		form1.pword.focus();
		return (false);
	}

	return (true);
}
//--></script>


<?php if (!isset($_POST['submit'])) { ?>

<form name="setup" action="<?php $_SERVER['PHP_SELF']?>" method="post" onSubmit="return form_val(this)">

  <table width="600" border="0" align="center" cellpadding="8" cellspacing="0" class="row">
    <tr>
      <td><div align="right"><strong>Your email address:</strong></div></td>
      <td><label>
        <input name="uname" type="text" size="20" />
        </label></td>
    </tr>
    <tr>
      <td><div align="right"><strong>Create a password:</strong></div></td>
      <td><input name="pword" type="text" size="20" />
        (6 to 10 alphanumeric characters)</td>
    </tr>
    <tr>
      <td colspan="2"> &nbsp;*Note: Your password (if you want to make it difficult for hackers) should NOT be a word from the dictionary, but SHOULD contain both upper and lowercase letters and  at least one number. But you're a big boy/girl so choose whatever you want. Just don't say I didn't &quot;tell ya so.&quot;</td>
      </tr>
    <tr>
      <td><div align="right"><strong>Insert example event:</strong></div></td>
      <td> <input type="radio" name="test_event" id="test_event" value="yes" checked="checked" />
      YES &nbsp;&nbsp;&nbsp;&nbsp; <input type="radio" name="test_event" id="test_event" value="no" />NO</td>
    </tr>
  </table>
  <br />
  <input type="submit" value="Setup the database" name="submit"/>
  </form>
  
<?php
}
else {
  
// Database connection
include("config.php"); 

$uname = $_POST['uname'] ;
$pword = $_POST['pword'] ;
$test_event = $_POST['test_event'] ;
$pword = md5($pword.$salt);
$current_year = date("Y");

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) or die ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die ( 'Unable to select database');

//create events table
$query1 = "CREATE TABLE IF NOT EXISTS events (
id int(6) NOT NULL auto_increment, 
event text NOT NULL, 
hour varchar(2) NOT NULL, 
minute varchar(2) NOT NULL, 
ampm varchar(2) NOT NULL, 
hour_end varchar(2) NOT NULL, 
minute_end varchar(2) NOT NULL, 
ampm_end varchar(2) NOT NULL, 
month varchar(2) NOT NULL, 
day varchar(2) NOT NULL, 
year varchar(4) NOT NULL, 
month_end varchar(2) NOT NULL, 
day_end varchar(2) NOT NULL, 
year_end varchar(4) NOT NULL, 
month_show  varchar(2) NOT NULL,
day_show varchar(2) NOT NULL,  
year_show varchar(4) NOT NULL, 
location varchar(255) NOT NULL, 
email varchar(100) NOT NULL, 
phone varchar(20) NOT NULL, 
link varchar(255) NOT NULL, 
link_name varchar(255) NOT NULL, 
description text NOT NULL, 
html int(1) NOT NULL, 
PRIMARY KEY  (id) )";

mysqli_query($con, $query1);

// no events message setup
$query2 = "CREATE TABLE IF NOT EXISTS no_events (
id int(1) NOT NULL, 
description text NOT NULL, 
PRIMARY KEY  (id) )";
mysqli_query($con, $query2);

// insert the no events message
$query3 = "INSERT INTO no_events VALUES (
'1',
'There are no events scheduled at this time.  Please check back later. Thank you')";
mysqli_query($con, $query3);

// username and password table setup
$query4 = "CREATE TABLE IF NOT EXISTS admin (
id int(1) NOT NULL auto_increment, 
uname varchar(255) NOT NULL, 
pword varchar(255) NOT NULL, 
PRIMARY KEY  (id) )";
mysqli_query($con, $query4);

//insert user/pass data
$query5 = "INSERT INTO admin VALUES ('1','$uname', '$pword')";
mysqli_query($con, $query5);

if ($query5) { echo "username and password inserted successfuly!<br><br>"; }

// if insert test events is checked then...
if ($test_event =="yes") {
$query6 = "INSERT INTO events VALUES (
'',
'Test Event',
'12',
'00',
'PM',
'02',
'00',
'PM',
'12',
'31',
'$current_year',
'12',
'31',
'$current_year',
'12',
'31',
'$current_year',
'Test location',
'you@yourwebsite.com',
'415-555-1212',
'http://www.yourwebsite.com',
'Your web site',
'This is the test event description.  You can either delete this event, by clicking the delete link in the all events section, or you can edit the event, and set the date in the past.  All events that are scheduled in the past, will automatically disappear from the publicly viewable events page.',
'0'
)";


mysqli_query($con, $query6);
}

//Check to see if the events table is actually setup
$query7=" SELECT * FROM events";
$result=mysqli_query($con, $query7);
$num=mysqli_num_rows($result);
mysqli_close($con);
$i=0;

    function mysqli_result($result, $number, $field=0) {
        mysqli_data_seek($result, $number);
        $row = mysqli_fetch_array($result);
        return $row[$field];
    }

while ($i < $num) {
$id=mysqli_result($result,$i,"id");
$i++;
}

if ($id != "") { echo "<b>Database setup successful!</b> <p> <a href=login.php>Login Now!</a> ";}
else { echo "Error";}
}

?>
  
</center>
<p>&nbsp;</p>
</body>
</html>
