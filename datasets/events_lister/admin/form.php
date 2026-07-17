<script Language="JavaScript" src="validate.js"></script>


<form action="<?php $_SERVER['PHP_SELF']?>" method="post" onSubmit="return form_val(this)">
<center><b>Required fields are marked with an asterisk *</b></center>
<table width="600" border="0" align="center" cellpadding="4" cellspacing="0" class="input_table">
  <tr>
    <td colspan="2" valign="top" height="1">&nbsp;</td>
  </tr>
  <tr>
    <td valign="top"><div align="right"><b> * Event:</b></div></td>
    <td valign="top"><input name="ud_event" type="text" id="event" size="55" value="<?php echo $event; ?>" class="text_field"></td>
  </tr>
  <tr valign="top">
    <td align="right"><b>* Start Date:</b></td>
    <td><table width="390" border="0" cellpadding="0" cellspacing="0">
      <tr align="right" valign="top">
        <td width="130"><div align="right">Month:
          <select name="ud_month">
                    <option value="<?php echo $month; ?>" selected><?php echo $month; ?></option>
                    <option value="01">01</option>
                    <option value="02">02</option>
                    <option value="03">03</option>
                    <option value="04">04</option>
                    <option value="05">05</option>
                    <option value="06">06</option>
                    <option value="07">07</option>
                    <option value="08">08</option>
                    <option value="09">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                  </select>
        </div></td>
        <td width="130">Day:
          <select name="ud_day">
                <option value="<?php echo $day; ?>" selected><?php echo $day; ?></option>
                <option value="01">01</option>
                <option value="02">02</option>
                <option value="03">03</option>
                <option value="04">04</option>
                <option value="05">05</option>
                <option value="06">06</option>
                <option value="07">07</option>
                <option value="08">08</option>
                <option value="09">09</option>
                <option value="10">10</option>
                <option value="11">11</option>
                <option value="12">12</option>
                <option value="13">13</option>
                <option value="14">14</option>
                <option value="15">15</option>
                <option value="16">16</option>
                <option value="17">17</option>
                <option value="18">18</option>
                <option value="19">19</option>
                <option value="20">20</option>
                <option value="21">21</option>
                <option value="22">22</option>
                <option value="23">23</option>
                <option value="24">24</option>
                <option value="25">25</option>
                <option value="26">26</option>
                <option value="27">27</option>
                <option value="28">28</option>
                <option value="29">29</option>
                <option value="30">30</option>
                <option value="31">31</option>
              </select>        </td>
        <td width="130">Year:
          <select name="ud_year">
                <option value="<?php echo $year; ?>" selected><?php echo $year; ?></option>
                <option value="<?php echo $current_year; ?>"><?php echo $current_year; ?></option>
                <option value="<?php echo $next_year; ?>"><?php echo $next_year; ?></option>
              </select>        </td>
      </tr>
    </table></td>
  </tr>
  <tr valign="top">
    <td align="right"><b>* Start time:</b></td>
    <td><table width="390" border="0" cellpadding="0" cellspacing="0">
        <tr valign="top">
          <td width="130" align="right"><div align="right">Hour:
            <select name="ud_hour">
                    <option value="<?php echo $hour; ?>" selected><?php echo $hour; ?></option>
                    <option value="01">01</option>
                    <option value="02">02</option>
                    <option value="03">03</option>
                    <option value="04">04</option>
                    <option value="05">05</option>
                    <option value="06">06</option>
                    <option value="07">07</option>
                    <option value="08">08</option>
                    <option value="09">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                  </select>
          </div></td>
          <td width="130" align="right">Min:
            <select name="ud_minute">
                <option value="<?php echo $minute; ?>" selected><?php echo $minute; ?></option>
                <option value="00">00</option>
                <option value="15">15</option>
                <option value="30">30</option>
                <option value="45">45</option>
              </select>          </td>
          <td width="130" align="right">AM/PM:
            <select name="ud_ampm">
                <option value="<?php echo $ampm; ?>" selected><?php echo $ampm; ?></option>
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>          </td>
        </tr>
    </table></td>
  </tr>
  
  <tr valign="top">
    <td align="right">&nbsp;</td>
    <td>&nbsp;</td>
  </tr>
  <tr valign="top">
    <td align="right"><b>End Date:</b></td>
    <td><table width="390" border="0" cellpadding="0" cellspacing="0">
      <tr align="right" valign="top">
        <td width="130"><div align="right">Month:
          <select name="ud_month_end">
                    <option value="<?php echo $month_end; ?>" selected><?php echo $month_end; ?></option>
                    <option value="01">01</option>
                    <option value="02">02</option>
                    <option value="03">03</option>
                    <option value="04">04</option>
                    <option value="05">05</option>
                    <option value="06">06</option>
                    <option value="07">07</option>
                    <option value="08">08</option>
                    <option value="09">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                  </select>
        </div></td>
        <td width="130">Day:
          <select name="ud_day_end">
                <option value="<?php echo $day_end; ?>" selected><?php echo $day_end; ?></option>
                <option value="01">01</option>
                <option value="02">02</option>
                <option value="03">03</option>
                <option value="04">04</option>
                <option value="05">05</option>
                <option value="06">06</option>
                <option value="07">07</option>
                <option value="08">08</option>
                <option value="09">09</option>
                <option value="10">10</option>
                <option value="11">11</option>
                <option value="12">12</option>
                <option value="13">13</option>
                <option value="14">14</option>
                <option value="15">15</option>
                <option value="16">16</option>
                <option value="17">17</option>
                <option value="18">18</option>
                <option value="19">19</option>
                <option value="20">20</option>
                <option value="21">21</option>
                <option value="22">22</option>
                <option value="23">23</option>
                <option value="24">24</option>
                <option value="25">25</option>
                <option value="26">26</option>
                <option value="27">27</option>
                <option value="28">28</option>
                <option value="29">29</option>
                <option value="30">30</option>
                <option value="31">31</option>
              </select>        </td>
        <td width="130">Year:
          <select name="ud_year_end">
                <option value="<?php echo $year_end; ?>" selected><?php echo $year_end; ?></option>
                <option value="<?php echo $current_year; ?>"><?php echo $current_year; ?></option>
                <option value="<?php echo $next_year; ?>"><?php echo $next_year; ?></option>
              </select>        </td>
      </tr>
    </table></td>
  </tr>
  <tr valign="top">
    <td align="right"><b>End time:</b></td>
    <td><table width="390" border="0" cellpadding="0" cellspacing="0">
      <tr valign="top">
        <td width="130" align="right"><div align="right">Hour:
          <select name="ud_hour_end" id="hour_end">
                    <option value="<?php echo $hour_end; ?>" selected><?php echo $hour_end; ?></option>
                    <option value="01">01</option>
                    <option value="02">02</option>
                    <option value="03">03</option>
                    <option value="04">04</option>
                    <option value="05">05</option>
                    <option value="06">06</option>
                    <option value="07">07</option>
                    <option value="08">08</option>
                    <option value="09">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                  </select>
        </div></td>
        <td width="130" align="right">Min:
          <select name="ud_minute_end" id="minute_end">
                <option value="<?php echo $minute_end; ?>" selected><?php echo $minute_end; ?></option>
                <option value="00">00</option>
                <option value="15">15</option>
                <option value="30">30</option>
                <option value="45">45</option>
              </select>        </td>
        <td width="130" align="right">AM/PM:
          <select name="ud_ampm_end" id="ampm_end">
                <option value="<?php echo $ampm_end; ?>" selected><?php echo $ampm_end; ?></option>
                <option value="AM">AM</option>
                <option value="PM">PM</option>
            </select></td>
      </tr>
    </table></td>
  </tr>
  <tr>
    <td valign="top" align="right"><b>Show until:</b></td>
    <td valign="top"><table width="480" border="0" cellpadding="0" cellspacing="0">
      <tr align="right" valign="top">
        <td width="130"><div align="right">Month:
          <select name="ud_month_show">
                    <option value="<?php echo $month_show; ?>" selected><?php echo $month_show; ?></option>
                    <option value="01">01</option>
                    <option value="02">02</option>
                    <option value="03">03</option>
                    <option value="04">04</option>
                    <option value="05">05</option>
                    <option value="06">06</option>
                    <option value="07">07</option>
                    <option value="08">08</option>
                    <option value="09">09</option>
                    <option value="10">10</option>
                    <option value="11">11</option>
                    <option value="12">12</option>
                  </select>
        </div></td>
        <td width="130">Day:
          <select name="ud_day_show">
                <option value="<?php echo $day_show; ?>" selected><?php echo $day_show; ?></option>
                <option value="01">01</option>
                <option value="02">02</option>
                <option value="03">03</option>
                <option value="04">04</option>
                <option value="05">05</option>
                <option value="06">06</option>
                <option value="07">07</option>
                <option value="08">08</option>
                <option value="09">09</option>
                <option value="10">10</option>
                <option value="11">11</option>
                <option value="12">12</option>
                <option value="13">13</option>
                <option value="14">14</option>
                <option value="15">15</option>
                <option value="16">16</option>
                <option value="17">17</option>
                <option value="18">18</option>
                <option value="19">19</option>
                <option value="20">20</option>
                <option value="21">21</option>
                <option value="22">22</option>
                <option value="23">23</option>
                <option value="24">24</option>
                <option value="25">25</option>
                <option value="26">26</option>
                <option value="27">27</option>
                <option value="28">28</option>
                <option value="29">29</option>
                <option value="30">30</option>
                <option value="31">31</option>
              </select>        </td>
        <td width="130">Year:
          <select name="ud_year_show">
                <option value="<?php echo $year_show; ?>" selected><?php echo $year_show; ?></option>
                <option value="<?php echo $current_year; ?>"><?php echo $current_year; ?></option>
                <option value="<?php echo $next_year; ?>"><?php echo $next_year; ?></option>
              </select>        </td>
        <td><!--<div align="left" class="small"> &nbsp; (optional) </div>--></td>
      </tr>
    </table></td>
  </tr>
  <tr>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td valign="top" align="right"><div align="right"><b>* Location:</b></div></td>
    <td valign="top"><input name="ud_location" type="text" id="location" size="55" value="<?php echo $location; ?>"class="text_field"></td>
  </tr>
  <tr>
    <td valign="top" align="right"><b>Email:</b></td>
    <td valign="top"><input name="ud_email" type="text" id="email" size="55" value="<?php echo $email; ?>"class="text_field"></td>
  </tr>
  <tr>
    <td valign="top" align="right"><b>Phone:</b></td>
    <td valign="top"><input name="ud_phone" type="text" id="phone" size="55" value="<?php echo $phone; ?>"class="text_field"></td>
  </tr>
  <tr>
    <td valign="top" align="right"><b>link:</b></td>
    <td valign="top"><input name="ud_link" type="text" id="link" size="55" value="<?php echo $link; ?>"class="text_field">
        <br>
        <i class="small">example: http://www.yourwebsite.com</i><br>
        <br>    </td>
  </tr>
  <tr>
    <td valign="top" align="right"><b>Link Name:</b></td>
    <td valign="top"><input name="ud_link_name" type="text" id="link_name" size="55" value="<?php echo $link_name; ?>" class="text_field">
        <br>
        <i class="small">example: visit our web site <br>
      </i></td>
  </tr>
  <tr>
    <td colspan="2" valign="top"><table border="0" cellpadding="5" width="99%" align="center">
      <tr>
        <td><div align="left"><b>* Description:</b> &nbsp;   Normal (TEXT):
          <input name="ud_html" type="radio" value="0" checked>
          &nbsp; HTML:
          <input name="ud_html" type="radio" value="1">
          <br>
          <textarea name="ud_description"  rows="10" id="description" wrap="virtual" class="text_area"><?php echo $description; ?></textarea>
        </div></td>
      </tr>
    </table></td>
  </tr>
  <tr>
    <td valign="top" colspan="2"><center>
    </center></td>
  </tr>
</table>
<p align="center">

<input type="Submit" value="<?php echo $submit_label; ?>" name="submit"></p>

</form>
