from django.shortcuts import render

# Create your views here.
from codex.baseerror import *
from codex.baseview import APIView

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class Admin(APIView):

    def get(self):
        return

    def post(self):
        usn = self.body.username
        pwd = self.body.password
        user = authenticate(username=usn, password=pwd)
        return