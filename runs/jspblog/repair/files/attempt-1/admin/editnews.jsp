<%@page contentType="text/html"%>
<%@ page language="java" import="java.sql.*" %>
<%@ include file="auth.jsp" %>
<html><head><title>Edit News</title>
</head>
<body>
<center>
<h1 class="blog">Cguru's Blog</h1>
<h2>EDIT doesnt work yet!</h2>
</center>
<%
Class.forName("org.gjt.mm.mysql.Driver");
Connection myConn = 
DriverManager.getConnection("jdbc:mysql://localhost/portal?user=root&password=root");
    java.sql.Statement stmt = myConn.createStatement();
String query="select * from news";
ResultSet myResultSet = stmt.executeQuery(query);
if (myResultSet != null) {
    while (myResultSet.next()) {
      // specify the field name
      String body = myResultSet.getString("body");
      String headline = myResultSet.getString("headline");
      String author = myResultSet.getString("author");
      String date = myResultSet.getString("date");
%>
<form name='edit' action='editnews2.jsp'>
<table border='1' align="center" class="blog">
  <tr> 
    <td><b><input type='text' name='headline' value="
<%= headline %>">
</b></td>
  </tr>
<tr> 
    <td><b><%= date %></b></td>
  </tr>
  <tr> 
    <td><i><%= author %></i></td>
  </tr>
  <tr> 
    <td><input type="textarea" name="body" rows='24' cols='50'><%= body %>
</textarea>
</td>
  </tr>
</table>
<input type='submit'>
</form>
<br />
<%
    }
  }   stmt.close();   myConn.close();
%>
<p> </p>
<p> </p>
<p>

</p>
</body>
</html>

