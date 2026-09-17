<%@page contentType="text/html"%>
<%@ include file="auth.jsp" %>
<html>
<!-- Programmed in JSP by Anthony Ehrhardt -->
<!-- cguru.ma.cx released under the GPL (GNU Public license -->
<head><title>Add Author</title></head>
<basefont face="Arial">
<body>
<center>
<h1>Add Author</h1>
<br>
<table border=0 cellspacing=5 cellpadding=5>
<form action="adduser2.jsp" method="POST"> <tr>
<td><b>Email Address</b></td>
<td><INPUT name='author' type='text' size='50'>
</TD></TR>

<td><b>Full Name</b></td>
<td><INPUT name='name' type='text' size='50'>
</TD></TR>
<tr>
<td colspan=2><input type="submit" name="submit" value="Add"></td>
</tr> </form>
</table>
</body>
</html>

