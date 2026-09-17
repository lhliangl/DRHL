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

if(!function_exists('str_split')){
   function str_split($string,$split_length=1){
       $count = strlen($string); 
       if($split_length < 1){
           return false; 
       } elseif($split_length > $count){
           return array($string);
       } else {
           $num = (int)ceil($count/$split_length); 
           $ret = array(); 
           for($i=0;$i<$num;$i++){ 
               $ret[] = substr($string,$i*$split_length,$split_length); 
           } 
           return $ret;
       }     
   } 
}

$barra1array = str_split ($_POST['barra1']);
$b1r = $barra1array[1].$barra1array[2];
$b1g = $barra1array[3].$barra1array[4];
$b1b = $barra1array[5].$barra1array[6];
$barra1r = hexdec ($b1r);
$barra1g = hexdec ($b1g);
$barra1b = hexdec ($b1b);

$barra2array = str_split ($_POST['barra2']);
$b2r = $barra2array[1].$barra2array[2];
$b2g = $barra2array[3].$barra2array[4];
$b2b = $barra2array[5].$barra2array[6];
$barra2r = hexdec ($b2r);
$barra2g = hexdec ($b2g);
$barra2b = hexdec ($b2b);

$barra3array = str_split ($_POST['barra3']);
$b3r = $barra3array[1].$barra3array[2];
$b3g = $barra3array[3].$barra3array[4];
$b3b = $barra3array[5].$barra3array[6];
$barra3r = hexdec ($b3r);
$barra3g = hexdec ($b3g);
$barra3b = hexdec ($b3b);

$barra4array = str_split ($_POST['barra4']);
$b4r = $barra4array[1].$barra4array[2];
$b4g = $barra4array[3].$barra4array[4];
$b4b = $barra4array[5].$barra4array[6];
$barra4r = hexdec ($b4r);
$barra4g = hexdec ($b4g);
$barra4b = hexdec ($b4b);


// assegno le variabili di connessione
$phpoll_db = mysql_connect ($phpoll_host, $phpoll_user, $phpoll_password)
	or die ("Errore nella connessione a MySQL");
	
// selezione del database
mysql_select_db($phpoll_database, $phpoll_db)
	or die ("Errore nella connessione al database ".$phpoll_database);

$query_login = "SELECT login, password FROM phpoll_".$prepoll."_configurazione;";
$estrai_login = mysql_query($query_login, $phpoll_db) or die ("Errore nella connessione per estrazione login configurazione dal database ".$phpoll_database);
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

$query_svuota_config = "TRUNCATE TABLE `phpoll_".$prepoll."_configurazione`";

$svuota_config = mysql_query($query_svuota_config, $phpoll_db)
	or die ("Errore nella connessione per svuotamento dati configurazione al database ".$database);		
	
if ((isset($_POST['login'])&&$_POST['login']!="")&&(isset($_POST['password'])&&$_POST['password']!="")) {
	$log = $_POST['login'];
	$pw = $_POST['password'];
}
else {
	$log = $_POST['old_login'];
	$pw = $_POST['old_password'];
}

// $testoemail = str_replace ($esc_chars, $sos_chars, $_POST['testo_email']);

$testoemail = $_POST['testo_email'];
	
$query_inserisci_config = "INSERT INTO `phpoll_".$prepoll."_configurazione` ( `id` , `messaggio_ip`, `intervallo_tempo`, `testo_submit`, `max_voti` , `domini` , `oggetto_email`, `testo_email`, `valid_email`, `messaggio_conferma_mail`, `messaggio_domini` , `messaggio_giavotato` , `messaggio_sgamo` , `titolo_posizione` , `titolo_tipologia` , `titolo_punteggio` , `risultati_pixel`, `login`, `password`,".
	"`barra1r`, `barra1g`, `barra1b`, `barra2r`, `barra2g`, `barra2b`, `barra3r`, `barra3g`, `barra3b`, `barra4r`, `barra4g`, `barra4b`, `percorso_link`) ".
	"VALUES ('', '".$_POST['messaggio_ip']."', '".$_POST['intervallo_tempo']."', '".$_POST['testo_submit']."', '".$_POST['max_voti']."', '".$_POST['domini']."', '".$_POST['oggetto_email']."', '".$testoemail."', '".$_POST['valid_email']."', '".$_POST['messaggio_conferma_mail']."', '".$_POST['messaggio_domini']."', '".$_POST['messaggio_giavotato']."', '".$_POST['messaggio_sgamo']."', '".$_POST['titolo_posizione']."', '".$_POST['titolo_tipologia']."', '".$_POST['titolo_punteggio']."', '".$_POST['risultati_pixel']."', '".$log."', '".$pw."', ".
	"'".$barra1r."', '".$barra1g."', '".$barra1b."', '".$barra2r."', '".$barra2g."', '".$barra2b."', ".
	"'".$barra3r."', '".$barra3g."', '".$barra3b."', '".$barra4r."', '".$barra4g."', '".$barra4b."', '".$_POST['percorso_link']."' );";
	
$inserisci_config = mysql_query($query_inserisci_config, $phpoll_db)
	or die ("Errore nella connessione per inserimento dati configurazione al database ".$database);			  
	
mysql_close ($phpoll_db);

$immagine = imagecreate (1,10);
$colore = imagecolorallocate ($immagine, $barra1r, $barra1g, $barra1b);
imagefill ($immagine, 0, 0, $colore);
imagegif ($immagine, "../img/barra1.gif"); 	
imagedestroy ($immagine);
$immagine = imagecreate (1,10);
$colore = imagecolorallocate ($immagine, $barra2r, $barra2g, $barra2b);
imagefill ($immagine, 0, 0, $colore);
imagegif ($immagine, "../img/barra2.gif"); 	
imagedestroy ($immagine);
$immagine = imagecreate (1,10);
$colore = imagecolorallocate ($immagine, $barra3r, $barra3g, $barra3b);
imagefill ($immagine, 0, 0, $colore);
imagegif ($immagine, "../img/barra3.gif"); 	
imagedestroy ($immagine);
$immagine = imagecreate (1,10);
$colore = imagecolorallocate ($immagine, $barra4r, $barra4g, $barra4b);
imagefill ($immagine, 0, 0, $colore);
imagegif ($immagine, "../img/barra4.gif"); 	
imagedestroy ($immagine);


print "<script type=\"text/javascript\">window.location=\"config_editor.php?language=".$_GET['language']."\";</script>";

?>
	
	

</body>
</html>