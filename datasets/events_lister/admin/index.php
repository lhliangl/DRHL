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
<title>Events Home</title>
</head>

<body>


  <h1 align="center">Events Administration</h1>
 
  
  
  
  
  <?php
// Database connection
include("config.php"); 
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

$query=" SELECT * FROM events";
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

$i++;
}

if ($id == "") { echo "<a href=setup.php.baksetup.php.bak>Click here to setup the database.</a>";}
else { echo "";}


?>
  


<?php include ('nav.php'); ?>
</body>
</html>
