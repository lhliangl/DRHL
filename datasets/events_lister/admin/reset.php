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
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="admin.css" rel="stylesheet" type="text/css">
<title>Reset your password</title>

<?php 
if (!isset($_POST['submit']) ){
$code=$_GET['code'];    //密码
$id=$_GET['id'];

// Database connection
include("config.php"); 

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query=" SELECT * FROM admin WHERE id='$id'";
$result=mysqli_query($con, $query);
$num=mysqli_num_rows($result);
mysqli_close($con);
$i=0;
while ($i < $num) {
$pw=mysql_result($result,$i,'pword');
$uid=mysql_result($result,$i,'id');
$user=mysql_result($result,$i,'uname');
$i++;
}

if (($code != $pw) || ($code ==null)) { 

echo "<center>You are not authorized to reset this user's password.</center>";
exit();
}

else {
                    
?>

<script Language="JavaScript">
			<!--			
function form_val(form1)
{
 
	
	if ((form1.pword.value.length < 6) || (form1.pword.value.length > 10))
	{
		alert("Your password must be between 6 and 10 characters");
		form1.pword.focus();
		return (false);
	}

	return (true);
}
//--></script>

</head>
<body>

<form name="setup" action="<?php echo $_SERVER['PHP_SELF']; ?>?id=<?php echo $uid; ?>code=<?php echo $code; ?>" method="post" onSubmit="return form_val(this)">
<input type="hidden" name="uid" value="<?php echo $uid; ?>" />

 <table width="600" border="0" align="center" cellpadding="8" cellspacing="0" class="row">
    
    <tr>
      <td><center>
      <b>choose new password for the user:</b> <?php echo $user; ?>
      <br><br>
       <input name="pword" size="20" type="text"/> 
        (from 6 to 10 characters)
        </center>
        <br>
        
    </td></tr>
    
 </table> 
  <br />
 <center><input type="submit" value="Submit" name="submit" /></center>
 <br>
 </form>

<?php
}
}
else {
$id=$_GET['id'];

include("config.php"); 
$pword = $_POST['pword'];

$pword = md5($pword.$salt);

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query2 = "UPDATE admin SET pword = '$pword' WHERE id = '$id'";
mysqli_query($con, $query2);
mysqli_close($con);

if (query2) { echo "<center>Password successfully reset! <br><br> <a href=login.php>Login Now!</a></center>"; }

}

?>

</body>
</html>
