import unittest
import meep_example_app
import meepcookie
import nose

class TestApp(unittest.TestCase):
    def setUp(self):
        meep_example_app.initialize()
        app = meep_example_app.MeepExampleApp()
        self.app = app

    def test_index(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            nose.tools.assert_equal(status, '200 OK')
            nose.tools.assert_equal((('Content-type', 'text/html') in headers), True)

        nose.tools.assert_equal(('Add a topic' in data[0]), True)
        nose.tools.assert_equal(('Show topics' in data[0]), True)
    
    def test_view_topic(self):
        environ = {}
        environ['PATH_INFO'] = '/m/topics/view'
        environ['QUERY_STRING'] = 'id=0'
        
        def fake_start_response(status, headers):
            nose.tools.assert_equal(status, '200 OK')
            nose.tools.assert_equal((('Content-type', 'text/html') in headers), True)
            
        data = self.app(environ, fake_start_response)
        nose.tools.assert_equal(('First Topic' in data[0]), True)
      
    def test_list_topics(self):
        environ = {}
        environ['PATH_INFO'] = '/m/list_topics'
        
        def fake_start_response(status, headers):
            nose.tools.assert_equal(status, '200 OK')
            nose.tools.assert_equal((('Content-type', 'text/html') in headers), True)
            
        data = self.app(environ, fake_start_response)
        nose.tools.assert_equal(('First Topic' in data[0]), True)
      
    def test_add_topic(self):
        environ = {}
        environ['PATH_INFO'] = '/m/add_topic'
        
        def fake_start_response(status, headers):
            nose.tools.assert_equal(status, '200 OK')
            nose.tools.assert_equal((('Content-type', 'text/html') in headers), True)
            
        data = self.app(environ, fake_start_response)
        nose.tools.assert_equal(('Add a new topic' in data[0]), True)
       

    # I set up adding users so that it's required to be logged in as the admin user account.
    # This was unnecessary to do, but I felt like doing it anyway.
    def test_add_user(self):
        environ = {}
        environ['PATH_INFO'] = '/add_user'
        
        cookie_name, cookie_val = \
                    meepcookie.make_set_cookie_header('username',
                                                    'admin')
        
        def fake_start_response(status, headers):
            headers.append((cookie_name, cookie_val))
            nose.tools.assert_equal(status, '200 OK')
            nose.tools.assert_equal((('Content-type', 'text/html') in headers), True)
            
        data = self.app(environ, fake_start_response)
        nose.tools.assert_equal(('Add a new topic' in data), True)
      
    def test_login(self):
        environ = {}
        environ['PATH_INFO'] = '/login'
        
        def fake_start_response(status, headers):
            nose.tools.assert_equal(status, '200 OK')
            nose.tools.assert_equal((('Content-type', 'text/html') in headers), True)
            
                nose.tools.assert_equal(('Username' in data), True)
        data = self.app(environ, fake_start_response)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
