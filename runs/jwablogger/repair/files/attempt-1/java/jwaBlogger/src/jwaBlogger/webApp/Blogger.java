/**
 * Copyright (C) 2006 - present by David Bulmore, Software Sensation Inc.  
 * All Rights Reserved.
 *
 * This file is part of jwaBlogger.
 *
 * jwaBlogger is free software; you can redistribute it and/or modify it under 
 * the terms of the accompanying license.
 *
 * jwaBlogger is distributed in the hope that it will be useful, but WITHOUT 
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. See the accompanying license 
 * for more details.
 *
 * You should have received a copy of the license along with jwaBlogger; if not, 
 * go to http://www.jwebapp.org or http://www.softwaresensation.com 
 * and download the latest version.
 */

package jwaBlogger.webApp;

import jwaBlogger.WebAppInterface;
import jwaBlogger.BlogEntry;
import jwaBlogger.BlogEntryComment;
import jwaBlogger.BlogManager;
import jwaBlogger.User;
import com.sun.syndication.io.FeedException;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.servlet.http.Cookie;
import jpersist.JPersistException;
import jwebapp.JWebAppException;
import jwebapp.RequestHandler;
import jwebapp.ServerInterface;
import jwebtk.mail.EmailSenderException;
import jwebtk.password.Password;
import jwebtk.password.PasswordException;
import jwebtk.validator.Validator;

/**
 * jWebApp specific interfacing
 */
public class Blogger extends RequestHandler
  {
    private static final Logger logger = Logger.getLogger(Blogger.class.getName());
    
    public String processRequest(ServerInterface serverInterface) { return "/blogger/entries"; }
    
    public String processTemplate(ServerInterface serverInterface) throws JPersistException
      {
        if (serverInterface.getRemoteUser() == null && serverInterface.getCookie("autoLogin") != null)
          autoLogin(serverInterface);
        
        return "/WEB-INF/jwaBlogger.jsp";
      }
    
    public String processEntries(ServerInterface serverInterface) 
      {
        BlogManager blogManager = (BlogManager)serverInterface.getServletContext().getAttribute("blogManager");

        WebAppInterface.entryList(blogManager, serverInterface.getServletRequest(), serverInterface.getParameter("c"), 
                                  Integer.valueOf(serverInterface.getParameter("pageSize", blogManager.getProperties().getProperty("pageSize", "20"))),
                                  Integer.valueOf(serverInterface.getParameter("page","1")), (List<BlogEntry>)serverInterface.getSessionAttribute("searchEntries"));
      
        if (serverInterface.getParameter("ajax") != null)
          return "/WEB-INF/ajaxEntryList.jsp"; 

        return "/blogger/template";
      }
    
    public String validateSaveEntry(ServerInterface serverInterface) throws JWebAppException
      {
        StringBuilder str = WebAppInterface.validateEntry((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"),
                                                          serverInterface.getServletRequest(), serverInterface.fillObjectFromRequest(new BlogEntry()), 
                                                          serverInterface.getRemoteUser(), serverInterface.getParameter("captchaId"), 
                                                          serverInterface.getParameter("captchaAnswer"));

        if (str.length() > 0)
          {
            serverInterface.setErrorMessage(str.toString());

            return "/blogger/template?c=entry";
          }
        
        return SUCCESS;
      }
    
    public String processSaveEntry(ServerInterface serverInterface) throws Exception
      {
        String remoteUser = serverInterface.getRemoteUser();

        if (remoteUser != null)
          {
            boolean switchToTextarea = serverInterface.getParameter("textarea") != null,
                    switchToWysiwyg = serverInterface.getParameter("wysiwyg") != null;
            
            WebAppInterface.saveEntry((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), 
                                      serverInterface.getServletRequest(), remoteUser, serverInterface.getParameter("blogEntryId", true), 
                                      switchToWysiwyg, switchToTextarea, serverInterface.isUserInRole("trusted"));
            
            if (switchToWysiwyg || switchToTextarea)
              return "/blogger/template?c=entry";
          }

        return "/blogger/template";
      }
    
    public String processViewEntry(ServerInterface serverInterface) throws JWebAppException, JPersistException
      {
        if (serverInterface.getRemoteUser() == null) return "/blogger/entries";

        WebAppInterface.viewEntry((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"),
                                  serverInterface.getServletRequest(), serverInterface.getPathArguments(), 
                                  getControl(serverInterface), serverInterface.isUserInRole("administrator"));

        return "/blogger/template";
      }
    
    public String processVoteEntry(ServerInterface serverInterface) throws JWebAppException, JPersistException, IOException
      {
        WebAppInterface.voteEntry((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"),
                                  serverInterface.getServletResponse(), serverInterface.getParameter("entryId"),
                                  getControl(serverInterface), serverInterface.isUserInRole("administrator"));
      
        return NO_FORWARDING;
      }
    
    public String processSpamEntry(ServerInterface serverInterface) throws JWebAppException, JPersistException, IOException
      {
        WebAppInterface.spamEntry((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), 
                                  serverInterface.getParameter("entryId"), getControl(serverInterface), 
                                  serverInterface.isUserInRole("administrator"));

        return NO_FORWARDING;
      }
    
    public String processVoteComment(ServerInterface serverInterface) throws JWebAppException, JPersistException, IOException
      {
        WebAppInterface.voteComment((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), 
                                     serverInterface.getServletResponse(), serverInterface.getParameter("entryId"), 
                                     serverInterface.getParameter("commentId"), getControl(serverInterface),
                                     serverInterface.isUserInRole("administrator"));
      
        return NO_FORWARDING;
      }
    
    public String processSpamComment(ServerInterface serverInterface) throws JWebAppException, JPersistException, IOException
      {
        WebAppInterface.spamComment((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), 
                                    serverInterface.getParameter("entryId"), serverInterface.getParameter("commentId"), 
                                    serverInterface.getRemoteUser(), getControl(serverInterface), serverInterface.isUserInRole("administrator"));

        return NO_FORWARDING;
      }
    
    public String validateSaveComment(ServerInterface serverInterface) throws JWebAppException
      {
        StringBuilder str = WebAppInterface.validateComment((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), 
                                                            serverInterface.getServletRequest(), serverInterface.fillObjectFromRequest(new BlogEntryComment()), 
                                                            serverInterface.getRemoteUser(), serverInterface.getParameter("captchaId"), serverInterface.getParameter("captchaAnswer"));
        
        if (str.length() > 0)
          {
            serverInterface.setErrorMessage(str.toString());
            
            return "/blogger/viewEntry/" + serverInterface.getParameter("internalName") + ".html";
          }
        
        return SUCCESS;
      }
    
    public String processSaveComment(ServerInterface serverInterface) throws JPersistException, JWebAppException, IOException
      {
        WebAppInterface.saveComment((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), 
                                    serverInterface.fillObjectFromRequest(new BlogEntryComment()), serverInterface.getRemoteUser());

        serverInterface.setAttribute("blogEntryComment", new BlogEntryComment());
        
        return "/blogger/viewEntry/" + serverInterface.getParameter("internalName") + ".html";
      }
    
    public String processSearch(ServerInterface serverInterface) throws JPersistException, IOException
      {
        int numberPages = WebAppInterface.search((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), serverInterface.getServletRequest());

        if (numberPages > 1)
          return "/blogger/entries?c=search";
        
        if (numberPages == 0)
          serverInterface.setErrorMessage("Searching for something?");
        
        return "/blogger/template";
      }
    
    public String validateRegister(ServerInterface serverInterface) throws JWebAppException
      {
        StringBuilder str = WebAppInterface.validateRegister(serverInterface.fillObjectFromRequest(new User()), serverInterface.getRemoteUser());
        
        if (str.length() > 0)
          {
            serverInterface.setErrorMessage(str.toString());
            
            return "/blogger/template?c=register";
          }
        
        return SUCCESS;
      }
    
    public String processRegister(ServerInterface serverInterface) throws JWebAppException, JPersistException, PasswordException
      {
        User user = serverInterface.getSessionAttribute("user", new User());
        String email = user.getEmail();

        user.setPassword(null);
        serverInterface.fillObjectFromRequest(user);

        if (email == null || !email.equalsIgnoreCase(user.getEmail()))
          {
            if (Validator.isNotEmptyOrNull(user.getPassword()))
              user.setPassword(Password.getEncryptedPassword(user.getPassword()));

            try
              {
                if (WebAppInterface.register((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), user, 
                                             serverInterface.getAbsoluteUrl(serverInterface.getServletRequest().getContextPath() + "/blogger/verify/")))
                  {
                    serverInterface.setApplicationMessage("New user saved.  Thank you!  You will receive a verification email shortly.");
                  }
              }
            catch(EmailSenderException e)
              {
                logger.log(Level.SEVERE, "Error sending email", e);
                serverInterface.setErrorMessage("Error sending email: " + e.getMessage());
              }
          }
        
        return "/blogger/entries";
      }
    
    public String processVerify(ServerInterface serverInterface) throws JPersistException
      {
        if (WebAppInterface.verify((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), serverInterface.getPathArguments()))
          {
            serverInterface.setApplicationMessage("Email verified.  You may now login and add your own content.  Thank you!");
            serverInterface.invalidateRemoteUser();
          } 
        
        return "/blogger/entries";
      }
    
    public String processFeed(ServerInterface serverInterface) throws IOException, FeedException, JPersistException
      {
        String feedType = WebAppInterface.stripExtension(serverInterface.getPathArguments()[0], ".xml");
        
        WebAppInterface.feed(serverInterface.getServletRequest(), serverInterface.getServletResponse(),
                            (BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), feedType, 
                            serverInterface.getServletRequest().getContextPath() + "/blogger/viewEntry/");

        return NO_FORWARDING;
      }
    
    public String validateLogin(ServerInterface serverInterface) throws JWebAppException
      {
        StringBuilder str = WebAppInterface.validateLogin(serverInterface.fillObjectFromRequest(new User()));
        
        if (str.length() > 0)
          {
            serverInterface.setErrorMessage(str.toString());
            
            return "/blogger/entries";
          }
        
        return SUCCESS;
      }
    
    public String processLogin(ServerInterface serverInterface) throws JWebAppException, JPersistException, PasswordException
      {
        User user = serverInterface.fillObjectFromRequest(new User());
        Set<String> roles = WebAppInterface.login((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), user);

        if (roles != null)
          {
            serverInterface.setSessionAttribute("user", user);
            serverInterface.setRemoteUserInformation(user.getUsername(), null, user.getFirstName(), user.getLastName(), roles);

            return "/blogger/search?searchString='" + user.getUsername() + "'&author=y";
          }
        else serverInterface.setErrorMessage("Username/password is not a valid login combination");
        
        return "/blogger/entries";
      }
    
    void autoLogin(ServerInterface serverInterface) throws JPersistException
      {
        User user = new User(serverInterface.getCookie("autoLogin").getValue());
        Set<String> roles = WebAppInterface.autoLogin((BlogManager)serverInterface.getServletContext().getAttribute("blogManager"), user);
        
        if (roles != null)
          {
            serverInterface.setSessionAttribute("user", user);
            serverInterface.setSessionAttribute("autoLogin", Boolean.TRUE);
            serverInterface.setRemoteUserInformation(user.getUsername(), null, user.getFirstName(), user.getLastName(), roles);
          }
      }
    
    public String processSetAutoLogin(ServerInterface serverInterface) throws IOException
      {
        BlogManager blogManager = (BlogManager)serverInterface.getServletContext().getAttribute("blogManager");
        
        if (serverInterface.getRemoteUser() != null && blogManager.getProperties().getProperty("allowCookieLogin", "false").equals("true"))
          {
            if (serverInterface.getParameter("autoLogin", "false").equals("true"))
                {
                  User user = serverInterface.getSessionAttribute("user");
              
                  serverInterface.setSessionAttribute("autoLogin", Boolean.TRUE);
                  serverInterface.getServletResponse().addCookie(getNewCookie("autoLogin", user.getUsername() + ":" + user.getPassword(), 1000000));
                }
              else
                {
                  serverInterface.removeSessionAttribute("autoLogin");
                  serverInterface.getServletResponse().addCookie(getNewCookie("autoLogin", "false", 0));
                }
        
            serverInterface.getServletResponse().setContentType("text/plain");
            serverInterface.getServletResponse().getWriter().print(serverInterface.getParameter("autoLogin", "false"));
          }
        
        return NO_FORWARDING;
      }
    
    public String processLogout(ServerInterface serverInterface)
      {
        serverInterface.invalidateRemoteUser();
        
        return "/blogger/entries";
      }

    static Cookie getNewCookie(String name, String value, int seconds)
      {
        Cookie cookie = new Cookie(name, value);
      
        cookie.setPath("/");
        cookie.setMaxAge(seconds);
        
        return cookie;
      }
    
    static String getControl(ServerInterface serverInterface)
      {
        String value = serverInterface.getRemoteUser();

        if (value == null)
          {
            Cookie cookie = (Cookie)serverInterface.getCookie("pc");
            
            if (cookie != null)
              value = cookie.getValue();
            else
              {
                value = serverInterface.getServletRequest().getRemoteAddr();

                serverInterface.getServletResponse().addCookie(getNewCookie("pc", value, 1000000));
              }
          }
        
        return value;
      }
  }
