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
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="admin.css" rel="stylesheet" type="text/css">
<title>Copy Event</title>
<body>
<center>
<?php


$id=$_GET['id'];
include("config.php");
include ('db.php');
//Connect To Database
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

$query=" SELECT * FROM events WHERE id='$id'";
$result=mysqli_query($con, $query);
$num=mysqli_num_rows($result);
mysqli_close($con);

$i=0;

//function mysqli_result($result, $number, $field=0) {
//    mysqli_data_seek($result, $number);
//    $row = mysqli_fetch_array($result);
//    return $row[$field];
//}

while ($i < $num) {

/* 
Assign variables to all our db values.  leaving all the time and date varables blank.  Since
the script is copying an existing event, the user should assign new values.
*/
$id=mysqli_result($result,$i,"id");
$event=mysqli_result($result,$i,"event");

$hour='';
$minute='';
$ampm='';
$month='';
$day='';
$year='';
$hour_end='';
$minute_end='';
$ampm_end='';
$month_end='';
$day_end='';
$year_end='';
$month_show='';
$day_show='';
$year_show='';

$location=mysqli_result($result,$i,"location");
$email=mysqli_result($result,$i,"email");
$phone=mysqli_result($result,$i,"phone");
$link=mysqli_result($result,$i,"link");
$link_name=mysqli_result($result,$i,"link_name");
$description=mysqli_result($result,$i,"description");
$html=mysqli_result($result,$i,"html");

$i++;
}

if (!isset($_POST['submit'])) {

?>


<h1>Copy Event: <?php echo $event; ?>  </h1>

<?php include('form.php'); ?>

</table>
</center>

<?php 
}
 else {
 
//Get form values
$ud_event=$_POST['ud_event'];
$ud_hour=$_POST['ud_hour'];
$ud_minute=$_POST['ud_minute'];
$ud_ampm=$_POST['ud_ampm'];
$ud_month=$_POST['ud_month'];
$ud_day=$_POST['ud_day'];
$ud_year=$_POST['ud_year'];
$ud_hour_end=$_POST['ud_hour_end'];
$ud_minute_end=$_POST['ud_minute_end'];
$ud_ampm_end=$_POST['ud_ampm_end'];
$ud_month_end=$_POST['ud_month_end'];
$ud_day_end=$_POST['ud_day_end'];
$ud_year_end=$_POST['ud_year_end'];
$ud_month_show=$_POST['ud_month_show'];
$ud_day_show=$_POST['ud_day_show'];
$ud_year_show=$_POST['ud_year_show'];
$ud_location=$_POST['ud_location'];
$ud_email=$_POST['ud_email'];
$ud_phone=$_POST['ud_phone'];
$ud_link=$_POST['ud_link'];
$ud_link_name=$_POST['ud_link_name'];
$ud_description=$_POST['ud_description'];
$ud_html=$_POST['ud_html'];

//escape single quotes and replace them with html equivalent
$ud_event=preg_replace("/\'/","&#039;", ($ud_event));
$ud_description=preg_replace("/\'/","&#039;", ($ud_description));

include("config.php");
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport);
mysqli_select_db($con, $dbname) or die( "Unable to select database");

//insert values into db, under new id
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

//success!... hopefully :)
$rt=mysqli_query($con, $query);
if ($rt) {echo "<center><h1>Event Copied!</h1> </center>"; }
else { mysql_error(); } 
mysqli_close($con);

}

include("nav.php"); ?>

</body>
</html>