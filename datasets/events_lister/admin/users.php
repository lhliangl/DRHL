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

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>User Management</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="admin.css" rel="stylesheet" type="text/css">
</head>
<body>

<center><h1>User Management</h1></center>
<table width='600' border='0' cellspacing='1' cellpadding='5' align='center'>
  <tr class='row_head'>
    <th align="left" width="375"><b>User</b></th>
     
     <th align="left" width="225"><b>Action</b></th>
  </tr>
<?php

//Connect To Database
include("config.php");
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

//SQL statment: get all events (records) happening this year or later
$query="SELECT * FROM admin";

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
    $uname=mysqli_result($result,$i,"uname");
    $pword=mysqli_result($result,$i,"pword");


    echo "<tr class='row'> <td>$uname</td>  
            <td> 
                <a href='recover.php?id=$id'>reset password</a>&nbsp;  |
                <a href='user_delete.php?id=$id'>delete user</a>
            </td> 
          </tr>";

    $i++;
}

echo "</table>";
?>
<br><br>
<center><a href="user_add.php">Add a new user</a></center>

<?php include("nav.php"); ?>
</body>
</html>