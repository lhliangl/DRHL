<%@ page contentType='text/html; charset=UTF-8' %>
<%@ page import='java.io.*' %>
<%@ page import='javax.servlet.*' %>
<%@ page import='javax.servlet.http.*' %>
<%@ page import='java.sql.*' %>
<%@ page import='java.sql.Connection' %>
<%@ page import='java.sql.Statement' %>
<%@ page import='java.sql.ResultSet' %>
<%@ page import='forum.*' %>

<% String sessionUsername = (String)session.getAttribute("username"); %>
<% String sessionPassword = (String)session.getAttribute("password"); %>
<% String sessionType = (String)session.getAttribute("type"); %>	
		
<% String forum_id = request.getParameter("forum_id"); %>
<% String reqThread_id = request.getParameter("thread_id"); %>
<% String reqReply_id = request.getParameter("reply_id"); %>
<% String start = request.getParameter("start"); %>
<%	
try{

DBConnectie db = new DBConnectie(Variable.getDb(),Variable.getDbLogin(),Variable.getDbPassword());
			
db.connect();
ResultSet rs = db.selectQuery(
	"SELECT * FROM forum_message " +
   	"WHERE forum_id=\"" + forum_id + "\" AND thread_id =\"" + reqThread_id + "\" AND reply_id=\"" + reqReply_id + "\"");
						
	String message = null;
	String messageUser = null;
	while(rs.next()){
		message = rs.getString("message");	
		messageUser = rs.getString("user");
		
		if(message.indexOf("<!-- begin --!>") != -1 ){
			int begin = message.indexOf("<!-- begin --!>");		
			message = message.substring(0,begin);
		}
	}
	db.close();
	
	if(sessionUsername != null && !"Admin".equals(sessionType) && !sessionUsername.equals(messageUser)) {
		response.sendRedirect(Variable.getForumPath() + "index.jsp");
		return;
	}
	
	message = FilterBack.filterAll(message);
	
	
%>
<jsp:include page="./include/header.jsp" flush="true">
	<jsp:param name="title" value="Edit Message" /> 
</jsp:include>	
<jsp:include page="./include/body.jsp" flush="true" />
<% if( sessionUsername != null){%>
	<table width="100%" height="20" border="0" cellpadding="1" cellspacing="1">
		<tr> 
			<td height="20" valign="top" class="pathBar">
				<a href="index.jsp" class="pathBarLink"><%= Variable.getForumName() %></a><span class="pathBarSeperator"> > </span>
				<a href="./index.jsp?page=thread&forum_id=<%= forum_id %>" class="pathBarLink"><%= Utilities.getforumTile(forum_id) %></a><span class="pathBarSeperator"> > </span>
				<a href="./index.jsp?page=thread&forum_id=<%= forum_id %>&thread_id=<%=reqThread_id%>&start=<%= start %>" class="pathBarLink"><%= Utilities.getThreadTile(forum_id,reqThread_id) %></a><span class="pathBarSeperator"> > </span><a href="./index.jsp?page=editmessage&forum_id=<%= forum_id %>&thread_id=<%=reqThread_id%>&reply_id=<%= reqReply_id %>&start=<%= start %>" class="pathBarLink">Edit Message</a>
			</td>
		</tr>
	</table>

	<jsp:include page="./include/table_start.jsp" flush="true" />      
	<jsp:include page="./include/table_title.jsp" flush="true">
		<jsp:param name="title" value="Edit Message" /> 
		<jsp:param name="colspan" value="3" /> 
		<jsp:param name="align" value="left" /> 
	</jsp:include>	    
	<jsp:include page="./include/table_start_body.jsp" flush="true" />
	<jsp:include page="./include/table_body.jsp" flush="true">
		<jsp:param name="width" value="0" /> 
	</jsp:include>			
	<b>Message:</b>
	<form action="../servlet/forum.ChangeMessage" method="POST" name="formmessage">
	<input type="hidden" name="start" value="<%= start %>">
	<input type="hidden" name="forum_id" value="<%= forum_id %>">
	<input type="hidden" name="thread_id" value="<%= reqThread_id %>">
	<input type="hidden" name="reply_id" value="<%= reqReply_id %>">
	<textarea name="message" cols="45" rows="10" maxlength="3000"><%= message %></textarea>
	<br>
	<input type="submit" value="change">
	</form>
	<jsp:include page="./include/table_body.jsp" flush="true">
		<jsp:param name="width" value="200" /> 
	</jsp:include>
	<jsp:include page="./include/textStyle.jsp" flush="true" />

	<jsp:include page="./include/table_body.jsp" flush="true">
		<jsp:param name="width" value="200" /> 
	</jsp:include>
	<jsp:include page="./include/emoticons.jsp" flush="true" />

	<jsp:include page="./include/table_close_body.jsp" flush="true" />	
	<jsp:include page="./include/table_start_title.jsp" flush="true" />
	<% String back = "<a href=index.jsp?page=message&forum_id=" + forum_id + "&thread_id=" + reqThread_id + "&start=" + start + ">Back</a>"; %>
	<jsp:include page="./include/table_title.jsp" flush="true">
		<jsp:param name="title" value="<%= back %>" /> 
		<jsp:param name="colspan" value="3" /> 
		<jsp:param name="align" value="left" /> 
	</jsp:include>
	<jsp:include page="./include/table_close.jsp" flush="true" />
<% }else { %>
	<br>
	<jsp:include page="./include/table_start.jsp" flush="true" /> 
	<jsp:include page="./include/table_title.jsp" flush="true">
		<jsp:param name="title" value="Error" /> 
		<jsp:param name="colspan" value="1" /> 
		<jsp:param name="align" value="left" /> 
	</jsp:include>						
	<jsp:include page="./include/table_start_body.jsp" flush="true" />
	<jsp:include page="./include/table_body.jsp" flush="true">
		<jsp:param name="width" value="200" /> 
	</jsp:include>
	You have to login first !
	<br>
	<br>
	<a href="./register.jsp">Register</a>
	<jsp:include page="./include/table_close_body.jsp" flush="true" />				 
	<jsp:include page="./include/table_close.jsp" flush="true" />
<% } %>   
<jsp:include page="./include/footer.jsp" flush="true" />
<% }catch(Exception e){out.println(e);} %>