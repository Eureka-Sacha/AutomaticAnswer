# -*- coding: utf-8 -*-
"""
@authon:
@time: 2017/10/25 11:23
@desc: 

"""
import abc
from email.header import decode_header

from poplib import POP3, POP3_SSL


class MailClientFactory(type):
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(POPClient, *args, **kwargs)
        obj.__init__(*args, **kwargs)
        return obj


class Mail:
    PROTOCOL = ("pop", "imap", "smtp")

    def __init__(self):
        self.__protocol = "pop"
        self.mail_list = []
        self.__client = None
        self.__buffer = []
        self.parser = MailParser()

    def conn(self, service, port, ssl=False):
        if self.__client is None:
            self.__client = POPClient(service, port, ssl=ssl)

    def login(self, user, passwd):
        if self.__client is None:
            raise TypeError("Don't have any client")
        self.__client.login(user, passwd)

    def exit(self):
        if self.__client is not None:
            self.__client.logout()
            self.__client = None

    def list(self):
        return self.__client.list()

    def get(self, title):
        return self.__client.get(title)

    def delete(self, title):
        return self.__client.delete(title)

    def download(self, title):
        return self.__client.download(title)

    def send(self, receiver, title=None, text=None, annex=None):
        return self.__client.send(receiver, title, text, annex)


class MailClient:
    def __init__(self, service, port):
        self.__service = service
        self.__port = port

    @abc.abstractmethod
    def login(self, user, passwd):
        pass

    @abc.abstractmethod
    def logout(self):
        pass

    @abc.abstractmethod
    def list(self):
        pass

    @abc.abstractmethod
    def get(self):
        pass

    @abc.abstractmethod
    def delete(self):
        pass

    @abc.abstractmethod
    def download(self):
        pass

    @abc.abstractmethod
    def send(self):
        pass


class POPClient:
    def delete(self):
        pass

    def list(self):
        return self.pop.list()

    def download(self, title):
        return self.pop.retr(title)

    def send(self):
        pass

    def get(self, title):
        return self.pop.retr(title)

    def login(self, user, passwd):
        self.pop.user(user)
        self.pop.pass_(passwd)
        return self.pop.stat()

    def logout(self):
        return self.pop.quit()

    #   子类不重写__init__自动调用父类的init
    def __init__(self, service, port, ssl=False):
        if ssl:
            self.pop = POP3_SSL(service, port=port)
        else:
            self.pop = POP3(service, port=port)


class IMAPClient(MailClient):
    def delete(self):
        pass

    def list(self):
        pass

    def download(self):
        pass

    def send(self):
        pass

    def get(self):
        pass

    def login(self, user, passwd):
        pass

    def logout(self):
        pass


class SMTPClient(MailClient):
    def delete(self):
        pass

    def list(self):
        pass

    def download(self):
        pass

    def send(self):
        pass

    def get(self):
        pass

    def login(self, user, passwd):
        pass

    def logout(self):
        pass


class MailContext:
    def __init__(self, message):
        from email.message import Message
        self.message = Message(message)
        self.index = None
        self.subject = self.decode_str("Subject")
        self.from_name = self.decode_str("From")
        self.from_mail = self.decode_str("From")
        self.to_name = self.decode_str("To")
        self.to_mail = self.decode_str("To")
        self.charset = self.guess_charset()
        self.file = None
        self.text = None
        self.size = None
        self.date = self.decode_str("From")
        self.cc = None
        self.bc = None

    def guess_charset(self):
        charset = self.message.get_charset()
        if charset is None:
            content_type = self.message.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def decode_str(self, s):
        """
        解析邮件头数据
        :param s:
        :return:
        """
        decoded = decode_header(self.message.get(s))
        result = []
        value, charset = None, None
        for value, charset in decoded:
            if charset:
                value = value.decode(charset)
                result.append(value)
        if len(result) > 1:
            return result
        return value


class MailParser:
    def __init__(self, pr=None, default_buffed=10):
        if pr:
            self.__pr = Parser()
        else:
            self.__pr = pr
        # 暂时不考虑缓存了
        self.__buffer = []
        self.__buffer_num = default_buffed

    def parse(self, msg):
        return self.__buffer.append(MailContext(self.__pr.parse(msg)))
        # if len(self.__buffer) < self.__buffer_num:
        #     self.__buffer.append(MailContext(self.__pr.parse(msg)))
        # else:
        #     self.__buffer.append(MailContext(self.__pr.parse(msg, True)))

    def get(self, title, only_annex=False):
        if type(title) == int():
            return self.__buffer[title]
        else:
            return [x for x in self.__buffer if str(x.subject).index(title) > -1]

    def download(self, title):
        return MailParser.get(title, True)


if __name__ == '__main__':
    from email.parser import Parser
    from email.feedparser import FeedParser

    mail = Mail()
    mail.conn("mail.billjc.com", 110, False)
    mail.login("", "")
    mail_list = list(mail.list()[1])
    print mail_list[1].split(" ")
    print mail_list

    m = "\n".join(mail.get("1")[1])
    parser = Parser()
    result = parser.parsestr(m)
    print result

    fd = FeedParser()
    result = fd.feed(m)
    # result = fd.close()
    print result
    fd.feed("\n".join(mail.get("2")[1]))
    result = fd.close()
    print result
