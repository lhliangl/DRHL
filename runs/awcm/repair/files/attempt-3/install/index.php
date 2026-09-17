<?php
if(phpversion() < 0) {
print 'AWCM needs php5 to work correctly<br />البرنامج يحتاج الإصدار الخامس من بي اتش بي كي يعمل بشكل صحيح';
exit;
}
include ("header.php");
if(!isset($member) || $member == 'no') {
    print '<meta http-equiv="refresh" content="0; URL=../index.php">';
    exit;
}
?>

<br /><br /><br />
<form action="step1.php" method="post">
<center>
أختر لغة \ choose language
<br />
<select name="lang">
<option value="ar.php">عربي \ Arabic</option>
<option value="en.php">English \ إنجلينزي</option>
</select>
<br /><br />
<input type="submit" value="next \ التالي" />
</center>
</form>
<br /><br /><br />
<?php
include ("footer.php");
?>
