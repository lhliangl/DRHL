<!--

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

-->

<?php

if (isset ($_GET['language'])) { 
	$language=(int)$_GET['language'];
}

else {
	$language=1;
}

if (isset ($_GET['nuova_band'])) { 
	$nuova_band=(int)$_GET['nuova_band'];
}

else {
	$nuova_band=2;
}

if ($language==0||$nuova_band==0) {

  die ("Try a different way!");

}

include "../config/config.php";
include "localization.php";

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">

<head>

<title>PHPOLL - band editor</title>
<link rel="stylesheet" href="css/phpoll_layout.css" title="phpoll layout" />
</head>
<body>

<?php

// assegno le variabili di connessione
$phpoll_db = mysql_connect ($phpoll_host, $phpoll_user, $phpoll_password)
	or die ("Errore nella connessione a MySQL");
	
// selezione del database
mysql_select_db($phpoll_database, $phpoll_db)
	or die ("Errore nella connessione al database ".$phpoll_database);
		
// controllo login amministratore
$query_login = "SELECT login, password FROM phpoll_".$prepoll."_configurazione;";
$estrai_login = mysql_query($query_login, $phpoll_db)
	or die ("Errore nella connessione per estrazione login configurazione dal database ".$phpoll_database);
$dati_login = mysql_fetch_assoc($estrai_login);
if (!$dati_login) {
	die ("Try a different way!");
}
$string_cook_login = "phpoll_".$prepoll."_login";
$string_cook_password = "phpoll_".$prepoll."_password";
$log=$dati_login['login'];
$pw=$dati_login['password'];
$test_log = false;
if ((isset($_COOKIE[$string_cook_login])&&$log==$_COOKIE[$string_cook_login])&&(isset($_COOKIE[$string_cook_password])&&$pw==$_COOKIE[$string_cook_password])) {
	$test_log = true;
}
if (!$test_log) {
	die ("Try a different way!");
}
$esc_chars = array ("'", "/", "\"");
$sos_chars = array ("&apos;", "\/", "&quot;");
	
if ($nuova_band==2) {	
	
// QUERY per MySQL
$query_band = "SELECT * FROM ".$tab_band." ORDER BY nome_band;";

$estrai_band = mysql_query($query_band, $phpoll_db)
	or die ("Errore nella connessione per estrazione nomi band al database ".$phpoll_database);	

$i=0;	
while ($dati_band=mysql_fetch_assoc ($estrai_band)) {
	
	$stringa_nome_band = "nome_band_".$i;
	$stringa_voti = "voti_".$i;
	$stringa_check = "check_".$i;
	$stringa_id = "id_".$i;

	$nome_banda =  str_replace ($esc_chars, $sos_chars, $_POST[$stringa_nome_band]);
		
	$query_replace_nome = "UPDATE `".$tab_band."` SET `nome_band` = '".$nome_banda."' WHERE `id` = ".$_POST[$stringa_id]." LIMIT 1 ;";
	$query_replace_voti = "UPDATE `".$tab_band."` SET `voti` = '".$_POST[$stringa_voti]."' WHERE `id` = ".$_POST[$stringa_id]." LIMIT 1 ;";
		 
	$query_delete = "DELETE FROM ".$tab_band." WHERE `id`='".$_POST[$stringa_id]."';";
								 
	if ($_POST[$stringa_check]=="on") {
				   
		$delete = mysql_query ($query_delete, $phpoll_db)
			or die ("Errore durante il DELETE");
		
		//print $query_delete;
						
	}
				
	if ($_POST[$stringa_nome_band]!=$dati_band['nome_band']) {				 
								 
		$replace = mysql_query ($query_replace_nome, $phpoll_db)
			or die ("Errore durante il REPLACE");
		
		//print $query_replace_nome;
							
	}

	if ($_POST[$stringa_voti]!=$dati_band['voti']) {				 
								 
		$replace = mysql_query ($query_replace_voti, $phpoll_db)
			or die ("Errore durante il REPLACE");
		
		//print $query_replace_voti;
							
	}
	
	$i++;

}

}

else if ($nuova_band==1) {
	
	if ($_POST['nome_band']!="") {
		
		$nome_banda =  str_replace ($esc_chars, $sos_chars, $_POST['nome_band']);
	
		$query_inserisci = "INSERT INTO `".$tab_band."` ( `id` , `nome_band` , `voti` ) VALUES ('', '".$nome_banda."', '".$_POST['voti']."');";
	
		$inserisci_band = mysql_query($query_inserisci, $phpoll_db)
			or die ("Errore nella connessione per inserimento nuova band al database ".$phpoll_database);
			
	}
	
	else {
		
		print "<script type=\"text/javascript\">alert(\"".$config_alert_nuovocandidatovuoto."\");</script>";
		
		
	}	

	
}

mysql_close ($phpoll_db);

print "<script type=\"text/javascript\">window.location=\"band_editor.php?language=".$language."\";</script>";

?>

</body>
</html>