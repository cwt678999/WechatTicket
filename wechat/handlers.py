# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler

import uuid, random, time

from wechat.models import Activity,Ticket,User
from WeChatTicket import settings

from django.utils import timezone


__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))

class BookHandler(WeChatHandler):

    def createUniqueId(self):
        unique_id = str(uuid.uuid1()) + '-' + str(random.randint(0, 100000))
        return unique_id

    def datetimeToStamp(self, date_time):
        return int(time.mktime(date_time.timetuple()))

    def sub8Hours(self, date_time):
        time_stamp = int(time.mktime(date_time.timetuple()))
        time_stamp -= 8 * 60 * 60
        time_tuple = time.localtime(time_stamp)
        dtime = time.strftime('%Y-%m-%d %H:%M:%S', time_tuple)
        return dtime

    def check(self):
        return self.is_book_event_click(self.view.event_keys['book_header'])

    def handle(self):
        input_event = self.input['EventKey'].split('_')
        act_id = int(input_event[2])
        act = Activity.objects.get(id=act_id)
        openid = self.input['FromUserName']
        studentid = User.objects.get(open_id=openid).student_id
        if studentid =='':
            return self.reply_text(self.get_message('book_fail_validate', activity_name=act.name))
        bookstart = self.datetimeToStamp(act.book_start)
        bookend = self.datetimeToStamp(act.book_end)
        current = int(time.mktime(timezone.now().timetuple()))
        # 判断有无票
        try:
            Ticket.objects.get(student_id=studentid, activity_id=act_id)
        except:
            # 判断活动时间
            try:
                if current < bookstart or current > bookend:
                    raise Exception('not booking time')
            except:
                return self.reply_text(self.get_message('book_fail_time', activity_name=act.name,
                                                        book_start=act.book_start
                                                        , book_end=act.book_end))
            try:
                remain = act.remain_tickets
                if remain <= 0:
                    raise Exception('no more tickets left')
            except:
                return self.reply_text(self.get_message('book_fail_no_remain', activity_name=act.name))
            # 创建票
            else:
                uniqueid = self.createUniqueId()
                print(uniqueid)
                sta = Ticket.STATUS_VALID
                ticket = Ticket(student_id=studentid, unique_id=uniqueid, activity_id=act_id, status=sta)
                ticket.save()
                act.remain_tickets -= 1
                act.save()
                return self.reply_text(self.get_message('book_success', activity_name=act.name, unique_id=uniqueid))
        else:
            ticket = Ticket.objects.get(student_id=studentid, activity_id=act_id)
            # 票取消过
            if ticket.status == Ticket.STATUS_VALID:
                return self.reply_text(self.get_message('book_fail_exist', activity_name=act.name))
            elif ticket.status == Ticket.STATUS_CANCELLED:
                ticket.status = Ticket.STATUS_VALID
                return self.reply_text(self.get_message('book_success', activity_name=act.name, unique_id=uniqueid))

class BookWhatHandler(WeChatHandler):
    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        details = []
        activities = Activity.objects.filter(status=Activity.STATUS_PUBLISHED)
        if activities:
            for item in activities:
                details.append({
                    'Title':item.name,
                    'Description':item.description,
                    'PicUrl':item.pic_url,
                    'Url':settings.get_url("/u/activity",{"id":item.id})
                })

            return self.reply_news(details)

        else :
            return self.reply_text(self.get_message('bind_account'))

class FindOutTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        details = []
        if not self.user.student_id:
            return self.reply_text("您还未绑定")
        tickets = Ticket.objects.filter(student_id=self.user.student_id,status=Ticket.STATUS_VALID)
        if not tickets:
            return self.reply_text("没有票可用")
        else :
            for item in tickets:
                activity = Activity.objects.filter(key=self.input['Content'][3:],status=Activity.STATUS_PUBLISHED)
                details.append({
                    'Title': activity.name,
                    'Description': activity.description,
                    'PicUrl': activity.pic_url,
                    'Url': settings.get_url("/u/ticket", {'openid':user.open_id,'ticket':item.unique_id})
                })
            return self.reply_news(details)
