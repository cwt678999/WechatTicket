# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity,Ticket,User
from WeChatTicket import settings
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