<!--
function form_val(form1)
{
	
	if (form1.ud_event.value == "")
	{
		alert("Please enter the event name");
		form1.ud_event.focus();
		return (false);
	}
	
	if (form1.ud_month.value == "")
	{
		alert("Please select the month");
		form1.ud_month.focus();
		return (false);
	}
	
	if (form1.ud_day.value == "")
	{
		alert("Please select the day");
		form1.ud_day.focus();
		return (false);
	}
	
	if (form1.ud_year.value == "")
	{
		alert("Please select the year");
		form1.ud_year.focus();
		return (false);
	}

	if (form1.ud_hour.value == "")
	{
		alert("Please select the start hour");
		form1.ud_hour.focus();
		return (false);
	}
	
	if (form1.ud_minute.value == "")
	{
		alert("Please select the start minute");
		form1.ud_minute.focus();
		return (false);
	}
	
	if (form1.ud_ampm.value == "")
	{
		alert("Please select either AM or PM for the start time");
		form1.ud_ampm.focus();
		return (false);
	}

/*	
	if ((form1.hour2.value < form.hour.value)&&(form1.ampm.value =="PM"))
	{
	 alert("The ending time cannot be before the starting time");
	 form1.ampm2.focus();
	 return(false);
	 }*/
	
	
	
	if (form1.ud_location.value == "")
	{
		alert("Please enter a location");
		form1.ud_location.focus();
		return (false);
	}

	if (form1.ud_description.value == "")
	{
		alert("Please enter a description");
		form1.ud_description.focus();
		return (false);
	}

	return (true);
}
//-->