<?php
  // Terrible hack, but allows us to get around duplicating the view code.
require_once("../include/users.php");
session_start();
if (!Users::is_logged_in()) {
    header("Location: " . Users::$LOGIN_URL);
    exit;
}
$usercheck = False;
include("view.php");

?>