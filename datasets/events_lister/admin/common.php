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

session_start();

function loginUser($username,$password){
	$errorText = '';
	$validUser = false;
	
// Check user existance	
	
include 'config.php';
$con = mysqli_connect($dbhost,$dbuser,$dbpass,'',$dbport) OR DIE ('Unable to connect to database! Please try again later.');

mysqli_select_db($con, $dbname) or die( "Unable to select database");
$username = mysqli_real_escape_string($con, $username);   //转义特殊字符，username中有特殊字符就会被转义成新的username然后再进行增删改查操作
$password = mysqli_real_escape_string($con, $password);
$query=" SELECT * FROM admin WHERE uname = '$username'";
$result=mysqli_query($con, $query);
$num=mysqli_num_rows($result);
mysqli_close($con);
$i=0;
	//读取编号为number的数据
	function mysqli_result($result, $number, $field=0) {
		mysqli_data_seek($result, $number);   //查找编号为$number的数据放在$result中
		$row = mysqli_fetch_array($result);   // 读取数据
		return $row[$field];
	}

while ($i < $num) {
$pword=mysqli_result($result,$i,"pword");
$i++;
}


//if ($pword == md5($password)){
if ($pword == md5($password.$salt)){

$validUser= true;
$_SESSION['userName'] = $username;
} 

if ($validUser != true) $errorText = "<center><font class=\"error\">Invalid username or password!</font> </center>";
    
if ($validUser == true) $_SESSION['validUser'] = true;
else $_SESSION['validUser'] = false;
return $errorText;	
} 
	
function logoutUser(){
	unset($_SESSION['validUser']);
	unset($_SESSION['userName']);
}

function checkUser(){
	if ((!isset($_SESSION['validUser'])) || ($_SESSION['validUser'] != true)){
		header('Location: login.php');
	}
}

?>
