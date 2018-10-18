from django.shortcuts import render

# Create your views here.
from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.core import serializers

from wechat.models import Activity

import json, datetime, time

class Admin(APIView):

    def stringToTimeStamp(self, date_str):
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return int(timeStamp)

    def timeStampToString(self, date_stamp):
        d = datetime.datetime.fromtimestamp(float(date_stamp))
        str = d.strftime("%Y-%m-%d %H:%M:%S.%f")
        return str

    def formatActivityList(self, act_json_list):
        res_list = []
        for line in act_json_list:
            tmp_dict = {}
            fields = line['fields']
            tmp_dict['id'] = line['pk']
            tmp_dict['name'] = fields['name']
            tmp_dict['description'] = fields['description']
            tmp_time = fields['start_time'].replace("T", " ").replace("Z", "")
            tmp_dict['startTime'] = self.stringToTimeStamp(tmp_time)
            tmp_time = fields['end_time'].replace("T", " ").replace("Z", "")
            tmp_dict['endTime'] = self.stringToTimeStamp(tmp_time)
            tmp_dict['place'] = fields['place']
            tmp_time = fields['book_start'].replace("T", " ").replace("Z", "")
            tmp_dict['bookStart'] = self.stringToTimeStamp(tmp_time)
            tmp_time = fields['book_end'].replace("T", " ").replace("Z", "")
            tmp_dict['bookEnd'] = self.stringToTimeStamp(tmp_time)
            tmp_dict['currentTime'] = int(time.time())
            tmp_dict['status'] = fields['status']
            res_list.append(tmp_dict)
        return res_list


    def formatActivityDetail(self, act_json):
        fields = act_json[0]['fields']
        tmp_dict = {}
        tmp_dict['name'] = fields['name']
        tmp_dict['key'] = fields['key']
        tmp_dict['description'] = fields['description']
        tmp_time = fields['start_time'].replace("T", " ").replace("Z", "")
        tmp_dict['startTime'] = self.stringToTimeStamp(tmp_time)
        tmp_time = fields['end_time'].replace("T", " ").replace("Z", "")
        tmp_dict['endTime'] = self.stringToTimeStamp(tmp_time)
        tmp_dict['place'] = fields['place']
        tmp_time = fields['book_start'].replace("T", " ").replace("Z", "")
        tmp_dict['bookStart'] = self.stringToTimeStamp(tmp_time)
        tmp_time = fields['book_end'].replace("T", " ").replace("Z", "")
        tmp_dict['bookEnd'] = self.stringToTimeStamp(tmp_time)
        tmp_dict['totalTickets'] = fields['total_tickets']
        tmp_dict['picUrl'] = fields['pic_url']
        tmp_dict['bookedTickets'] = fields['total_tickets'] - fields['remain_tickets']
        tmp_dict['usedTickets'] = 0
        tmp_dict['currentTime'] = int(time.time())
        tmp_dict['status'] = fields['status']
        return tmp_dict

    def get(self):
        path = self.request.path[7:]
        response = {'code': 0, 'msg': '', 'data': None}

        if path == "login":
            if self.request.user.is_authenticated():
                return None
            else:
                response['code'] = 3
                raise response

        if path == "activity/list":
            activity_json = json.loads(serializers.serialize("json", Activity.objects.all()))
            activity = self.formatActivityList(activity_json)
            return activity

        if path == "activity/detail":
            if self.request.user.is_authenticated == False:
                response['code'] = 3
                raise response
            act_id = self.query['id']
            detail_queryset = Activity.objects.filter(id=act_id)
            detail_json = json.loads(serializers.serialize("json", detail_queryset))
            detail = self.formatActivityDetail(detail_json)
            return detail

        if path == "activity/menu":
            res = []
            act = Activity.objects.all()


    def post(self):
        path = self.request.path[7:]
        response = {'code': 0, 'msg': '', 'data': None}

        if path == "login":
            usn = self.body['username']
            pwd = self.body['password']
            user = authenticate(username=usn, password=pwd)
            if user is not None and user.is_active:
                auth.login(self.request, user)
                return None
            response['code'] = 3
            raise response

        if path == "logout":
            auth.logout(self.request)
            return None

        if path == "activity/delete":
            del_id = self.body["id"]
            del_act = Activity.objects.get(id=del_id)
            if del_act is not None:
                del_act.delete()
                return None
            else:
                response['code'] = 2
                raise response

        if path == "activity/create":
            if self.request.user.is_authenticated == False:
                response['code'] = 3
                raise response
            act_info = self.body
            new_act = Activity(name=act_info["name"], key=act_info["key"], place=act_info["place"],
                               description=act_info["description"], start_time=act_info["startTime"],
                               end_time=act_info["endTime"], book_start=act_info["bookStart"],
                               book_end=act_info["bookEnd"], total_tickets=act_info["totalTickets"],
                               status=act_info["status"], pic_url=act_info["picUrl"],
                               remain_tickets=act_info["totalTickets"])
            new_act.save()
            id = new_act.id
            return id

        if path == "activity/delete":
            del_id = self.body
            del_act = Activity.objects.get(id=del_id)
            if del_act is None:
                response['code'] = 1
                raise response
            del_act.delete()
            return None


        if path == "activity/detail":
            if self.request.user.is_authenticated == False:
                response['code'] = 3
                raise response
            new_act_info = self.body
            act_id = new_act_info['id']
            act = Activity.objects.get(id=act_id)
            if act:
                act.description = new_act_info['description']
                act.pic_url = new_act_info['picUrl']
                act.start_time = new_act_info['startTime']
                act.end_time = new_act_info['endTime']
                act.book_start = new_act_info['bookStart']
                act.book_end = new_act_info['bookEnd']
                act.total_tickets = new_act_info['totalTickets']
                act.status = new_act_info['status']
                act.save()
            return None

        if path == "image/upload":
            if self.request.user.is_authenticated == False:
                response['code'] = 3
                raise response
            img = self.request.body['image']
            img_name = '/media/img/%s' % (img.name)
            with open(img_name, 'wb') as f:
                for fimg in img.chunks():
                    f.write(fimg)
            response['code'] = 0
            img_url = self.request.path.split("a/image/upload") + img_name
            return img_url

