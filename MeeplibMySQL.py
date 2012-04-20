import MySQLdb

db = MySQLdb.connect(host="localhost",user="meep_db",passwd="meep_db_passw0rd!", db='cse491')
c = db.cursor()

encryptionkey = 'VGhpcyBpcyBhbiBlbmNyeXB0aW9uIGtleS4='
    
class Message(object):
    def __init__(self, msg_id, topic_id, username, header, msg_text):
        self.msg_id = msg_id
        self.topic_id = topic_id
        self.username = username
        self.header = header
        self.msg_text = msg_text
        
    @classmethod
    def get_message(self, topic_id, msg_id):
        c.execute('SELECT * FROM messages WHERE msg_id = %s AND topic_id = %s', (msg_id, topic_id,))
        
        row = c.fetchone()
        
        self.msg_id = msg_id
        self.topic_id = topic_id
        self.username = row[2]
        self.header = row[3]
        self.msg_text = row[4]
        
        return self
        
    @classmethod
    def newmessage(self, topic_id, username, msg_header, msg_text):
        #print """INSERT INTO messages (topic_id, username, header, msg_text)
        #             VALUES ( %s, %s, %s, %s )""", (topic_id, username, msg_header, msg_text,)
        c.execute("""INSERT INTO messages (topic_id, username, header, msg_text)
                     VALUES ( %s, %s, %s, %s )""", (topic_id, username, msg_header, msg_text,))
    
    @classmethod    
    def delete_message(self, topic_id, msg_id):
        c.execute('DELETE FROM messages WHERE topic_id = %s AND msg_id = %s', (topic_id, msg_id,))
        
class Topic(object):
    def __init__(self, topic_id):
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
        
    @classmethod
    def newtopic(self, topic_name, username, msg_header, msg_text):
        c.execute('INSERT INTO topics (topic_name) VALUES ( %s )', (topic_name,))
        c.execute('SELECT * FROM topics ORDER BY topic_id DESC LIMIT 1')
        
        self.messages = []
        
        row = c.fetchone()
        
        self.messages.append(Message.newmessage(row[0],  username, msg_header, msg_text))
        self.topic_id = int(row[0])
        self.topic_name = topic_name
        
        return self
        
    def delete_topic(self):
        for msg in self.messages:
            Message.delete_message(self.topic_id, msg.msg_id)
        c.execute('DELETE FROM topics WHERE topic_id = %s', (self.topic_id,))
            
def get_all_topics():
    topics = []
    
    c.execute('SELECT topic_id FROM topics')
    
    for row in c:
        topic = Topic(int(row[0]))
        topics.append(topic)
        
    return topics
        
class User(object):
    def __init__(self, username, password):
        c.execute('SELECT AES_DECRYPT(password, %s) AS upass FROM users where (username = %s)', (encryptionkey, username,))
        
        try:
            row = c.fetchone()
        except:
            self.validlogin = False
         
        isvalid = password == row[0]
        
        self.validlogin = isvalid
        
    @classmethod
    def newuser(self, username, password):
        c.execute('INSERT INTO users (username, password) VALUES ( %s, AES_ENCRYPT(%s, %s) )', (username, password, encryptionkey,))
        
def get_all_users():
    users = []
    c.execute('SELECT username from USERS')
    
    for row in c:
        users.append(row[0])
        
    return users
    
def initialize():
    try:
        c.execute('DROP TABLE messages')
        c.execute('DROP TABLE topics')
        c.execute('DROP TABLE users')
    except:
        print "Unable to drop tables, must be a new database."
        
    c.execute('CREATE TABLE messages (msg_id INTEGER PRIMARY KEY AUTO_INCREMENT, topic_id INTEGER, username VARCHAR(32), header TINYTEXT, msg_text TEXT)')
    c.execute('CREATE TABLE topics (topic_id INTEGER PRIMARY KEY AUTO_INCREMENT, topic_name TEXT)')
    c.execute('CREATE TABLE users (username VARCHAR(32), password VARCHAR(50))')
    Topic.newtopic("My First Topic", "admin", "my title", "This is my message!")
    User.newuser('admin','4dm1n')