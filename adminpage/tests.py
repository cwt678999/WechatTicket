from django.test import TestCase,Client
from wechat.models import User,Ticket,Activity
from django.contrib.auth.models import User
import json

user={
    "username":"user",
    "email":"user@user.com",
    "password":"a"
}
superuser={
    "username":"admin",
    "email":"admin@admin.com",
    "password":"b"
}
class LoginTest(TestCase):

    def setUp(self):
        User.objects.create_user(user['username'],user['email'],user['password'])
        User.objects.create_superuser(superuser['username'],superuser['email'],superuser['password'])
    def testWrongLogin(self):
        c=Client()
        res = c.post('/api/a/login',user)
        code = res.json()['code']
        self.assertEqual(code,0)

        res = c.post('/api/a/login',{
                                        "username":"admin",
                                        "email":"admin@admin.com",
                                        "password":"111"
                                    })
        code = res.json()['code']
        self.assertNotEqual(code,0)
    def testRightLogin(self):
        c=Client()
        res = c.post('/api/a/login',superuser)
        code = res.json()['code']
        self.assertEqual(code,0)

class LogoutTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(sueruser['username'], sueruser['email'], sueruser['password'])

    def testWrongLogout(self):
        c= Client()
        res = c.post('/api/a/logout',content_type="application/json")
        code = res.json()['code']
        self.assertEqual(code,0)

    def testRightLogout(self):
        c= Client()
        res = c.post('/api/a/login',superuser)
        res = c.post('/api/a/logout',content_type="application/json")
        code=res.json()['code']
        self.assertEqual(code,0)

class ActivityTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(superuser['username'],superuser['email'],superuser['password'])

    def testCreateActivity(self):
        c= Client()
        c.post('/api/a/login',superuser)
        activity = {'name': '1',
                          'key': '1',
                          'place': '1',
                          'description': '1',
                          'pic_url': '/static/img/1.jpg',

                          'start_time': '2018-11-11T00:00:00.000Z',

                          'end_time': '2018-11-11T23:59:59.999Z',

                          'book_start': '2018-10-19T00:00:00.000Z',

                          'book_end': '2018-10-19T11:11:11.111Z',

                          'total_tickets': '100',
                          'status':1
                          }
        res = c.post('/api/a/activity/create',activity)
        code = res.json()['code']
        self.assertNotEqual(code,0)

    def testDeleteActivity(self):
        c = Client()
        c.post('/api/a/login',superuser)
        activity = {'name': '22',
                    'key': '1',
                    'place': '1',
                    'description': '1',
                    'pic_url': '/static/img/1.jpg',

                    'start_time': '2018-11-11T00:00:00.000Z',

                    'end_time': '2018-11-11T23:59:59.999Z',

                    'book_start': '2018-10-19T00:00:00.000Z',

                    'book_end': '2018-10-19T11:11:11.111Z',

                    'total_tickets': '100',
                    'status': 1
                    }
        res = c.post('/api/a/activity/create',activity)
        res = c.post('/api/a/activity/delete',{'name':'22'})
        code = res.json()['code']
        self.assertNotEqual(code,0)
        res = c.post('/api/a/activity/delete',{'name':'212'})
        code = res.json()['code']
        self.assertNotEqual(code,0)