<?php echo "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?".">"; 

/*

This file is part of PHPOLL.

    PHPOLL is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    PHPOLL is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PHPOLL; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

*/


?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>

<script type="text/javascript" language="JavaScript">


</script>

<title>PHPOLL</title>
<link rel="stylesheet" href="../css/phpoll_layout.css" title="phpoll layout" />
</head>
<body>

<?php
include "../config/config.php";

// assegno le variabili di connessione
$phpoll_db = mysql_connect ($phpoll_host, $phpoll_user, $phpoll_password)
	or die ("Errore nella connessione a MySQL");
	
// selezione del database
mysql_select_db($phpoll_database, $phpoll_db)
	or die ("Errore nella connessione al database ".$phpoll_database);

// Verifica autenticazione amministratore
$query_login = "SELECT login, password FROM phpoll_".$prepoll."_configurazione;";
$estrai_login = mysql_query($query_login, $phpoll_db)
	or die ("Errore nella connessione per estrazione login configurazione dal database ".$phpoll_database);
$dati_login = mysql_fetch_assoc($estrai_login);
$string_cook_login = "phpoll_".$prepoll."_login";
$string_cook_password = "phpoll_".$prepoll."_password";
$log=$dati_login['login'];
$pw=$dati_login['password'];
$test_log = false;
if ((isset($_COOKIE[$string_cook_login])&&$log==$_COOKIE[$string_cook_login])&&(isset($_COOKIE[$string_cook_password])&&$pw==$_COOKIE[$string_cook_password])) {
    $test_log = true;
}
if ($test_log == false) {
    print "<script type=\"text/javascript\">window.location=\"index.php\";</script>";
    exit;
}

// QUERY per MySQL
$query_voti = "SELECT * FROM ".$tab_voti.";";

$estrai_voti = mysql_query($query_voti, $phpoll_db)
	or die ("Errore nella connessione per estrazione voti al database ".$phpoll_database);
	
// QUERY per MySQL
$query_band = "SELECT * FROM ".$tab_band." ORDER BY nome_band;";	
	
while ($dati_voti=mysql_fetch_assoc ($estrai_voti)) {
	

	if ($_POST[$dati_voti['id']]=="on") {
		
		$query_delete = "DELETE FROM `".$tab_voti."` WHERE `id` = ".$dati_voti['id']." LIMIT 1;";
		$delete_voti = mysql_query($query_delete, $phpoll_db)
			or die ("Errore nella connessione per cancellazione voti al database ".$phpoll_database);
		
		$estrai_band = mysql_query($query_band, $phpoll_db)
			or die ("Errore nella connessione per estrazione nomi band al database ".$dphpoll_atabase);	
			
		while ($dati_band=mysql_fetch_assoc ($estrai_band)) {	
				
		if (stristr($dati_voti['band_votate'], $dati_band['nome_band'])) {
			
			$voti=$dati_band['voti']-1;
			
			$query_update = "UPDATE `".$tab_band."` SET `voti` = '".$voti."' WHERE `id` = ".$dati_band['id']." LIMIT 1;";
			$update_voti = mysql_query($query_update, $phpoll_db)
				or die ("Errore nella connessione per cancellazione voti al database ".$phpoll_database);
				
			
		}
		
		
		}
		
		unset ($estrai_band);		
					
	}	
	
}

mysql_close ($phpoll_db);

print "<script type=\"text/javascript\">window.location=\"votanti.php?language=".$_GET['language']."\";</script>";
	
	
	
?>
	
	

</body>
</html>