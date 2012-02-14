from Cookie import SimpleCookie
import datetime

def make_set_cookie_header(name, value, path='/'):
    """
    Makes a 'Set-Cookie' header.
    
    """
    c = SimpleCookie()
    c[name] = value
    c[name]['path'] = path
    
    # can also set expires and other stuff.  See
    # Examples under http://docs.python.org/library/cookie.html.

    s = c.output()
    (key, value) = s.split(': ')
    return (key, value)
    
def load_username(cookie):
    c = SimpleCookie()
    c.load(cookie)
    
    try:
        return c["username"].value
    except:
        return ""
    
def clear_username(cookie):
    c = SimpleCookie()
    c.load(cookie)
    expires = datetime.datetime(2000, 2, 14, 18, 30, 14) + datetime.timedelta(hours=1)
    c['username']['expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S')
    
    s = c.output()
    (key, value) = s.split(': ')
    
    return (key, value)