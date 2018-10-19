# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Ticket, User, Activity

import uuid, random, time


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

    def check(self):
        return self.is_book_event_click(self.view.event_keys['book_header'])

    def handle(self):
        input_event = self.input['EventKey'].split('_')
        act_id = int(input_event[2])
        act = Activity.objects.get(id=act_id)
        openid = self.input['FromUserName']
        studentid = User.objects.get(open_id=openid).student_id
        bookstart = self.datetimeToStamp(act.book_start)
        bookend = self.datetimeToStamp(act.book_end)
        current = int(time.time())
        try:
            if current < bookstart or current > bookend:
                raise Exception('not booking time')
        except:
            return self.reply_text(self.get_message('book_fail_time', activity_name=act.name,
                                                    book_start=act.book_start, book_end=act.book_end))
        try:
            remain = act.remain_tickets
            if remain <= 0:
                raise Exception('no more tickets left')
        except:
            return self.reply_text(self.get_message('book_fail_no_remain', activity_name=act.name))
        try:
            Ticket.objects.get(student_id=studentid, activity_id=act_id)
        except:
            uniqueid = self.createUniqueId()
            print(uniqueid)
            sta = Ticket.STATUS_VALID
            ticket = Ticket(student_id=studentid, unique_id=uniqueid, activity_id=act_id, status=sta)
            ticket.save()
            act.remain_tickets -= 1
            act.save()
            return self.reply_text(self.get_message('book_success', activity_name=act.name, unique_id=uniqueid))
        else:
            return self.reply_text(self.get_message('book_fail_exist', activity_name=act.name))