<?php

$date = date("d/m/Y");
header('Content-type: application/sql');
header('Content-Disposition: attachment; filename="backup_'.$date.'.sql"');
$noheads = 'yes';
include ("../common.php");

if ($member_level !== 'admin') {
    exit;
}


      function mysql_dump($database) {
      $query = '';
      $tables = @mysql_list_tables($database);
      while ($row = @mysql_fetch_row($tables)) { $table_list[] = $row[0]; }
      for ($i = 0; $i < @count($table_list); $i++) {
      $results = mysql_query('DESCRIBE ' . $database . '.' . $table_list[$i]);
      $query .= 'DROP TABLE IF EXISTS `' . $database . '.' . $table_list[$i] . '`;' . lnbr;
      $query .= lnbr . 'CREATE TABLE `' . $database . '.' . $table_list[$i] . '` (' . lnbr;
      $tmp = '';
      while ($row = @mysql_fetch_assoc($results)) {
      $query .= '`' . $row['Field'] . '` ' . $row['Type'];
      if ($row['Null'] != 'YES') { $query .= ' NOT NULL'; }
      if ($row['Default'] != '') { $query .= ' DEFAULT \'' . $row['Default'] . '\''; }
      if ($row['Extra']) { $query .= ' ' . strtoupper($row['Extra']); }
      if ($row['Key'] == 'PRI') { $tmp = 'primary key(' . $row['Field'] . ')'; }

      $query .= ','. lnbr;

      }

      $query .= $tmp . lnbr . ');' . str_repeat(lnbr, 2);

      $results = mysql_query('SELECT * FROM ' . $database . '.' . $table_list[$i]);

      while ($row = @mysql_fetch_assoc($results)) {

      $query .= 'INSERT INTO `' . $database . '.' . $table_list[$i] .'` (';

      $data = Array();

      while (list($key, $value) = @each($row)) { $data['keys'][] = $key; $data['values'][] = addslashes($value); }

      $query .= join($data['keys'], ', ') . ')' . lnbr . 'VALUES (\'' . join($data['values'], '\', \'') . '\');' . lnbr;

      }

      $query .= str_repeat(lnbr, 2);

      }

      return $query;

      }

echo mysql_dump("$db_database");

?>
