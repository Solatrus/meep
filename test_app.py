import unittest, meep_example_app, meepcookie, twill, nose, os, sys, subprocess, time

class TestApp(unittest.TestCase):
    def setUp(self):
        meep_example_app.initialize()
        self.app = meep_example_app.MeepExampleApp()
        
    def twill(self, test):
        def get_url():
            if _server_url is None:
                raise Exception("server has not yet been started")
            return _server_url
    
        def run_server(PORT=8080):
            import time, tempfile
            global _server_url

            if PORT is None:
                PORT = int(os.environ.get('TWILL_TEST_PORT', '8000'))

            outfd = tempfile.mkstemp('twilltst')[0]

            #print 'STARTING:', sys.executable, './servetest.py', os.getcwd()
            process = subprocess.Popen([sys.executable, '-u', './servetest.py'],
                                       stderr=subprocess.STDOUT,
                                       stdout=outfd)
           
            time.sleep(1)

            _server_url = 'http://localhost:%d/' % (PORT,)

        def kill_server():
            """
            Kill the previously started Quixote server.
            """
            global _server_url
            if _server_url != None:
               try:
                  fp = urllib.urlopen('%sexit' % (_server_url,))
               except:
                  pass

            _server_url = None
            
        run_server(8080)
        
        url = get_url()
        
        #print url
        
        path = os.getcwd() + "/twill/"
        
        #print path
        
        dir = os.listdir(path)
        
        twill.execute_file(path + "test_" + test + ".twill", initial_url=url)
            
        kill_server()
        
        #assert 0

    def test_index(self):
        self.twill("index")
    
    def test_login(self):
        self.twill("login")
    
    def test_view_topic(self):
        self.twill("view_topic")
      
    def test_list_topics(self):
        self.twill("list_topics")
      
    def test_add_topic(self):
        self.twill("add_topic")
        
    def test_add_message(self):
        self.twill("add_message")
        
    def test_reply_message(self):
        self.twill("reply_message")
       
    def test_add_user(self):
        self.twill("add_user")
        
    def test_delete_message(self):
        self.twill("delete_message")
        
    def test_delete_topic(self):
        self.twill("delete_topic")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
