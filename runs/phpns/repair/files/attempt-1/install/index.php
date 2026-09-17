<?php
//constant proclaiming installation in progress
define("INSTALLING",1);

@include_once("../inc/config.php");
@session_start();
if (@$globalvars['installed'] == "yes" && @$_SESSION['auth'] != "yes") {
    header("Location: ../login.php");
    die();
}

function db_form($data=NULL) {
    global $error_message;
    if (!$data['db_tableprefix']) {
        $data['db_tableprefix'] = 'phpns_';
    }
    if (!$data['db_host']) {
        $data['db_host'] = 'localhost';
    }
    $content = '
    '.$error_message.'
    <form action="index.php?step=2" method="post">
    <div class="form">
        <h3>Database information</h3>
        <label for="type">Database type</label>
        <select id="type" style="width: 400px">
            <optgroup label="Select a database type...">
                <option>mySQL database</option>
            </optgroup>
        </select>
        <br />
        <label for="db_host">Database host</label>
        <input type="text" name="db_host" value="'.$data['db_host'].'" /> (Usually "localhost")
        <br />
        <label for="db_user">Database user</label>
        <input type="text" name="db_user" value="'.$data['db_user'].'" />
        <br />
        <label for="db_password">Database password</label>
        <input type="password" name="db_password" value="'.$data['db_password'].'" />
        <br /><br />
        <label for="db_name">Database name</label>
        <input type="text" name="db_name" value="'.$data['db_name'].'" />
        <br />
        <label for="db_tableprefix">Table prefix</label>
        <input type="text" name="db_tableprefix" value="'.$data['db_tableprefix'].'" />
        <br />
        <h3>Admin information</h3>
        <br />
        <label for="username">Admin username</label>
        <input type="text" name="username" value="'.$data['username'].'" />
        <br />
        <label for="password">Admin password</label>
        <input type="password" name="password" value="'.$data['password'].'" />
        <br />
        <label for="c_password">Confirm password</label>
        <input type="password" name="c_password" value="'.$data['c_password'].'" />
    </div>
    <div class="alignr">
        <input type="submit" id="submit" value="Continue" />
    </div>
    </form>
    ';
    return $content;
}

//get step
$step = $_GET['step'];

if (!$step) {
    $logo = '';
    $license_txt = file_get_contents("../docs/LICENSE");
    $content = '
        <form action="index.php?step=1" method="post">
        <textarea style="width: 100%; height: 200px;" readonly="readonly">
        '.$license_txt.'
        </textarea>
        <br />
        <div class="alignr">
            <label><input type="checkbox" id="upgrade" name="upgrade" value="TRUE" />Upgrade from V1.x</label>
            <input type="submit" id="submit" value="Continue" />
        </div>
        </form>
    ';
} elseif ($step == 1) { //step 1
    //If upgrade is selected, then go directly to upgrade
    if($_POST[upgrade] == TRUE){
        header("location: upgrade.php");
    }
    $content = db_form();
} elseif ($step == 2) { //step 2 : check data.
    //get data from post, now we'll verify...
    $data = $_POST;
    //set continue to TRUE, then we'll make sure everything is ok
    $continue = TRUE;
    foreach ($data as $key=>$value) {
        if ($value == NULL && $key != 'db_tableprefix') {
            $continue = FALSE;
            echo "";
            $error_message = '<div class="warning">You need to fill out all the fields (excluding the table prefix)</div>';
        }
    }
    if ($data['password'] && ($data['password'] != $data['c_password'])) {
        $error_message .= '<div class="warning">Your passwords do not match.</div>';
        $continue = FALSE;
    } elseif ($data['password']) {
        $data['password'] = sha1($data['password']);
    }
    if ($continue == TRUE) { //if all fields are full, we move on to verification. First, we'll do the db stuff.
        if (!$connection = @mysql_connect($data['db_host'], $data['db_user'], $data['db_password'])) {
            $error_message .= '<div class="warning">We could not connect to the database ('.$data['db_host'].') with the information you provided. This is most likely due to a misspelled username or password. If you are sure you provided correct information, the user you are using probably doesn\'t exist on the server you specified.</div>';
            $continue = FALSE;
        }
        if (!@mysql_select_db($data['db_name'], $connection)) {
            $error_message .= '<div class="warning">We could not find the database ('.$data['db_name'].') you specified. You might have spelled the database wrong, or, you are not connected to a database (you would recieve a previous error if this was the case).</div>';
            $continue = FALSE;
        }
        //if connection is active, insert data
        if ($continue == TRUE) {
            include_once("install.inc.php");
        }
    }
    if ($continue == FALSE) {
        //if there were errors, we're going to redisplay the form with errors (inside the function)
        $content = db_form($data);
    } elseif ($continue == TRUE) {
        //else if we have no errors, we serialize the $data, and head over to ?step=3
        $data = serialize($data);
        $data = str_replace('\"', "'", $data); //replace all \"s with 's as to be xhtml compliant in hidden form
        $url = str_replace('install/index.php','',$_SERVER['PHP_SELF']);
        $content = '
        <h3>Configuration finished</h3>
        <p>You have filled in all the fields in the previous step successfully. Now, we need to write the configuration to the phpns config.php file, so it can be used globally across the whole system. But, before we can do this, we need you to give this script proper permissions. Please do the following:
        <ol>
            <li>Using your favorite FTP application, login to your website directory, and navigate to where you uploaded the phpns system ('.$url.').</li>
            <li>Now, you need to navigate to: /inc</li>
            <li>Select the config.php file</li>
            <li>Change the permissions of the file to 0777, or 777.</li>
            <li>Return to this installation guide, and press continue.</li>
            <form action="index.php?step=3" method="post">
                <input type="hidden" name="config" value="'.$data.'" />
                <div class="alignr">
                    <input type="submit" id="submit" value="Continue" />
                </div>
            </form>
        ';
    }
} elseif ($step == 3) { //else if step 3
    //unserialize string passed through form, get back array
    $data = unserialize(str_replace("'", '"', stripslashes($_POST['config'])));
    //form file contents
    $fcontent = '<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

//This is the file generated by the installation. Copy and paste this into the /inc/config.php file. If neceessary, you should edit anything needed below.

//The Host is where the mySQL database is stored. Usually localhost.
$databaseinfo[\'host\'] = "'.$data['db_host'].'";

//The user your database is assigned to.
$databaseinfo[\'user\'] = "'.$data['db_user'].'";

//The password of your user.
$databaseinfo[\'password\'] = "'.$data['db_password'].'";

//The database name that phpns will use.
$databaseinfo[\'dbname\'] = "'.$data['db_name'].'";

//The table prefix defined on the database.
$databaseinfo[\'prefix\'] = "'.$data['db_tableprefix'].'";

//Change the variable below to "yes", once you have completed the above.
$globalvars[\'installed\'] = "yes";



?>';
    $continue = TRUE;
    if ($filec = @fopen("../inc/config.php",'w')) { //if we can open
        //if we can open the file for reading...
        if (!@fwrite($filec, $fcontent)) {
            $error_message .= '<div class="warning">We opened the config.php file, but we could not write to it. This is probably because you didn not set the file permissions correctly.</div>';
            $continue = FALSE;
        }
    } else {
        $error_message .= '<div class="warning">We could not open the config.php file to edit with your configuration options. The file permissions probably are not set correctly.</div>';
        $continue = FALSE;
    }
    //if problems with writing to file, give them the code to edit the file themselves.
    if ($continue == FALSE) {
        $content = '
        <h3>Error writing to config.php</h3>
        <p>We could not edit the file with your configuration. This is probably due to wrong file permissions. You can try to set the permissions again, and refresh this page. However, if you really do not know what you are doing, you can open the file on the server, and replace everything in the file with the following:</p>
        <textarea style="width: 600px; height: 300px;" readonly="readonly">'.$fcontent.'</textarea>
        ';
    } else {
        $content = '
        <h3>Success</h3>
        <p>We have successully edited the config.php file with your configuration, and created the database structure. Installation is complete, here is what you do:</p>
        <ol>
            <li>Open your FTP or File browser on the server</li>
            <li>Navigate to the phpns directory, and DELETE the /install directory</li>
            <li>Navigate to the <a href="../">login page</a>, and login with your recently created admin account</li>
        </ol>
        <p>A copy of the config.php file is attached below for your reference.</p>
        <textarea style="width: 600px; height: 300px;" readonly="readonly">'.$fcontent.'</textarea>
        ';
    }
}

include("install.tmp.php");
?>