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
<link href="admin.css" rel="stylesheet" type="text/css">
<title>Add a user</title>
</head>
<body>
<center>

<h1>Add User</h1>

</center>
<center>


<script Language="JavaScript">
			<!--			
function form_val(form1)
{
   var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
   var address = form1.uname.value;
   if(reg.test(address) == false) {
      alert('Please enter a valid email address');
	  form1.uname.focus();
      return false;
   }
	
	if ((form1.pword.value.length < 6) || (form1.pword.value.length > 10))
	{
		alert("Your password must be between 6 and 10 characters");
		form1.pword.focus();
		return (false);
	}

	return (true);
}
//--></script>


<?php if (!isset($_POST['submit'])) { ?>

<form name="setup" action="<?php $_SERVER['PHP_SELF']?>" method="post" onSubmit="return form_val(this)">



  <table width="600" border="0" align="center" cellpadding="8" cellspacing="0" class="row">
    
    <tr>
      <td><div align="right"><strong>email address:</strong></div></td>
      <td><label>
        <input name="uname" type="text" size="30" />
        </label></td>
    </tr>
    <tr>
      <td><div align="right"><strong>Create a password:</strong></div></td>
      <td><input name="pword" type="text" size="30" />
        <span class="small">(6 to 10 alphanumeric characters)</span></td>
    </tr>
  </table>
  <br />
  <input type="submit" value="Add user" name="submit"/>
  </form>
  
<?php
}
else {
  
// Database connection
include("config.php"); 

$uname = $_POST['uname'] ;
$pword = $_POST['pword'] ;


// Database connection
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

// does user exist?

$query = "SELECT * FROM admin WHERE uname='$uname';";
$res = mysqli_query($con, $query);
if (mysqli_num_rows($res) > 0) {
echo "Username already exists!";
} 

else {


$pword = md5($pword.$salt);

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");

$query = "INSERT INTO admin VALUES ('','$uname', '$pword')";


$rt=mysqli_query($con, $query);


if ($rt) {echo "username and password successfuly inserted!<br><br>"; }

else { mysqli_error($con); }

mysqli_close($con);

} 
}
?>
  
</center>
<p>&nbsp;</p>

<?php include("nav.php"); ?>

</body>
</html>
