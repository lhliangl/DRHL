<%@page contentType="text/html"%>
<%@ include file="auth.jsp" %>
<%
if (drhlLoggedIn == null || !drhlLoggedIn.equals("true")) {
    response.sendRedirect("index.jsp");
    return;
}
%>
<html>
<!-- Programmed in JSP by Anthony Ehrhardt -->
<!-- cguru.ma.cx released under the GPL (GNU Public license -->
<head><title>Edit News</title>
<BASEFONT face='Arial'>
</head>
<body>
<center> 
<h1>This doesnt work yet! </h1>
<%@ page language="java" import="java.sql.*" %> <%
// add_res.jsp // form data
//String user = request.getParameter("user");
String headline = request.getParameter("headline");
String date = request.getParameter("date");
String body = request.getParameter("body");
String about = request.getParameter("about");
String category = request.getParameter("category");
String author = request.getParameter("author"); // database parameters
String host = "localhost";
String user = "root";
String pass = "root";
String db = "portal";
String connString;
Class.forName("com.mysql.jdbc.Driver");
connString = "jdbc:mysql://" + host + "/" + db + "?user=" + user + "&password=" + pass;
Connection Conn = DriverManager.getConnection(connString);
java.sql.Statement SQLStatement = Conn.createStatement();
String Query = "UPDATE news set body = '" + body + "'";
int SQLStatus = SQLStatement.executeUpdate(Query); if(SQLStatus != 0)
{
out.println("Entry succesfully added.");
out.println("<br><br><a href='addnews.jsp'>Add Another blog</a> | <a href='index.jsp'>Home</a>");
}
else
{
out.println("Error! Please try again.");
} // close connection
SQLStatement.close();
Conn.close(); %> </center>


</body>
</html>

