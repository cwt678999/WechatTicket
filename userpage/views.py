from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User, Ticket, Activity
import time,datetime


def timeStamp(date):
    #d = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    t = date.timetuple()
    timestamp = int(time.mktime(t))
    timestamp = float(str(timestamp) + str("%06d" % date.microsecond)) / 1000000
    return int(timestamp)

class UserBind(APIView):

    def validate_user(self):
        user = User.get_by_openid(self.input['openid'])
        stuId = self.input['student_id']
        try:
            User.objects.get(student_id=self.input['student_id'])
        except:
            user.student_id = stuId
            user.save()
        else:
            raise ValidateError("Existed student_id")


    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()
        
class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        activity = Activity.objects.get(id=self.input['id'])
        if activity.status == Activity.STATUS_PUBLISHED:
            ActivityDict={}
            ActivityDict['name']=activity.name
            ActivityDict['key']=activity.key
            ActivityDict['description']=activity.description
            ActivityDict['startTime']=timeStamp(activity.start_time)
            ActivityDict['endTime']=timeStamp(activity.end_time)
            ActivityDict['place']=activity.place
            ActivityDict['bookStart']=timeStamp(activity.book_start)
            ActivityDict['bookEnd']=timeStamp(activity.book_end)
            ActivityDict['totalTickets']=activity.total_tickets
            ActivityDict['picUrl']=activity.pic_url
            ActivityDict['remainTickets']=activity.remain_tickets
            ActivityDict['currentTime']=int(time.time())
            return ActivityDict
        else : raise InputError("error")
class TicketDetail(APIView):

    def get(self):
        self.check_input('openid', 'ticket')
        ticket = Ticket.objects.get(unique_id=self.input['ticket'])
        TicketDict={}
        TicketDict['activityName']=ticket.activity.name
        TicketDict['place']=ticket.activity.place
        TicketDict['activityKey'] = ticket.activity.key
        TicketDict['uniqueId'] = ticket.unique_id
        TicketDict['startTime'] = timeStamp(ticket.activity.start_time)
        TicketDict['endTime'] = timeStamp(ticket.activity.end_time)
        TicketDict['currentTime'] = int(time.time())
        TicketDict['status'] = ticket.status
        return TicketDict








