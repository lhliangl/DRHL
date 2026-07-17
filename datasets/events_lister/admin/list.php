<?php
error_reporting(0);
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

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>All Events</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="admin.css" rel="stylesheet" type="text/css">
</head>
<body>

<center><h1>Active Events</h1></center>
<table width="600" border="0" cellspacing="1" cellpadding="5" align="center">
  <tr class='row_head'>
    <th align="left" width="90"><b>Date</b></th>
     <th align="left"><b>Event</b></th>
     <th align="left" width="165"><b>Action</b></th>
  </tr>
<?php
// define variables

$status=$_GET['status'];
if($status ==null) {$status = 'all';}

//Connect To Database
include("config.php");
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

//SQL statment: get all events (records) happening this year or later
//$query_active="SELECT * FROM events WHERE (year >= $current_year AND month > $current_month) OR (year >= $current_year AND month = $current_month AND day > $current_day) OR (year > $current_year) ORDER BY year, month, day";

$query_active="SELECT * FROM events WHERE 
(year >= $current_year AND month > $current_month) 
OR (year >= $current_year AND month = $current_month AND day >= $current_day) 
OR (year_end >= $current_year AND month_end = $current_month AND day_end >= $current_day) 
OR (year > $current_year) 

OR (year_show >= $current_year AND month_show > $current_month)
OR (year_show >= $current_year AND month_show = $current_month AND day_show >= $current_day) 
OR (year_show > $current_year) 
ORDER BY year, month, day";

$query_all="SELECT * FROM events ORDER BY year, month, day";

if ($status=='active') {
$result=mysqli_query($con, $query_active);
}
else if ($status=='all') { 
$result=mysqli_query($con, $query_all);
}

else { 
$result=mysqli_query($con, $query_all);
}

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
$event=mysqli_result($result,$i,"event");
$month=mysqli_result($result,$i,"month");
$day=mysqli_result($result,$i,"day");
$year=mysqli_result($result,$i,"year");

echo "<tr class='row'> <td>$month/$day/$year</td> <td>$event</td> <td> <a href='update.php?id=$id'>update</a>&nbsp;&nbsp;|&nbsp;<a href='copy.php?id=$id'>copy</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href='delete.php?id=$id'>delete</a></td> </tr>"; 

$i++;
}

echo "</table>";

// if there are no scheduled events, print the no events message
if (!mysqli_num_rows($result)) {

echo "<center><br><br>There are no active events in the database.<br><br>  <a href=add.php>Add an event now.</a> <br><br></center>";
}

include("nav.php"); ?>
</body>
</html>