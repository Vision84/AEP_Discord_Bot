# import smtplib
import sys
# import yagmail

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main():
    sender_address, sender_password = get_sender_details("sender_details.txt")
    
    message = Mail(
        from_email=sender_address,
        # ! change mail when testing
        to_emails='receiver',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print()
        print(response.headers)
    except Exception as e:
        print(e.message)


def get_sender_details(f):
    """
    Gets the detials about the sender from f
    """
    try:
        with open(f, 'r') as f:
            return f.read().split()

    except FileNotFoundError:
        sys.exit(f"{f} Not Found.")


if __name__ == '__main__':
    main()
