import sys
import csv 
import os
import requests
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import date, datetime


def main():
    # Read files
    class_schedule = read_class_schedule("class_schedule.csv")
    sender_address = get_sender_details("sender_details.txt")

    # Gets the current day of the week
    current_day_of_week = date.today().strftime("%A")

    # Gets the current time
    current_time = datetime.now().time()
   
    for class_info in class_schedule:
            # Get the day from Item
            item = class_info['Item']
            day_index = item.find(current_day_of_week)
            day = item[day_index:item.find(' ', day_index + 1)]

            if day:
                send_class_reminders(class_info, sender_address)


#Extracting the email of the recipient
def send_class_reminders(class_info, sender_address):
    recipients = class_info['Email'].split(';')
    item = class_info["Item"]
    start_time, end_time, am_pm = re.findall(r'(\d:\d\d) - (\d:\d\d)(\w\w)', item)[0]
    class_name = item[0:item.find(date.today().strftime("%A"))]
    
    for recipient in recipients:
        message = Mail(
            from_email=sender_address,
            to_emails=recipient, 
            subject=f'AEP Class Reminder',
            html_content= f"""
                        Hello {class_info["First Name"]} {class_info["Last Name"]},<br><br>
                        Your class {class_name} is scheduled for today at {start_time} - {end_time} {am_pm}.<br>
                        Please remember to join at the specified time.
                        """
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
             
            # Capture recipient's email address
            sent_to = recipient

            # Create a message with the recipient's information
            discord_message = f"""
            Email Sent!
            Name: {class_info['First Name']} {class_info['Last Name']}
            Recipient: {sent_to}
            Class: {class_name}
            Time: {start_time} - {end_time} {am_pm}\n
            """

            # Send the message to Discord webhook
            webhook_url = "https://discord.com/api/webhooks/1087912305876008960/3aRKWpauzvJrhSsRL2sLTuXM8TNnv5TlaFyiqGtGKv25G2cxWsOregwsyA9hUTWAcyr5"
            data = {
                "content": discord_message
            }
            response_discord = requests.post(webhook_url, json=data)

            # Debugging purposes
            if response_discord.status_code != 204:
                print(f"Error sending to Discord webhook. Status Code: {response_discord.status_code}")
                print(response_discord.content)

        except Exception as e:
            print(e)

            
def read_class_schedule(filename):
    class_schedule = []
    with open(filename, 'r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            class_schedule.append(row)
    return class_schedule


def get_sender_details(f):
    """
    Gets the detials about the sender from f
    """
    try:
        with open(f, 'r') as f:
            return f.read().split()[0]

    except FileNotFoundError:
        sys.exit(f"{f} Not Found.")


if __name__ == '__main__':
    main()
