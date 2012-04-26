import MeeplibMySQL as meeplib
import traceback
import cgi
import meepcookie
import os
import urlparse
from time import sleep

from jinja2 import Environment, FileSystemLoader

def initialize():
    #meeplib.load_data()
	meeplib.initialize()

    # done.

env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
    template = env.get_template(filename)
    x = template.render(**variables)
    return str(x)
    
def check_cookie(cookie):
    session = meepcookie.get_session(cookie)  
    #print session
    return meeplib.get_user_from_session(session)
    
def clear_session(cookie):
    session = meepcookie.get_session(cookie)      
    meeplib.delete_session(session)
    return meepcookie.clear_session(cookie)

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
                
        start_response("200 OK", [('Content-type', 'text/html')])
        
        return [ render_page('index.html', username=username) ]
        
    def login(self, environ, start_response): 
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        
        return [ render_page('login.html', invalid='false', username=None) ]

    def do_login(self, environ, start_response):
        #print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        
        try:
            username = form['username'].value
            password = form['password'].value
            password = password.replace('+', '%20')
            password = urlparse.unquote(password)
        except:
            password = None
            
        
        # retrieve user
        user = meeplib.User(username, password)
        
        k = 'Location'
        v = ''
        returnMsg = ""
        
        loginSuccess = user.validlogin
        
        headers = [('Content-type', 'text/html')]
        
        """if user is not None and password is not None:
            if password == user.password:
            # set content-type


            
                # send back a redirect to '/'
                
                loginSuccess = True
                


                #print headers"""
            
            
        if not loginSuccess:
            headers = [('Content-type', 'text/html')]
            start_response("200 OK", headers)
            
            return [ render_page('login.html', invalid='true') ]
        else:
            session = meeplib.create_session(username)
            
            cookie_name, cookie_val = meepcookie.make_set_cookie_header('session',session)
            
            v = '/'
            
            headers.append((cookie_name, cookie_val))
            
            headers.append((k, v))
            
            start_response('302 Found', headers)
			
            return ["Valid password"]


    def logout(self, environ, start_response):
        cookie = environ.get('HTTP_COOKIE', '')

        cookie_name, cookie_val = clear_session(cookie)
        
        headers = [('Content-type', 'text/html')]
        headers.append((cookie_name, cookie_val))

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return [ "Log out" ] 
        
    def add_user(self, environ, start_response):
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        
        headers = [('Content-type', 'text/html')]
        if username == 'admin':
            start_response("200 OK", headers)
       
            return [ render_page('add_user.html', username=username) ]
        else:
            k = 'Location'
            v = '/login'
            headers.append((k, v))
            start_response('302 Found', headers)
            
            return ["Not admin"]
                
    def add_user_action(self, environ, start_response):
        #print environ['wsgi.input']
        curruser = check_cookie(environ.get('HTTP_COOKIE', ''))
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ,keep_blank_values=True)
        
        if curruser == 'admin':
            try:
                username = form['username'].value
                password = urlparse.unquote(form['password'].value)
                user = meeplib.User.newuser(username, password)
            except: 
                pass
            
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/'))
            start_response('302 Found', headers)
        
            return ["user added"]
        else:
            redre
        
    def delete_user(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        
        try:
            username = form['username'].value
        except:
            pass
            
        meeplib.User.deleteuser(username)
            
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/list_users'))
        start_response('302 Found', headers)
        
        return ["user added"]  
        
    def list_users(self, environ, start_response):        
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        
        if (username == "admin"):
            users = meeplib.get_all_users()
            headers = [('Content-type', 'text/html')]
            start_response("200 OK", headers)
            return [ render_page('list_users.html', users=users, username=username) ]
        elif (username != ""):
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/'))
            start_response("302 Found", headers)
            return ["Not admin"]
        else:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            return ["Not logged in"]
            
    def list_topics(self, environ, start_response):
        topics = meeplib.get_all_topics()
        
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
        
        return [ render_page('list_topics.html', topics=topics, username=username) ]
        
    def view_topic(self, environ, start_response):
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        qString = cgi.parse_qs(environ['QUERY_STRING'])
        tId = qString.get('id', [''])[0]
        #print tId
        topic = meeplib.Topic(int(tId))
        
        #for message in topic.messages:
            #print message
            
        headers = [('Content-type', 'text/html')]
            
        if topic.topic_id == -1:
            start_response("404 not found", headers)
            return [ render_page('404.html') ]
            
        start_response("200 OK", headers)
        
        return [ render_page('view_topic.html', messages=topic.messages, topic=topic, username=username) ]
    
    """def list_messages(self, environ, start_response):
    
        messages = meeplib.get_all_messages()
            
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return [ render_page('list_messages.html', messages=messages) ]"""
        
    def add_topic(self, environ, start_response):
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        
        if username != "":
        
            headers = [('Content-type', 'text/html')]
            
            start_response("200 OK", headers)

            return [ render_page('add_topic.html', username=username) ]
        else:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            return ["session expired"]
        
    def add_topic_action(self, environ, start_response):
        #print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        title = title.replace('+', '%20')
        title = urlparse.unquote(title)
        msgtitle = form['msgtitle'].value
        msgtitle = msgtitle.replace('+', '%20')
        msgtitle = urlparse.unquote(msgtitle)
        message = form['message'].value
        message = message.replace('+', '%20')
        message = urlparse.unquote(message)
        
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        
        if username == "":
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            
            return ["session expired"]
            
        #user = meeplib.User(username)
        
        new_topic = meeplib.Topic.newtopic(title, username, msgtitle, message)
        #new_topic = meeplib.Topic(title, new_message, username)

        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list_topics'))
        start_response("302 Found", headers)
        return ["topic added"]
        
        
    """def add_message(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)

        return [ render_page('add_message.html') ]

    def add_message_action(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        
        cookie = environ.get('HTTP_COOKIE', '')

        username = meepcookie.load_username(cookie)
        user = meeplib.get_user(username)
        
        if user is not None:
            new_message = meeplib.Message(title, message, user)
    
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/m/list'))
            start_response("302 Found", headers)
            return ["message added"]
        else:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            print "Session expired"
            return ["session expired"]
        
    def delete_message(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        
        id = int(form['id'].value)
        
        message = meeplib.get_message(id)
        
        meeplib.delete_message(message)
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list'))
        start_response("302 Found", headers)
        return ["message deleted"]"""
        
    def delete_message_topic(self, environ, start_response):
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        #print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        
        topic_id = int(form['topic_id'].value)
        msg_id = int(form['id'].value)
        
        #topic = meeplib.Topic(topic_id)
        
        msg = Message(topic_id, msg_id)
        
        if msg.username == username:
        
            meeplib.Message.delete_message(topic_id, msg_id)
            
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/m/topics/view?id=%d' % (topic_id,)))
            start_response("302 Found", headers)
            return ["message deleted"]
        else:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            return ["session expired"]
        
    """def reply(self, environ, start_response):
        print environ['wsgi.input']

        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        
        id = int(form['id'].value)
        
        m = meeplib.get_message(id)
        
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)

        return [ render_page('reply.html', message=m, topic_id=-1) ]"""
        
    def reply_topic(self, environ, start_response):
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        #print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        
        id = int(form['id'].value)
        topic_id = int(form['topic_id'].value)
        
        m = meeplib.Message.get_message(topic_id, id)
        
        if username != "":
        
            headers = [('Content-type', 'text/html')]
            start_response("200 OK", headers)
            return [ render_page('reply.html', message=m, topic_id=topic_id, username=username) ]
        else:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            return ["session expired"]
		
    def add_message_topic_action(self, environ, start_response):
        #print "Welp."
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        topicId = form['topicid'].value
        topic = meeplib.Topic(int(topicId))
        
        title = form['title'].value
        title = title.replace('+', '%20')
        title = urlparse.unquote(title)
        message = form['message'].value
        message = message.replace('+', '%20')
        message = urlparse.unquote(message)
        
        username = check_cookie(environ.get('HTTP_COOKIE', ''))
        #print username
        #user = meeplib.get_user(username)
        #print user
        
        if username != "":
            #print title, message, user
            #new_message = meeplib.Message(title, message, username)
            
            meeplib.Message.newmessage(topic.topic_id, username, title, message)
            #print "Message added to topic" + topicId
            
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/m/topics/view?id=%d' % (topic.topic_id)))
            start_response("302 Found", headers)
            return ["message added to topic"]
        else:
            headers = [('Content-type', 'text/html')]
            headers.append(('Location', '/login'))
            start_response("302 Found", headers)
            return ["session expired"]
        
    def delete_topic_action(self, environ, start_response):
        #print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        topicId = form['tid'].value
        topic = meeplib.Topic(int(topicId))
        topic.delete_topic()
        
        headers = [('Content-type', 'text/html')]
        headers.append(('Location', '/m/list_topics'))
        start_response("302 Found", headers)
        return ["topic deleted"]

    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/add_user': self.add_user,
                      '/add_user_action': self.add_user_action,
                      '/delete_user': self.delete_user,
                      '/list_users': self.list_users,
                      '/login': self.login,
                      '/do_login': self.do_login,
                      '/logout': self.logout,
                      #'/m/list': self.list_messages,
                      '/m/list_topics': self.list_topics,
                      '/m/topics/view': self.view_topic,
                      #'/m/add': self.add_message,
                      #'/m/add_action': self.add_message_action,
                      #'/m/delete_message': self.delete_message,
                      '/m/delete_message_topic': self.delete_message_topic,
                      #'/m/reply': self.reply,
                      '/m/reply_topic': self.reply_topic,
                      '/m/add_message_topic_action': self.add_message_topic_action,
                      '/m/add_topic': self.add_topic,
                      '/m/add_topic_action': self.add_topic_action,
                      '/m/delete_topic_action': self.delete_topic_action
                    }

        # see if the URL is in 'call_dict'; if it is, call that function.
        url = environ['PATH_INFO']
        fn = call_dict.get(url)
        
        #print "************ URL: ", url, "\n\n\n"

        if fn is None:
            serve = MimeServe(url)
            return serve.Go(environ, start_response)
            
        try:
            return fn(environ, start_response)
        except:
            tb = traceback.format_exc()
            #print tb
            x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

            status = '500 Internal Server Error'
            start_response(status, [('Content-type', 'text/html')])
            return [x]

class MimeServe(object):
    def __init__(self, filename):
        # Failsafe to plain text in case it matches nothing
        c_type = "text/plain;"
        if filename.endswith(".jpg"):
            c_type = "image/jpeg;"
        elif filename.endswith(".gif"):
            c_type = "image/gif;"
        elif filename.endswith(".html") or filename.endswith(".htm"):
            c_type = "text/html;"
        elif filename.endswith(".ico"):
            c_type = "image/x-icon;"
        elif filename.endswith(".css"):
            c_type = "text/css;"
        
        self.content_type = c_type
        self.filename = filename

    def Go(self, environ, start_response):
        try:
            #print "Filename:", self.filename
            #print os.getcwd()
            fp = open(os.getcwd() + self.filename, mode="r")
        except IOError:
            start_response("404 not found", [('Content-type', 'text/html'),])
            return [ render_page('404.html') ]

        data = fp.read()
        headers = [('Content-type', self.content_type),]
        headers.append(('Content-Disposition', 'attachment; filename='+self.filename))
        start_response("200 OK", headers)
        return [data]
