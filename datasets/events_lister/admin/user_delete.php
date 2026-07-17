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

	require('common.php');
	$un = $_SESSION['userName'];
	checkUser();
	
	
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>Delete</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<link href="admin.css" rel="stylesheet" type="text/css">
</head>
<body>
<center>

<?php
//Connect To Database
include("config.php");
$id=$_GET['id'];
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query=" SELECT * FROM admin WHERE id='$id'";
$result=mysqli_query($con, $query);
$num=mysqli_num_rows($result);
if ($num > 0) {
    $row = mysqli_fetch_assoc($result);
    $id = $row['id'];
    $uname = $row['uname'];
}
mysqli_close($con);
?>

<?php


if ($uname == $un) { echo '<span class=error><b>You cannot delete yourself!</b></span>'; 

exit();

 }
 
 else if ($id == '1') { echo '<span class=error><b>You cannot delete the main user!</b></span>';

exit();

 }
 
 else if ($uname == 'demo') { echo '<span class=error><b>You cannot delete the demo user!</b></span>';

exit();

 }



 if (!isset($_POST['submit'])) { ?>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>?id=<?php echo $id; ?>" method="post">
<center>
<h2>Are you sure you want to delete the user: </h2><h1><?php echo $uname; ?>? <br>
<img src="alert.gif" alt="ALERT!">
<h1><font color='red'> This action CANNOT be undone!</font></h1>
</center>
<br>
<input type="hidden" name="ud_id" value="<?php echo $id; ?>">
<center><input type="submit" name="submit" value="YES DELETE"> &nbsp; <input type=button value=" NO CANCEL " onClick="history.go(-1)"></center>
</form>
<?php } 

else {

$ud_id=$_POST['ud_id'];

include("config.php");

//Database connection
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport);
mysqli_select_db($con, $dbname) or die( "Unable to select database");

// here we limit the delection process to just one, so if we made a mistake, it only deletes one event and not the entire database.
$query = "DELETE FROM admin WHERE id='$ud_id' LIMIT 1";
mysqli_query($con, $query);

if ($query)
{ echo "<center><h1>User Deleted!</h1> <br><br> </center>"; }

else { echo "Error!"; }

mysqli_close($con);

}

include("nav.php");


?>
</center>
<br><br><br><br>
</body>
</html>