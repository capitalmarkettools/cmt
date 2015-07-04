'''
Created on Sep 28, 2012

@author: Capital Market Tools
'''
from django.core.mail import send_mail
class emailTest(object):

    def sendEmail(self):
        send_mail('test','hi','capitalmarkettools.org@gmail.com',['capitalmarkettools.org@gmail.com'],
                  fail_silently=False)

def main():
    e = emailTest()
    e.sendEmail()
if __name__ == "__main__":
    main()