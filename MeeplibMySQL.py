import MySQLdb

db = MySQLdb.connect(host="localhost",user="meep_db",passwd="meep_db_passw0rd!", db='cse491')
c = db.cursor()

def initalize():
    c.execute('CREATE TABLE messages (msg_id INTEGER PRIMARY KEY AUTO_INCREMENT, topic_id INTEGER, user TINYTEXT, header TINYTEXT, msg_text TEXT)')
    c.execute('CREATE TABLE topics (topic_id INTEGER PRIMARY KEY AUTO_INCREMENT, topic_name TEXT)')
    c.execute('INSERT INTO topics (\'First Topic\')')
    c.execute('INSERT INTO messages (1, \'admin\', \'my title\', \'This is my message!\')')
    
class Message(object):
    def __init__(self, msg_id, topic_id, user, header, msg_text)
        self.msg_id = msg_id
        self.topic_id = topic_id
        self.user = user
        self.header = header
        self.msg_text = msg_text

class Topic(object):
	def __init__(self, topic_id):
        c.execute('SELECT * FROM messages WHERE (topic_id = {0}'.format(topic_id))
        
        self.messages = []
        
        for row in c:
            msg = Message(row[0], row[1], row[2], row[3], row[4])
            self.messages.append(msg)
            
        c.execute('SELECT * FROM topics WHERE (topic_id = {0}'.format(topic_id))
        
        row = c.fetchone()
        
        self.topic_name = row[1]
            
    @classmethod
    def newtopic(self, topic_name, msg_header, msg_text, user):
        c.execute('INSERT INTO topics (\'{0}\')'.format(topic_name))
        c.execute('SELECT * FROM topics ORDER BY topic_id DESC LIMIT 1')
        
        for row in c:
            c.execute('INSERT INTO messages ({0}, \'{1}\', \'{2}\', \'{3}\')'.format(row[0], usr, msg_header, msg_text))
	
	def newmessage(self, msg_header, msg_text, user):
		c.execute('INSERT INTO messages ({0}, \'{1}\', \'{2}\', \'{3}\')'.format(self.topic_id, usr, msg_header, msg_text))