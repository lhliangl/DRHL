package forum;

import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import java.util.*;
import java.sql.*;
import java.sql.Connection;
import java.sql.Statement;
import java.sql.ResultSet;


public class AddForum extends HttpServlet {

        DBConnectie db = new DBConnectie(Variable.getDb(),Variable.getDbLogin(),Variable.getDbPassword());

        public void doPost (HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException{
        	PrintWriter out = response.getWriter();
        	    try{    
                	HttpSession session = request.getSession();
                	String sessionType = (String) session.getAttribute("type");
                	if("Admin".equals(sessionType)){
                	
                    int lastforum_id = Integer.parseInt(request.getParameter("lastforum_id"));
					String forum_id = Integer.toString(lastforum_id + 1);
					
					String title = request.getParameter("title");
					if(title.equals("")){
						title = "No title";
					}else{
						title = Filter.filterAll(title);
					}
					
					String forum_info = request.getParameter("forum_info");
					forum_info = Filter.filterAll(forum_info);
                                                            
                   	db.connect();

					
                    db.query(
                    	"INSERT INTO forum_forums(forum_id,title,forum_info) "+
                    	"VALUES(\"" + forum_id +
                    	"\",\"" + title + 
                    	"\",\"" + forum_info + "\")");
					 					 
                    db.close();
              		response.sendRedirect(Variable.getForumPath() + "index.jsp");
              		
                }
                }catch(Exception e){}
                
             
        }
        public void doGet (HttpServletRequest request, HttpServletResponse response)//{
        throws ServletException, IOException{ 
                doPost(request, response);
        }

}