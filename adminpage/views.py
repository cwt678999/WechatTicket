from django.shortcuts import render

# Create your views here.
from codex.baseerror import *
from codex.baseview import APIView

from django.contrib import auth
from django.contrib.auth import authenticate
from django.core import serializers
from django.utils import timezone

from wechat.models import Activity, Ticket
from wechat.views import CustomWeChatView
from codex.baseerror import BaseError

import json, datetime, time, os, uuid

class AdminLogin(APIView):

    def get(self):
        if self.request.user.is_authenticated():
            return None
        else:
            raise ValidateError('')

    def post(self):
        self.check_input('username', 'password')
        usn = self.input['username']
        pwd = self.input['password']
        user = authenticate(username=usn, password=pwd)
        if user is not None and user.is_active:
            auth.login(self.request, user)
            return None
        raise ValidateError('')

class AdminLogout(APIView):

    def post(self):
        auth.logout(self.request)
        return None

class AdminActivityList(APIView):

    def get(self):
        act = Activity.objects.all()
        activity = []
        for line in act:
            tmp_dict = {}
            tmp_dict['id'] = line.id
            tmp_dict['name'] = line.name
            tmp_dict['description'] = line.description
            tmp_dict['startTime'] = time.mktime(line.start_time.timetuple()) + 8 * 60 * 60
            tmp_dict['endTime'] = time.mktime(line.end_time.timetuple()) + 8 * 60 * 60
            tmp_dict['place'] = line.place
            tmp_dict['bookStart'] = time.mktime(line.book_start.timetuple()) + 8 * 60 * 60
            tmp_dict['bookEnd'] = time.mktime(line.book_end.timetuple()) + 8 * 60 * 60
            tmp_dict['currentTime'] = time.mktime(timezone.now().timetuple()) + 8 * 60 * 60
            tmp_dict['status'] = line.status
            activity.append(tmp_dict)
        return activity

class AdminActivityDelete(APIView):

    def post(self):
        self.check_input('id')
        del_id = self.input["id"]
        try:
            del_act = Activity.objects.get(id=del_id)
        except:
            raise LogicError('activity not found')
        else:
            del_act.delete()
            return None

class AdminActivityCreate(APIView):

    def post(self):
        self.check_input('name', 'key', 'place' , 'description', 'startTime', 'endTime', 'bookStart'
                         , 'bookEnd', 'totalTickets', 'status', 'picUrl')
        act_info = self.input
        new_act = Activity(name=act_info["name"], key=act_info["key"], place=act_info["place"],
                           description=act_info["description"], start_time=act_info["startTime"],
                           end_time=act_info["endTime"], book_start=act_info["bookStart"],
                           book_end=act_info["bookEnd"], total_tickets=act_info["totalTickets"],
                           status=act_info["status"], pic_url=act_info["picUrl"],
                           remain_tickets=act_info["totalTickets"], used_tickets=0)
        new_act.save()
        id = new_act.id
        return id

class AdminImageUpload(APIView):

    def post(self):
        self.check_input('image')
        img = self.input['image'][0]
        img_name = './static/media/img/%s' % (str(uuid.uuid1()) + '-' + img.name)
        with open(img_name, 'wb') as f:
            for fimg in img.chunks():
                f.write(fimg)
        img_url = 'http://' + self.request.get_host() + '/' + img_name.strip('./static')
        return img_url

class AdminActivityDetail(APIView):

    def stringToTimeStamp(self, date_str, pattern):
        d = datetime.datetime.strptime(date_str, pattern)
        t = d.timetuple()
        timeStamp = int(time.mktime(t))
        timeStamp = float(str(timeStamp) + str("%06d" % d.microsecond)) / 1000000
        return int(timeStamp)

    def get(self):
        self.check_input('id')
        act_id = self.input['id']
        try:
            act = Activity.objects.get(id=act_id)
        except:
            raise LogicError('activity not found')
        else:
            detail = {'name': act.name, 'key': act.key, 'description': act.description
                , 'startTime': int(time.mktime(act.start_time.timetuple())) + 8*60*60
                , 'endTime': int(time.mktime(act.end_time.timetuple())) + 8*60*60
                , 'place': act.place, 'bookStart': int(time.mktime(act.book_start.timetuple())) + 8*60*60
                , 'bookEnd': int(time.mktime(act.book_end.timetuple())) + 8*60*60
                , 'totalTickets': act.total_tickets, 'picUrl': act.pic_url
                , 'bookedTickets': act.total_tickets - act.remain_tickets
                , 'usedTickets': act.used_tickets, 'currentTime': int(time.mktime(timezone.now().timetuple())) + 8*60*60
                , 'status': act.status}
            return detail

    def post(self):
        self.check_input('id', 'name', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart',
                         'bookEnd', 'totalTickets', 'status')
        new_act_info = self.input
        act_id = new_act_info['id']
        current = timezone.now()
        try:
            act = Activity.objects.get(id=act_id)
        except:
            raise LogicError('no activity')
        else:
            if act.status == 0:
                act.name = new_act_info['name']
                act.place = new_act_info['place']
            act.description = new_act_info['description']
            act.pic_url = new_act_info['picUrl']
            pattern = "%Y-%m-%dT%H:%M:%S.%fZ"
            if current < act.start_time:
                time_stamp = self.stringToTimeStamp(new_act_info['bookEnd'], pattern) + 8*60*60
                act.book_end = datetime.datetime.fromtimestamp(time_stamp)
            if current < act.end_time:
                time_stamp = self.stringToTimeStamp(new_act_info['startTime'], pattern) + 8 * 60 * 60
                act.start_time = datetime.datetime.fromtimestamp(time_stamp)
                time_stamp = self.stringToTimeStamp(new_act_info['endTime'], pattern) + 8 * 60 * 60
                act.end_time = datetime.datetime.fromtimestamp(time_stamp)
            if current < act.book_start:
                act.total_tickets = new_act_info['totalTickets']
            if act.status == 0:
                time_stamp = self.stringToTimeStamp(new_act_info['bookStart'], pattern) + 8 * 60 * 60
                act.book_start = datetime.datetime.fromtimestamp(time_stamp)
                act.status = new_act_info['status']
            act.save()
        return None

class AdminActivityMenu(APIView):

    def get(self):
        res = []
        act = Activity.objects.all()
        current_stamp = time.mktime(timezone.now().timetuple())
        for line in act:
            start_stamp = time.mktime(line.book_start.timetuple())
            end_stamp = time.mktime(line.book_end.timetuple())
            if current_stamp < end_stamp:
                tmp_dict = {}
                tmp_dict['id'] = line.id
                tmp_dict['name'] = line.name
                tmp_dict['menuIndex'] = 0
                res.append(tmp_dict)
        return res

    def post(self):
        if isinstance(self.input, list) == False:
            raise InputError('')
        input_list = self.input
        act_list = []
        for update_id in input_list:
            act = Activity.objects.get(id=update_id)
            act_list.append(act)
        CustomWeChatView.update_menu(act_list)
        return None

class AdminActivityCheckin(APIView):

    def datetimeToStamp(self, date_time):
        return int(time.mktime(date_time.timetuple()))

    def post(self):
        self.check_input('actId')
        # 活动是否存在
        try:
            act = Activity.objects.get(id=int(self.input['actId']))
        except:
            raise LogicError('activity not found')
        else:
            act_start = self.datetimeToStamp(act.start_time)
            act_end = self.datetimeToStamp(act.end_time)
            current = int(time.mktime(timezone.now().timetuple()))
            if current < act_start or current > act_end:
                raise LogicError('not activity time')
        # 输入是否合法
        try:
            if 'ticket' in self.input:
                ticket = Ticket.objects.get(unique_id=int(self.input['ticket']), activity_id=int(self.input['actId']))
            elif 'studentId' in self.input:
                ticket = Ticket.objects.get(student_id=int(self.input['studentId']), activity_id=int(self.input['actId']))
            else:
                raise InputError('input error')
        except:
            raise LogicError('ticket not found')
        else:
            if ticket.status != Ticket.STATUS_VALID:
                raise LogicError('invalid ticket')
            ticket.status = Ticket.STATUS_USED
            ticket.save()
            act.used_tickets += 1
            act.save()
            return {'ticket': ticket.unique_id, 'studentId': ticket.student_id}
