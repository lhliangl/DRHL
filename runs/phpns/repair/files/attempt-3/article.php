<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

include("inc/header.php");
$do = $_GET['do'];
	//if we're previewing an article... set do to preview
	if (isset($_POST['preview'])) { $do = 'preview'; }
	if (!$do) {

		//quick permission check (redir to error)
		if ($globalvars['rank'][10] == 0) {
			header("Location: index.php?do=permissiondenied");
			die();	
		}
		
	$globalvars['page_name'] = 'new article'; //set page name
	
	//The do var is empty; display new article form
	$content = article_form();  //display form (function in function.php)
	
	} elseif ($do == "preview") {  //preview article
	
		//quick permission check (redir to error)
		if ($globalvars['rank'][10] == 0) {
			header("Location: index.php?do=permissiondenied");
			die();
		}
			$globalvars['page_name'] = 'preview article';
			$globalvars['page_image'] = 'new article';
		//define new item array from POST data
			$data['article_title'] = $_POST['article_title'];
			$data['article_subtitle'] = $_POST['article_subtitle'];
			$data['article_cat'] = $_POST['article_cat'];
			$data['article_text'] = $_POST['article_text'];
			$data['article_exptext'] = $_POST['article_exptext'];
			$data['acchecked'] = $_POST['acchecked'];
			$data['achecked'] = $_POST['achecked'];
			$data['start_date'] = $_POST['start_date'];
			$data['end_date'] = $_POST['end_date'];
			$data['archived'] = "0";
			$data['approved'] = "0";
		
		$content = '
			<hr />
			<h1 class="preview_title">'.$data['article_title'].'</h1>
			<div class="preview_main">
				'.$data['article_text'].'
			</div>
			<div class="preview_full">
				'.$data['article_exptext'].'
			</div>
			<hr />
			'.article_form().'
		';
	
	} elseif ($do == "p") { //if new form submitted
		
		//quick permission check (redir to error)
		if ($globalvars['rank'][10] == 0) {
			header("Location: index.php?do=permissiondenied");
			die();	
		}
		
		//now, if this user needs approval to post, we'll set the approve to 0 (which is 'no', or not approved) ELSE, 1
		if ($globalvars['rank'][10] == 2) {
			$data['approved'] = 0;
		} else {
			$data['approved'] = 1;
		}
		
		
		
		if(isset($_POST)) {
			$proceed = "yes"; //for verification later
			
			//define new item array from POST data
			$data['article_title'] = $_POST['article_title'];
			$data['article_subtitle'] = $_POST['article_subtitle'];
			$data['article_cat'] = $_POST['article_cat'];
			$data['article_text'] = $_POST['article_text'];
			$data['article_exptext'] = $_POST['article_exptext'];
			$data['acchecked'] = $_POST['acchecked'];
			$data['achecked'] = $_POST['achecked'];;
			$data['start_date'] = $_POST['start_date'];
			$data['end_date'] = $_POST['end_date'];
			
			// we already have this set, nulled out here for reference $data['approved'] = "0";
			
			$error_message = '<ol class="warning">';
			
			if (empty($data['article_title'])) {
				$proceed = "no";
				$error_message = $error_message.'<li>You must enter a title.</li>
				';
			}
			if (empty($data['article_text'])) {
				$proceed = "no";
				$error_message = $error_message.'<li>You must enter a main article.</li>
				';
				
			}
			if (empty($data['article_cat'])) {
				$proceed = "no";
				$error_message = $error_message.'<li>A category is necessary. You should NOT recieve this message, something is wrong. Make sure you have a category defined...</li>
				';
			}
				$error_message = $error_message.'</ol>'; //end error message ordered list
			//convert start and end date times | function will do everything, it also returns errors.
			if ($data['start_date']) {
				$unixtime['start'] = validate_date($data,'start');
			}
			if ($data['end_date']) {
				$unixtime['end'] = validate_date($data,'end');
			}
			
			
			if ($data['achecked'] == "") {  //if no value (not selected)
				$data['achecked'] = 1;
			}
			
			if ($data['acchecked'] == "") {  //if no value (not selected)
				$data['acchecked'] = 1;
			}
			
			//new article process (clean data, then submit to database)
			foreach($data as $key => $value) {
				//clean data (SQL injection security)
				$data[$key] = clean_data($value);
			}
			
			if ($proceed == "yes") {
				if ($_FILES['image']['name']) {
					if (!$data['image'] = upload_image($_FILES['image'])) {
						$proceed = "no";
						$error_message .= '<li>The image upload returned an error, which means the file was not an image, or we had trouble moving the file to (images/uploads). Check the permissions for the directory.</li>';
						$error_message = $error_message.'</ol>'; //end error message ordered list
					}
				}

				if ($proceed == "yes") { //if we're STILL ok, even with file upload... we finish up.
					new_item($data,$_SESSION['username']); //submit the data(function in inc/function.php) with username
					$globalvars['page_name'] = 'article success'; //set page name
					$globalvars['page_image'] = 'success';
				
					//set content for page success!
					$content = "";
				} else {
					$globalvars['page_name'] = 'new article'; //set page name
					$globalvars['page_image'] = 'error'; //error image
				
					//we have to convert the date back from the UNIX timestamp, IF it's in the correct format. (We already did this above)
					if ($data['acchecked'] == 0) { //if the article DISALLOWS comments, check the box
						$data['acchecked_check'] = ' checked="checked"';
					}
					if ($data['achecked'] == 0) {  //if the article is NOT active, check the box
						$data['achecked_check'] = ' checked="checked"';
					}
					$content = article_form();  //display form (function in function.php)
				}
				
			} else { //problem. display form with vars. 
				$globalvars['page_name'] = 'new article'; //set page name
				$globalvars['page_image'] = 'error'; //error image
				
				//we have to convert the date back from the UNIX timestamp, IF it's in the correct format. (We already did this above)
				if ($data['acchecked'] == 0) { //if the article DISALLOWS comments, check the box
					$data['acchecked_check'] = ' checked="checked"';
				}
				if ($data['achecked'] == 0) {  //if the article is NOT active, check the box
					$data['achecked_check'] = ' checked="checked"';
				}
				$content = article_form();  //display form (function in function.php)
			}
		}
	} elseif ($do == "edit") { //do elseif (edit)
	
		//quick permission check (redir to error)
		if ($globalvars['rank'][14] == 0) {
			header("Location: index.php?do=permissiondenied");
			die();	
		}
	
		$globalvars['page_name'] = 'edit article';  //set page name
		$globalvars['page_image'] = 'article management'; //set image
		$news_id = clean_data($_GET['id']);
			//sql and execution, grab update data from IP.
			$get_res = general_query("SELECT * FROM ".$databaseinfo['prefix']."articles WHERE id='$news_id' LIMIT 1");
		$data = mysql_fetch_assoc($get_res) or die("again.");
		if ($data['start_date']) {
			$data['start_date'] = date('m/d/Y',$data['start_date']);
		}
		if ($data['end_date']) {
			$data['end_date'] = date('m/d/Y',$data['end_date']);
		}
			//define checked boxes...
			echo $data['acchecked'];
			if ($data['allow_comments'] == 0) { //if the article DISALLOWS comments, check the box
				$data['acchecked_check'] = ' checked="checked"';
			}
			echo $data['achecked'];
			if ($data['active'] == 0) {  //if the article is NOT active, check the box
				$data['achecked_check'] = ' checked="checked"';
			}
		//display edit form
		$content = article_form();
		
	} elseif ($do == "editp") { //do elseif (edit process)
	
		//quick permission check (redir to error)
		if ($globalvars['rank'][14] == 0) {
			header("Location: index.php?do=permissiondenied");
			die();	
		}
		
		$globalvars['page_name'] = 'edit article';
			if(isset($_POST)) {
			// Ownership and cross-user access check: the article being edited must belong to the logged-in user.
			if (!isset($_POST['id'])) {
				header("Location: index.php?do=permissiondenied");
				die();
			}
			$edit_target_id = clean_data($_POST['id']);
			$edit_target_res = general_query("SELECT author FROM " . $databaseinfo['prefix'] . "articles WHERE id='" . $edit_target_id . "' LIMIT 1");
			$edit_target = mysql_fetch_assoc($edit_target_res);
			if (!$edit_target || $edit_target['author'] != $_SESSION['username']) {
				header("Location: index.php?do=permissiondenied");
				die();
			}

			$proceed = "yes"; //for verification later
			
			//define new item array from POST data
			$data['article_title'] = $_POST['article_title'];
			$data['article_subtitle'] = $_POST['article_subtitle'];
			$data['article_cat'] = $_POST['article_cat'];
			$data['article_text'] = $_POST['article_text'];
			$data['article_exptext'] = $_POST['article_exptext'];
			$data['acchecked'] = $_POST['acchecked'];
			$data['achecked'] = $_POST['achecked'];
			$data['start_date'] = $_POST['start_date'];
			$data['end_date'] = $_POST['end_date'];
			$data['approved'] = "0";
			
			$error_message = '<ol class="warning">';
			if (empty($data['article_title'])) {
				$proceed = "no";
				$error_message = $error_message.'<li>You must enter a title.</li>
				';
			}
			if (empty($data['article_text'])) {
				$proceed = "no";
				$error_message = $error_message.'<li>You must enter a main article.</li>
				';
				
			}
			if (empty($data['article_cat'])) {
				$proceed = "no";
				$error_message = $error_message.'<li>A category is necessary. You should NOT recieve this message, something is wrong. Make sure you have a category defined...</li>
				';
			}
			
			
			//convert start and end date times | function will do everything, it also returns errors.
			if ($data['start_date']) {
				$unixtime['start'] = validate_date($data,'start');
			}
			if ($data['end_date']) {
				$unixtime['end'] = validate_date($data,'end');
			}
			
			$error_message = $error_message.'</ol>';
			
			if ($data['achecked'] == "") {  //if no value (not selected)
				$data['achecked'] = 1;
			}
			if ($data['acchecked'] == "") {  //if no value (not selected)
				$data['acchecked'] = 1;
			}
			
			//new article process (clean data, then submit to database)
			foreach($data as $key => $value) {
				//clean data (SQL injection security)
				$data[$key] = clean_data($value);
			}
			if ($proceed == "yes") {
				if ($_FILES['image']['name']) {
					if (!$data['image'] = upload_image($_FILES['image'])) {
						$proceed = "no";
						$error_message .= '<li>The image upload returned an error, which means the file was not an image, or we had trouble moving the file to (images/uploads). Check the permissions for the directory.</li>';
						$error_message = $error_message.'</ol>'; //end error message ordered list
					}
				}
				
				if ($proceed == "yes") {
					$data['id'] = $_POST['id'];
					edit_item($data,$_SESSION['username']); //submit the data(function in inc/function.php) with username
					$globalvars['page_name'] = 'edit success'; //set page name
					$globalvars['page_image'] = 'success';
					$content = '';
				} else { //edit error display form and errors
					$globalvars['page_name'] = 'edit article'; //set page name
					$globalvars['page_image'] = 'error';
				
					//if the form dates are correct, recreate the human readable for edit page...
				
				if ($data['acchecked'] == 0) { //if the article DISALLOWS comments, check the box
					$data['acchecked_check'] = ' checked="checked"';
				}
				if ($data['achecked'] == 0) {  //if the article is NOT active, check the box
					$data['achecked_check'] = ' checked="checked"';
				}
					$content = article_form();  //display form (function in function.php)
				}
			} else {
				$globalvars['page_name'] = 'new article'; //set page name
				$globalvars['page_image'] = 'error'; //error image
				
				//we have to convert the date back from the UNIX timestamp, IF it's in the correct format. (We already did this above)
				if ($data['acchecked'] == 0) { //if the article DISALLOWS comments, check the box
					$data['acchecked_check'] = ' checked="checked"';
				}
				if ($data['achecked'] == 0) {  //if the article is NOT active, check the box
					$data['achecked_check'] = ' checked="checked"';
				}
				$content = article_form();  //display form (function in function.php)
			}
		}
	} elseif ($do == "activate") {
		//activating the article, function and then redirect.
			$id = $_GET['id'];
		approve($id);
		header("Location: article.php?do=edit&id=$id");
	
	} elseif ($do == "comments") {
		if ($_GET['action'] == 'delete') {
			$items = $_POST; //get vars
				if (!$items) { //if no items, avoid mysql error by just redirecting
					header("Location: ?do=comments&id=".$_GET['id']."");
				}
					//we're going to create list of ids to be deleted from database.
					foreach($items as $key=>$value) {
						$items_f = $items_f."'$key',";
					}
					//remove last comma in list for SQL
					$items_f = substr_replace($items_f,"",-1);
					//delete the items in 'articles'
					delete('comments',$items_f);
					
					//log this
					log_this('delete_comments','User <i>'.$_SESSION['username'].'</i> has <strong>deleted</strong> the comments: "'.$items_f.'"');
		}
		//if the id isn't numeric, kill the script. Injection protection.
		if (!is_numeric($_GET['id'])) { die("non numeric article id"); }
			$id = $_GET['id'];
		$globalvars['page_name'] = 'Comment list ('.$id.')';
		$globalvars['page_image'] = '0';
		
		//now, we generate comments for this specific article
			//get the template currently active in the installation
			$template = fetch_template();
		$fetch_com_res = general_query("SELECT * FROM ".$databaseinfo['prefix']."comments WHERE article_id='".$id."' AND approved='1'");
			//for each row (or comment) generated, we translate the item and assign it to $content
			while ($row = mysql_fetch_assoc($fetch_com_res)) {
				$comment_list .= '<div class="checkbox"><input type="checkbox" name="'.$row['id'].'" value="'.$row['id'].'" /></div>'.translate_comment($row, $template['html_comment'], 'html_comment');
			}
			//assign $comment_list to $content
			$content .= '
				<div><button class="activate" OnClick="window.location = \'?do=edit&id='.$id.'\';"><strong>Back to edit article</strong></button></div>
				<form action="?do=comments&id='.$id.'&action=delete" method="post">
					<div style="text-align: right;"><input id="selectall" type="checkbox" onClick="Checkall(this.form);" /></div>
					'.$comment_list.'
					<div class="alignr">
						<input type="submit" id="submit" value="Delete selected comments" />
					</div>
				</form>
			';
	
	} //end of main do


include("inc/themecontrol.php");  //include theme script
?>
