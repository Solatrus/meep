import unittest
import meep_example_app
import meepcookie

class TestApp(unittest.TestCase):
    def setUp(self):
        meep_example_app.initialize()
        app = meep_example_app.MeepExampleApp()
        self.app = app

    def test_index(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Add a topic' in data[0]
        assert 'Show topics' in data[0]
        
    def test_view_topic(self):
        environ = {}
        environ['PATH_INFO'] = '/m/topics/view'
        environ['QUERY_STRING'] = 'id=0'
        
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
            
        data = self.app(environ, fake_start_response)
        assert 'First Topic' in data[0]
        
    def test_list_topics(self):
        environ = {}
        environ['PATH_INFO'] = '/m/list_topics'
        
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
            
        data = self.app(environ, fake_start_response)
        assert 'First Topic' in data[0]
        
    def test_add_topic(self):
        environ = {}
        environ['PATH_INFO'] = '/m/add_topic'
        
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
            
        data = self.app(environ, fake_start_response)
        assert 'Add a new topic' in data
       
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
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
            
        data = self.app(environ, fake_start_response)
        assert 'Add a new topic' in data
        
    def test_login(self):
        environ = {}
        environ['PATH_INFO'] = '/login'
        
        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers
            
        assert 'Username' in data
        data = self.app(environ, fake_start_response)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
