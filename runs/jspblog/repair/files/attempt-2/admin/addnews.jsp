<%@page contentType="text/html"%>
<%@ include file="auth.jsp" %>
<html>
<!-- Programmed in JSP by Anthony Ehrhardt -->
<!-- cguru.ma.cx released under the GPL (GNU Public license -->
<head><title>Add News</title></head>
<basefont face="Arial">
<body>
<center>
<h2>Add News</h2> <table border=0 cellspacing=5 cellpadding=5>
<form action="addnews2.jsp" method="POST"> <tr>
<td><b>Email Address</b></td>
<td>
<select name="author">
<!-- generate list of available usernames from database -->
<%@ page language="java" import="java.sql.*" %>
<%@page import="java.util.*"%>
<% // database parameters
String host="localhost";
String user="root";
String pass="root";
String db="portal";
String connString; // load driver
Class.forName("org.gjt.mm.mysql.Driver"); // create connection string
connString = "jdbc:mysql://" + host + "/" + db + "?user=" + user + "&password=" + pass; // pass database parameters to JDBC driver
Connection Conn = DriverManager.getConnection(connString); // query statement
java.sql.Statement SQLStatement = Conn.createStatement(); // generate query
String Query = "SELECT DISTINCT author FROM user"; // get result
ResultSet SQLResult = SQLStatement.executeQuery(Query); // get and display each record
while(SQLResult.next())
{
String author = SQLResult.getString("author"); out.println("<option>" + author);
} // close connections
SQLResult.close();
SQLStatement.close();
Conn.close(); %> </select>
</td>
</tr> <tr>
<td>Headline</td>
<td><input type="Text" name="headline" size="50"></td>
</tr>

<input type='hidden' name='date' value='<%=
                new java.util.Date() %>'>
 <tr>
<td>Body</td>
<td><textarea name="body" rows='24' cols='50'></textarea></td>
</tr> 
 <tr>
<td colspan=2><input type="submit" name="submit" value="Add"></td>
</tr> </form>
</table> </center>


</body>
</html>

