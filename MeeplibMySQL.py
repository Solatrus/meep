import MySQLdb
import datetime
import random

db = None
c = None

def connect():
    global db
    global c
    db = MySQLdb.connect(host="localhost",user="meep_db",passwd="meep_db_passw0rd!", db='cse491')
    c = db.cursor()
    return c
    
def disconnect():
    global db
    db.close()

encryptionkey = 'VGhpcyBpcyBhbiBlbmNyeXB0aW9uIGtleS4='

def get_user_from_session(session):
    c = connect()
    #print "select username, session_timestamp from user_sessions where session_key = '%s'" % (session,)
    c.execute('SELECT username, session_timestamp FROM user_sessions WHERE session_key = %s', (session,))
    
    row = c.fetchone()
    
    disconnect()
    
    timecheck = datetime.datetime.now() + datetime.timedelta(weeks = 2)
    
    # Session lasts two weeks
    if row:
        if (row[1] < timecheck):
            return row[0]
        else:
            delete_session(session)
            return ""
    else:
        return ""
    
def delete_session(session):
    c = connect()
    c.execute('DELETE FROM user_sessions WHERE session_key = %s', (session,))
    disconnect()
    
def create_session(username):
    random_string = ''
    i = 0;
    for i in range(128):
        random_string += random.choice('abcdefghijklmnopqrstuvwxyz1234567890!@#:;\\\%|/$^&*(),.[]{}-=_+?')
    c = connect()
    timenow = datetime.datetime.now()
    #print "setting session"
    #print "INSERT INTO user_sessions (session_key, username, session_timestamp) VALUES (%s, %s, %s)" % (random_string, username, timenow,)
    c.execute("INSERT INTO user_sessions (session_key, username, session_timestamp) VALUES (%s, %s, %s)", (random_string, username, timenow,))
    disconnect()
    #   print random_string
    return random_string
    
    
class Message(object):
    def __init__(self, msg_id, topic_id, username, header, msg_text):
        self.msg_id = msg_id
        self.topic_id = topic_id
        self.username = username
        self.header = header
        self.msg_text = msg_text
        
    @classmethod
    def get_message(self, topic_id, msg_id):
        c = connect()
        c.execute('SELECT * FROM messages WHERE msg_id = %s AND topic_id = %s', (msg_id, topic_id,))
        
        row = c.fetchone()
        
        self.msg_id = msg_id
        self.topic_id = topic_id
        self.username = row[2]
        self.header = row[3]
        self.msg_text = row[4]
        
        disconnect()
        
        return self
        
    @classmethod
    def newmessage(self, topic_id, username, msg_header, msg_text):
        #print """INSERT INTO messages (topic_id, username, header, msg_text)
        #             VALUES ( %s, %s, %s, %s )""", (topic_id, username, msg_header, msg_text,)
        c = connect()
        c.execute("""INSERT INTO messages (topic_id, username, header, msg_text)
                     VALUES ( %s, %s, %s, %s )""", (topic_id, username, msg_header, msg_text,))
        disconnect()
    
    @classmethod    
    def delete_message(self, topic_id, msg_id):
        c = connect()
        c.execute('DELETE FROM messages WHERE topic_id = %s AND msg_id = %s', (topic_id, msg_id,))
        disconnect()
        
class Topic(object):
    def __init__(self, topic_id):
        c = connect()
        c.execute('SELECT * FROM messages WHERE (topic_id = %s)', (topic_id,))
        
        self.messages = []
        
        for row in c:
            msg = Message(row[0], row[1], row[2], row[3], row[4])
            self.messages.append(msg)
            
        c.execute('SELECT * FROM topics WHERE (topic_id = %s)', (topic_id,))
        
        row = c.fetchone()
        
        try:
            self.topic_name = row[1]
            self.topic_id = topic_id
        except:
            self.topic_name = "404"
            self.topic_id = -1
            
        disconnect()
        
    @classmethod
    def newtopic(self, topic_name, username, msg_header, msg_text):
        c = connect()
        c.execute('INSERT INTO topics (topic_name) VALUES ( %s )', (topic_name,))
        c.execute('SELECT * FROM topics ORDER BY topic_id DESC LIMIT 1')
        
        self.messages = []
        
        row = c.fetchone()
        
        disconnect()
        
        self.messages.append(Message.newmessage(row[0],  username, msg_header, msg_text))
        self.topic_id = int(row[0])
        self.topic_name = topic_name
        
        return self
        
    def delete_topic(self):
        for msg in self.messages:
            Message.delete_message(self.topic_id, msg.msg_id)
            
        c = connect()
        c.execute('DELETE FROM topics WHERE topic_id = %s', (self.topic_id,))
        disconnect()
            
def get_all_topics():
    topics = []
    c = connect()
    
    c.execute('SELECT topic_id FROM topics')
    
    disconnect()
    
    for row in c:
        topic = Topic(int(row[0]))
        topics.append(topic)
        
    return topics
        
class User(object):
    def __init__(self, username, password):
        c = connect()
        c.execute('SELECT AES_DECRYPT(password, %s) AS upass FROM users where (username = %s)', (encryptionkey, username,))
        
        try:
            row = c.fetchone()
        except:
            self.validlogin = False
         
        isvalid = password == row[0]
        
        self.validlogin = isvalid
        
        disconnect()
        
    @classmethod
    def newuser(self, username, password):
        c = connect()
        c.execute('INSERT INTO users (username, password) VALUES ( %s, AES_ENCRYPT(%s, %s) )', (username, password, encryptionkey,))
        disconnect()
        
    @classmethod
    def deleteuser(self, username):
        if (username != 'admin'):
            c = connect()
            c.execute('DELETE FROM users WHERE username = %s', (username,))    
            disconnect()
        
def get_all_users():
    users = []
    c = connect()
    c.execute('SELECT username FROM users')
    
    for row in c:
        users.append(row[0])
        
    disconnect()
        
    return users
    
def initialize():
    c = connect()
    try:
        c.execute('DROP TABLE messages')
        c.execute('DROP TABLE topics')
        c.execute('DROP TABLE users')
        c.execute('DROP TABLE user_sessions')
    except:
        print "Unable to drop tables, must be a new database."
        
    c.execute('CREATE TABLE messages (msg_id INTEGER PRIMARY KEY AUTO_INCREMENT, topic_id INTEGER, username VARCHAR(32), header TINYTEXT, msg_text TEXT)')
    c.execute('CREATE TABLE topics (topic_id INTEGER PRIMARY KEY AUTO_INCREMENT, topic_name TEXT)')
    c.execute('CREATE TABLE users (username VARCHAR(32), password VARCHAR(50))')
    c.execute('CREATE TABLE user_sessions ( session_key varchar(129) PRIMARY KEY NOT NULL, username VARCHAR(32) NOT NULL, session_timestamp DATETIME NOT NULL)')
    disconnect();
    Topic.newtopic("My First Topic", "admin", "my title", "This is my message!")
    User.newuser('admin','4dm1n')