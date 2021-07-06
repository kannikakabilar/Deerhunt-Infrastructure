import pytest
import requests

from .testbase import BaseTester

def test_login(request, flaskaddr, receive_email):
    temp = receive_email.split(':')
    email = temp[0]
    r = requests.post(f'http://{flaskaddr}/login', json={'email': email, 'password': 'tester1234'})
    with BaseTester() as test:
        test.run(request.node.name, r.text)
