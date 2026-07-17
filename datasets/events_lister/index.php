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
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="events.css" rel="stylesheet" type="text/css">
<title>Event Calendar</title>
</head>
<body>
<center>

<h1>Event Calendar</h1>

</center>

<div class="main_area">

 <?php



//Connect To Database
include("admin/config.php");
$con = mysqli_connect($dbhost,$dbuser,$dbpass) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

//只搜索active事件
$query="SELECT * FROM events WHERE 
(year >= $current_year AND month > $current_month) 
OR (year >= $current_year AND month = $current_month AND day >= $current_day) 
OR (year_end >= $current_year AND month_end = $current_month AND day_end >= $current_day) 
OR (year > $current_year) 

OR (year_show >= $current_year AND month_show > $current_month)
OR (year_show >= $current_year AND month_show = $current_month AND day_show >= $current_day) 
OR (year_show > $current_year) 
ORDER BY year, month, day LIMIT 0, $maxnum";


$result=mysqli_query($con, $query);
 if (!$result) {
     printf("Error: %s\n", mysqli_error($con));
     exit();
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

//Get all the data and assign variables
$id=mysqli_result($result,$i,"id");
$event=mysqli_result($result,$i,"event");
$hour=mysqli_result($result,$i,"hour");
$minute=mysqli_result($result,$i,"minute");
$ampm=mysqli_result($result,$i,"ampm");
$hour_end=mysqli_result($result,$i,"hour_end");
$minute_end=mysqli_result($result,$i,"minute_end");
$ampm_end=mysqli_result($result,$i,"ampm_end");
$month=mysqli_result($result,$i,"month");
$day=mysqli_result($result,$i,"day");
$year=mysqli_result($result,$i,"year");
$month_end=mysqli_result($result,$i,"month_end");
$day_end=mysqli_result($result,$i,"day_end");
$year_end=mysqli_result($result,$i,"year_end");
$month_show=mysqli_result($result,$i,"month_show");
$day_show=mysqli_result($result,$i,"day_show");
$year_show=mysqli_result($result,$i,"year_show");
$location=mysqli_result($result,$i,"location");
$email=mysqli_result($result,$i,"email");
$phone=mysqli_result($result,$i,"phone");
$link=mysqli_result($result,$i,"link");
$link_name=mysqli_result($result,$i,"link_name");
$description=mysqli_result($result,$i,"description");
$html=mysqli_result($result,$i,"html");
// removes slashes
$description=stripslashes($description);

//replaces carriage returns with html line breaks
if ($html =="0") {
        $description=preg_replace("/\n/","<br>", ($description));
    }

// removes the first zero from the hour.  We need the zero at first, to keep the numbering in order.  
//Of course the number ten needs the zero left in.
if ($hour !="10") {
$hour=preg_replace("/0/","", ($hour));
}

if ($hour_end !="10") {
$hour_end=preg_replace("/0/","", ($hour_end));
}

if (($hour_end =='') && ($minute_end =='') && ($ampm_end =='')) { $end_time ='';}
else { $end_time= " - $hour_end:$minute_end $ampm_end"; }

if (($month_end =='') && ($day_end =='') && ($year_end =='')) { $end_date ='';}
else { $end_date= "- $month_end/$day_end/$year_end"; }

// Here is where we actually print out the events.  
echo "
<a name=$id></a><span class=\"event_name\">$event</span> <br>
Date: $month/$day/$year $end_date  <br>
Time: $hour:$minute $ampm $end_time<br>
Location: $location <br>";
// email, phone and link is optional, so we have to use a conditional statement.  We don't want extra line breaks if these fields aren't used.
if ($email) { echo "Contact email: <a href='mailto:$email'>$email</a> <br>"; }     //mailto链接是一种html链接，能够设置你电脑中邮件的默认发送信息
if ($phone) { echo "Contact phone: $phone <br>"; } 
echo"<br>$description <br>";
if ($link)  { echo "<br><a href='$link' target='_blank'>$link_name</a>"; }
echo "<div class=\"separator\"></div>";
// looks for the next event id and if it exists, prints it out.
$i++;
}   //结束循环


// If there are no scheduled events, print the no events message
if (!mysqli_num_rows($result)) {
    $con = mysqli_connect($dbhost,$dbuser,$dbpass) OR DIE ('Unable to connect to database! Please try again later.');
    mysqli_select_db($con, $dbname) or die( "Unable to select database");
    $query2="SELECT * FROM no_events WHERE id=1";
    $result2=mysqli_query($con, $query2);
    $num2=mysqli_num_rows($result2);
    mysqli_close($con);
    $k=0;

    while ($k < $num2) {
    $description2=mysqli_result($result2,$k,"description");
    $description2=stripslashes($description2);
    $description2=preg_replace("/\n/","<br>", ($description2));
    echo "$description2";
    $k++;
    }
}


?>

<br><br>
Powered by: <a href="http://www.mevin.com/">mevin productions</a>
<br><br>

</div>

</body>
</html>
