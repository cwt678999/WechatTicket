from django.shortcuts import render

# Create your views here.
from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth
from django.contrib.auth import authenticate
from django.core import serializers

from wechat.models import Activity
from wechat.views import CustomWeChatView
from codex.baseerror import BaseError

import json, datetime, time, os

class AdminLogin(APIView):
    def get(self):
        if self.request.user.is_authenticated():
            return None
        else:
            e = BaseError(3, '')
            raise e

    def post(self):
        usn = self.body['username']
        pwd = self.body['password']
        user = authenticate(username=usn, password=pwd)
        if user is not None and user.is_active:
            auth.login(self.request, user)
            return None
        e = BaseError(3, '')
        raise e

class AdminLogout(APIView):
    def post(self):
        auth.logout(self.request)
        return None

class AdminActivityList(APIView):
    def stringToTimeStamp(self, date_str):
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return int(timeStamp)

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

    def get(self):
        activity_json = json.loads(serializers.serialize("json", Activity.objects.all()))
        activity = self.formatActivityList(activity_json)
        return activity

class AdminActivityDelete(APIView):
    def post(self):
        del_id = self.body["id"]
        del_act = Activity.objects.get(id=del_id)
        if del_act is not None:
            del_act.delete()
            return None
        else:
            e = BaseError(2, '')
            raise e

class AdminActivityCreate(APIView):
    def post(self):
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

class AdminImageUpload(APIView):
    def post(self):
        img = self.input['image'][0]
        img_name = './media/img/%s' % (img.name)
        print(os.getcwd())
        with open(img_name, 'wb') as f:
            for fimg in img.chunks():
                f.write(fimg)
        img_url = self.request.get_host() + self.request.path + img_name.strip('.')
        return img_url

class AdminActivityDetail(APIView):
    def stringToTimeStamp(self, date_str):
        d = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return int(timeStamp)

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
        act_id = self.query['id']
        detail_queryset = Activity.objects.filter(id=act_id)
        detail_json = json.loads(serializers.serialize("json", detail_queryset))
        detail = self.formatActivityDetail(detail_json)
        return detail

    def post(self):
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

class AdminActivityMenu(APIView):
    def get(self):
        res = []
        act = Activity.objects.all()
        current_stamp = int(time.time())
        count = 1
        for line in act:
            start_stamp = time.mktime(line.book_start.timetuple())
            end_stamp = time.mktime(line.book_end.timetuple())
            if start_stamp < current_stamp and current_stamp < end_stamp:
                tmp_dict = {}
                tmp_dict['id'] = line.id
                tmp_dict['name'] = line.name
                tmp_dict['menuIndex'] = 0
                res.append(tmp_dict)
        return res

    def post(self):
        list = self.body
        act_list = []
        for update_id in list:
            act = Activity.objects.get(id=update_id)
            act_list.append(act)
        CustomWeChatView.update_menu(act_list)
        return None

class AdminActivityCheckin(APIView):
    def post(self):
return None
