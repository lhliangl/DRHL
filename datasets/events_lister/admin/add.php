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

require_once('common.php');
checkUser();
include("config.php"); 

?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="admin.css" rel="stylesheet" type="text/css">
<title>Add An Event</title>
</head>
<body>

<h1 align="center">Add A New Event</h1>

<?php include ('db.php'); ?>

<?php if (!isset($_POST['submit'])) { ?>

<?php include ('form.php'); ?>


<table width="600" border="0" align="center" cellpadding="6" cellspacing="0"><tr><td width="" valign="top">

<?php
} 
else{
$ud_event = $_POST['ud_event'] ;
$ud_hour = $_POST['ud_hour'] ;
$ud_minute = $_POST['ud_minute'] ;
$ud_ampm = $_POST['ud_ampm'] ;
$ud_hour_end = $_POST['ud_hour_end'] ;
$ud_minute_end = $_POST['ud_minute_end'] ;
$ud_ampm_end = $_POST['ud_ampm_end'] ;
$ud_month = $_POST['ud_month'] ;
$ud_day = $_POST['ud_day'] ;
$ud_year = $_POST['ud_year'] ;
$ud_month_end = $_POST['ud_month_end'] ;
$ud_day_end = $_POST['ud_day_end'] ;
$ud_year_end = $_POST['ud_year_end'] ;
$ud_month_show = $_POST['ud_month_show'] ;
$ud_day_show = $_POST['ud_day_show'] ;
$ud_year_show = $_POST['ud_year_show'] ;
$ud_location = $_POST['ud_location'] ;
$ud_email = $_POST['ud_email'] ;
$ud_phone = $_POST['ud_phone'] ;
$ud_link = $_POST['ud_link'] ;
$ud_link_name = $_POST['ud_link_name'] ;
$ud_description = $_POST['ud_description'] ;
$ud_html = $_POST['ud_html'] ;

$ud_event=preg_replace("/\'/","&#039;", ($ud_event));
$ud_description=preg_replace("/\'/","&#039;", ($ud_description));

// Ensure the form data is being sent from YOUR server and not someone elses.
    #$_SERVER['HTTP_REFERER']链接到当前页面的前一页面的 URL 地址。
    #$_SERVER['HTTP_HOST'] #当前请求的 Host: 头部的内容。
if (strpos($_SERVER['HTTP_REFERER'], $_SERVER['HTTP_HOST'])>7 || !strpos($_SERVER['HTTP_REFERER'], $_SERVER['HTTP_HOST']))
die("<span class='error'>Error! Bad Referer</span> ");

/*
// Validate the input by ensuring that none of the required fields are left blank		
if ( $ud_event == "") { echo "<span class='error'>Event name is required.</span><br><br>"; }
if ( $ud_hour == "") { echo "<span class='error'>Hour is required.</span><br><br>"; }
if ( $ud_minute == "") { echo "<span class='error'>Minute is required.</span><br><br>"; }
if ( $ud_ampm == "") { echo "<span class='error'>AM or PM is required.</span><br><br>"; }
if ( $ud_month == "") { echo "<span class='error'>Month is required.</span><br><br>"; }
if ( $ud_day == "") { echo "<span class='error'>Day is required.</span><br><br>"; }
if ( $ud_year == "") { echo "<span class='error'>Year is required.</span><br><br>"; }
if ( $ud_location == "") { echo "<span class='error'>Location is required.</span><br><br>"; }
if ( $ud_description == "") { echo "<span class='error'>Description is required.</span>"; }
  
$validation_error = ($ud_event == "")||($ud_hour == "")||($ud_minute == "")||($ud_minute == "")||($ud_ampm == "")||($ud_month == "")||($ud_day == "")||($ud_year == "")||($ud_location == "")||($ud_description == "");

if ($validation_error)
{  echo "<p>&nbsp;</p><b> Please go back and correct the error(s) above.<b> <br><br>
<center><FORM><INPUT TYPE=\"button\" VALUE=\" Back \" onClick=\"history.go(-1)\"></FORM> </center>
";
exit();
}
*/

// Database connection

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query = "INSERT INTO events VALUES (
'',
'$ud_event',
'$ud_hour',
'$ud_minute',
'$ud_ampm',
'$ud_hour_end',
'$ud_minute_end',
'$ud_ampm_end',
'$ud_month',
'$ud_day',
'$ud_year',
'$ud_month_end',
'$ud_day_end',
'$ud_year_end',
'$ud_month_show',
'$ud_day_show',
'$ud_year_show',
'$ud_location',
'$ud_email',
'$ud_phone',
'$ud_link',
'$ud_link_name',
'$ud_description',
'$ud_html')";


$rt=mysqli_query($con, $query);

if ($rt) {echo "<center><h1>Event Added!</h1> </center><br><br>
"; }

else { mysqli_error($con); }

mysqli_close($con);
}
?>

</td></tr></table>
<?php include("nav.php"); ?>

</body>
</html>