package forum;

import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import java.sql.*;
import java.sql.Connection;
import java.sql.Statement;
import java.sql.ResultSet;

public class AddReply extends HttpServlet {

        DBConnectie db = new DBConnectie(Variable.getDb(),Variable.getDbLogin(),Variable.getDbPassword());

        public void doPost (HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException{
        	PrintWriter out = response.getWriter();
        	    try{    
     				String start = request.getParameter("start");
                    String forum_id = request.getParameter("forum_id");
                    int lastReply_id = Integer.parseInt(request.getParameter("lastReply_id"));
					String reply_id = Integer.toString(lastReply_id + 1);
			
					String thread_id = request.getParameter("thread_id");
					String message = request.getParameter("message");
					message = Filter.filterAll(message);
					
					
					String user = request.getParameter("user");
                    
                    HttpSession session = request.getSession();
                    String sessionUsername = (String) session.getAttribute("username");
                    if(sessionUsername != null){
                    
                    db.connect();


                    db.query(
                    	"INSERT INTO forum_message(forum_id,thread_id,reply_id,message,user,date_time) "+
                    	"VALUES(\"" + forum_id + 
                    	"\",\"" + thread_id +
                    	"\",\"" + reply_id +
                    	"\",\"" + message + 
                    	"\",\"" + user +
                    	"\",SYSDATE())");
                    					 
                    db.close();
           		
              		response.sendRedirect(Variable.getForumPath() + "index.jsp?page=message&forum_id="+ forum_id +"&thread_id=" + thread_id +"&start=" + start);
              		}
                }catch(Exception e){}
                
             
        }
        public void doGet (HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException{ 
                doPost(request, response);
        }

}