<%@page contentType="text/html"%>
<html>
<!-- Programmed in JSP by Anthony Ehrhardt -->
<!-- cguru.ma.cx released under the GPL (GNU Public license -->
<head><title>JSP Page</title>
<BASEFONT face='Arial'>
</head>
<body>
<center> 
<%@ page language="java" import="java.sql.*" %> <%
String drhlLoggedIn = (String) session.getAttribute("drhlLoggedIn");
if (drhlLoggedIn == null || !drhlLoggedIn.equals("true")) {
    response.sendRedirect("index.jsp");
    return;
}
// add_res.jsp // form data
//String user = request.getParameter("user");
String headline = request.getParameter("headline");
String date = request.getParameter("date");
String body = request.getParameter("body");
String about = request.getParameter("about");
String category = request.getParameter("category");
String author = request.getParameter("author"); // database parameters
String host="localhost";
String username="root";
String pass="root";
String db="portal";
String conn; Class.forName("org.gjt.mm.mysql.Driver"); // create connection string
conn = "jdbc:mysql://" + host + "/" + db + "?user=" + username + "&password=" + pass; // pass database parameters to JDBC driver
Connection Conn = DriverManager.getConnection(conn); // query statement
java.sql.Statement SQLStatement = Conn.createStatement(); // generate query
String Query = "INSERT INTO news (headline,body,date,author) VALUES ('" + headline + "', '" +
body + "','" + date + "', '" + author + "')"; // get result code
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

