import unittest
from email.message import Message
from webguard import inspect_url, inspect_response

class Tests(unittest.TestCase):
    def test_reject_bad_scheme(self):
        with self.assertRaises(ValueError): inspect_url('ftp://example.com')
    def test_reject_embedded_credentials(self):
        with self.assertRaises(ValueError): inspect_url('https://user:password@example.com')
    def test_independent_cookie_flags(self):
        headers = Message()
        headers['Content-Security-Policy'] = "default-src 'self'"
        headers['Set-Cookie'] = 'session=abc; Secure; HttpOnly'
        headers['Set-Cookie'] = 'tracking=xyz; Path=/'
        findings = inspect_response('https://example.test','https://example.test',200,headers)['findings']
        self.assertTrue(any('Cookie #2 missing Secure' in x['finding'] for x in findings))
        self.assertFalse(any('Cookie #1' in x['finding'] for x in findings))

if __name__ == '__main__': unittest.main()
