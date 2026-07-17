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
error_reporting(0);

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="admin.css" rel="stylesheet" type="text/css">
<title>recover</title>
</head>

<body>
<br />

<?php if (!isset($_POST['submit'])) { ?>

<script Language="JavaScript">
			<!--			
function form_val(form1)
{
   var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
   var address = form1.email.value;
   if(reg.test(address) == false) {   //test() 方法用于检测一个字符串是否匹配某个模式
      alert('Please enter a valid email address');
	  form1.email.focus();
      return false;
   }

	return (true);
}
//--></script>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post" name="recover" onSubmit="return form_val(this)">
    <table width="400" align="center"  cellpadding="5" class="row">
      <tr>
        <td colspan="2"> Enter your email address in the field below and click send.   You will then be sent a link that will allow you to reset your password. </td>
      </tr>
      <tr >
        <td><div align="right">email:</div></td>
        <td><input name="email" type="text" class="text" size="40"  /> </td>
      </tr>
      
       <tr>
        <td colspan="2" height="10">&nbsp;</td>
      </tr>
      
    </table>
    <br /><center><input class="text" type="submit" name="submit" value=" send " /></center>
  </form>

<?php 
}
else {

// Database connection
include("config.php"); 
$email = $_REQUEST['email'] ;

if ($email =="") 
{ echo "<center>Email field is blank?</center>";

exit();
 }

$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');
mysqli_select_db($con, $dbname) or die( "Unable to select database");
$query=" SELECT * FROM admin WHERE uname = '$email'";
$result=mysqli_query($con, $query);
$num=mysqli_num_rows($result);
mysqli_close($con);
$i=0;
while ($i < $num) {
$pword=mysql_result($result,$i,"pword");
$uname=mysql_result($result,$i,"uname");
$id=mysql_result($result,$i,"id");
$i++;
}

if ($uname == $email) {

$msgbody ="
To reset your password, go to: $website/admin/reset.php?id=$id&code=$pword";

$subject = "Message from Basic PHP Events List";
$headers .= "To: $email\r\n";
$headers .= "From: $email\r\n";

//and now mail it */
mail($to, $subject, $msgbody, $headers );    //mail函数允许从脚本中直接发送电子邮件。

/* Thank the visitor */

echo "<center>Email sent! Click the link in the email to start the password reset process.   Have a day!</center>";
}

else { echo "<center>The email address you entered is not in the database.</center>"; }
}
?>
<p>&nbsp;</p>

<?php include("nav.php"); ?>

</body>
</html>




