<?php
/*
    This file is a part of Basic PHP Events Lister.  Copyright (c) 2008 Mark MacCollin, Mevin Productions, www.mevin.com

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


// Database info

// Your MySQL host
$dbhost='localhost';
$dbport ='3306';

//Your MySQL username
$dbuser='root';

//Your MySQL password
$dbpass='root';

//Your MySQL database name
$dbname='events_lister';

//Maximum number of displayed events
$maxnum='10';

/* Your website url, with the directory where Basic PHP Events List is installed.  
Do NOT add the trailing slash. e.g. http://www.yourwebsite.com/events is OK, but http://www.yourwebsite.com/events/ is NOT.
*/
$website='http://www.yourwebsite.com/events';   

/*
The salt variable helps the script to further obscure the hash of your password in the database.  
Your password is "hashed" before it is stored in the database, but it is possible that if a hacker 
were to obtain the hashed version of your password, he or she could reverse engineer the hash to 
show the actual password.  When you salt the hash, with your own unique code, you make it much more 
difficult (Have to avoid the use of the word impossible here :)) to obtain your password.  

That's a very long way of saying, put 5 or 6 characters of YOUR OWN nonsense in the salt variable to 
make your password more secure.  If you choose not to use your own salt, the system will still
work, but will be a little less secure.  Good times!!
*/ 

$salt='bla947';

////////// END OF REQUIRED CONFIGURATION OPTIONS /////////////

/// Do NOT change these options.  If you do you risk breaking the script. 
/// Future versions will have the option of easily changing the date format, 
/// For now the only way to accomplish a date format change is to add PHP date filters in the display files (index.php or event.php

$current_month = date('m');
$month_after_next = ($current_month + 2);
$current_day = date('d');
$current_year = date('Y');
$next_year = ($current_year + 1);

?>


