from django.shortcuts import render

# Create your views here.
from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth
from django.contrib.auth import authenticate
from django.http import HttpResponse

from wechat.models import Activity

import json

class Admin(APIView):

    def get(self):
        path = self.request.path.strip("/api/a/")
        response = {'code': 0, 'msg': '', 'data': None}

        if path == "login":
            if self.request.user.is_authenticated():
                response['code'] = 0
                return response
            else:
                response['code'] = 1
                return response

        if path == "activity/list":
            activity = Activity.objects.all()
            response['code'] = 0
            response['code'] = activity
            return response

        if path == "activity/detail":
            if self.request.user.is_authenticated == False:
                response['code'] = 1
                return response


    def post(self):
        path = self.request.path.strip("/api/a/")
        response = {'code': 0, 'msg': '', 'data': None}

        if path == "login":
            usn = self.body['username']
            pwd = self.body['password']
            user = authenticate(username=usn, password=pwd)
            if user is not None and user.is_active:
                auth.login(self.request, user)
                response['code'] = 0
                return response
            response['code'] = 1
            return response

        if path == "logout":
            auth.logout(self.request)
            response['code'] = 0
            return response

        if path == "activity/delete":
            del_id = self.body["id"]
            del_act = Activity.objects.get(id=del_id)
            if del_act is not None:
                del_act.delete()
                response['code'] = 0
                return response
            else:
                response['code'] = 1
                return response

        if path == "activity/create":
            if self.request.user.is_authenticated == False:
                response['code'] = 1
                return response
            act_info = self.body
            new_act = Activity(name=act_info["name"], key=act_info["key"], place=act_info["place"],
                               description=act_info["description"], start_time=act_info["startTime"],
                               end_time=act_info["endTime"], book_start=act_info["bookStart"],
                               book_end=act_info["bookEnd"], total_tickets=act_info["totalTickets"],
                               status=act_info["status"], pic_url=act_info["picUrl"])
            new_act.save()
            response['code'] = 1
            return response

        if path == "image/upload":
            if self.request.user.is_authenticated == False:
                response['code'] = 1
                return response
            img = self.request.body['image']
            img_name = '/media/img/%s' % (img.name)
            with open(img_name, 'wb') as f:
                for fimg in img.chunks():
                    f.write(fimg)
            response['code'] = 0
            img_url = self.request.path.split("a/image/upload") + img_name
            response['data'] = img_url
            return response

