<?php
$v_header = "done";
$v_footer = "done";
$v_blocks = "done";
include ("header.php");

if($member == 'no') {
 print '<meta http-equiv="refresh" content="0; URL=index.php">';
exit;
}

if(isset($_GET['do'])) {
$gavatar = $_POST['avatar'];

$upqu = mysql_query("UPDATE awcm_members SET avatar = '$gavatar' WHERE id = '$member'");
if($upqu) {
	print 'تم بنجاح';
}

}
?>

<table width="100%" cellspacing="0" cellpadding="0" class="table_2" height="100%">
<tr><td align="center" class="gradient_2"><?php print $lang_avatar; ?></td></tr>
<tr><td>
<center>
<iframe width="130" height="130" frameborder="0" src="includes/avatar.php?id=<?php echo $member; ?>&h=130&w=130"></iframe>
<br />
<form action="?do" method="POST">
<?php echo $lang_url; ?> : <input type="text" value="<?php f_find_member($member,avatar); ?>" class="textfield" name="avatar" />

<input type="submit" value="<?php echo $lang_update; ?>" class="a_button" />

</form>
</center>
</td></tr>
<tr><td height="100%"></td></tr>
</table>

<?php
include ("footer.php");
?>
