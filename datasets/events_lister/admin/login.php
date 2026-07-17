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

$error = '0' ;

if (isset($_POST['submitBtn'])){
	// Get user input
	$username = isset($_POST['username']) ? $_POST['username'] : '';
	$password = isset($_POST['password']) ? $_POST['password'] : '';
	
	// filter out potential malicious code
	$bad_chars = array(" ", "(", ")", "<", ">", "'", "&gt;", "&lt;"); 
	
	$username = str_replace($bad_chars, "", $username);
	$password = str_replace($bad_chars, "", $password);
        
	// Try to login the user
	$error = loginUser($username,$password);
	
}


?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Login System</title>
<link href="admin.css" rel="stylesheet" type="text/css" />
</head>
<body>
<center>
  <h3>login</h3>
</center>
<div id="main">


  <?php 


$filename = 'setup.php';

if (file_exists($filename)) {
    echo "<center><div style=\"width:500px;\"><font color=red size=+2>WARNING!</font><p>  
	<font color=red>You need to delete the file \"setup.php\" from the admin folder.  If you do not delete the setup file, 
	the events system could be compromised and bullies will steal your lunch money!
	</font></div></center>";
} 
  
  
  
  if ($error != '') {?>
 
  <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post" name="loginform">
    <table width="0" align="center" class="row" cellpadding="5">
      <tr>
        <td><div align="right">Username:</div></td>
        <td><input name="username" type="text" class="text" size="30"  /></td>
      </tr>
      <tr>
        <td><div align="right">Password:</div></td>
        <td><input name="password" type="password" class="text" size="30" /></td>
      </tr>
    </table>
    <br /><center><input class="text" type="submit" name="submitBtn" value="Login" /></center>
  </form>
  <center><br> <a href=recover.php>Lost your password?</a></center>
  <?php 
}   
    if (isset($_POST['submitBtn'])){

?>
  <table width="700" align="center">
    <tr>
      <td>
        <?php
	if ($error == '') {

 echo "<center> <h2>Login successful!</h2> Please choose from one of the links below:</center><br/>"; 
include("nav.php");
}


else echo $error;

?>


        <br/>
        <br/>
        <br/></td>
    </tr>
  </table>
</div>
<?php 
}
?>

</div>
</body>
