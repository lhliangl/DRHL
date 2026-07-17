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
<title>Update Event</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="admin.css" rel="stylesheet" type="text/css">
</head>
<body>

<?php
//Connect To Database
include("config.php");

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query=" SELECT * FROM no_events WHERE id = 1";
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
$id=mysqli_result($result,$i,"id");
$message=mysqli_result($result,$i,"description");
$i++;
}

if (!isset($_POST['submit'])) {

?>

<center>
<h1>No Events Message</h1>
  (This is the messge that appears when there are no active events.) 
  <br> <br>
  
<form action="<?php $_SERVER['PHP_SELF']?>" method="post">
<table width="600" border="0" class="input_table">
<tr valign="top">
  <td >
  <table border="0" cellpadding="5" width="98%" align="center">
    <tr>
      <td>
          <textarea name="ud_description" cols="60" rows="8" class="text_area" ><?php echo $message; ?></textarea>
      </td>
    </tr>
  </table></td>
  </tr>
<tr valign="top"><td align="center"></td>
  </tr>
</table>
<p align="center"><input type="Submit" value="Update" name="submit"></p>
</table>
</form>

<?php 
}
 else {

$ud_description=$_POST['ud_description'];
$ud_description=preg_replace("/\'/","&#039;", ($ud_description));

include("config.php");

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport);
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query = "UPDATE no_events SET description = '$ud_description' WHERE id = '1'";
mysqli_query($con, $query);

if ($query);
{ echo "<center><h1>Message Updated!</h1> </center>"; }
mysqli_close($con);
}

?>

</center>

<?php include("nav.php"); ?>
</body>
</html>
