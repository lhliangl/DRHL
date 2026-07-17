<?php
error_reporting(0);
$page_name = basename($_SERVER['PHP_SELF']);

if ($page_name == 'add.php') { $submit_label = 'Add Event'; }
if ($page_name == 'update.php') { $submit_label = 'Update Event'; }
if ($page_name == 'copy.php') { $submit_label = 'Copy Event'; }

if ($page_name == 'add.php') {

$id='';
$event='';
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
$location='';
$email='';
$phone='';
$link='';
$link_name='';
$description='';
$html='';
}

else {

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

$query=" SELECT * FROM events WHERE id='$id'";
$result=mysqli_query($con, $query);
$num=mysqli_num_rows($result);
mysqli_close($con);

$i=0;

    function mysqli_result($result, $number, $field=0) {
        mysqli_data_seek($result, $number);
        $row = mysqli_fetch_array($result);
        return $row[$field];
    }
    
while ($i < $num) {


$event=mysqli_result($result,$i,"event");
$hour=mysqli_result($result,$i,"hour");
$minute=mysqli_result($result,$i,"minute");
$ampm=mysqli_result($result,$i,"ampm");
$month=mysqli_result($result,$i,"month");
$day=mysqli_result($result,$i,"day");
$year=mysqli_result($result,$i,"year");

$hour_end=mysqli_result($result,$i,"hour_end");
$minute_end=mysqli_result($result,$i,"minute_end");
$ampm_end=mysqli_result($result,$i,"ampm_end");
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

$i++;
}
}

?>