<?php
  // Terrible hack, but allows us to get around duplicating the view code.
$usercheck = False;
require_once("../include/users.php");
if (!Users::is_logged_in()) {
    header("Location: " . Users::$LOGIN_URL);
    exit;
}
include("view.php");

?>