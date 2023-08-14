# import smtplib
import sys
# import yagmail
import csv 
import os
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import date, datetime




def main():
    class_schedule = read_class_schedule("class_schedule.csv")
    sender_address, sender_password = get_sender_details("sender_details.txt")
    current_day_of_week = date.today().strftime("%A")#Finds the current day of the week
    current_time = datetime.now().time()#Finds the current time
   
    for class_info in class_schedule:
            if class_info['Day'] == current_day_of_week and is_time_to_send(current_time, class_info['Time']):
                send_class_reminders(class_info, sender_address)

def is_time_to_send(current_time, class_time_str):
    class_time = datetime.strptime(class_time_str.split(' ')[-2], "%I:%M %p").time()
    time_difference = datetime.combine(date.today(), class_time) - datetime.combine(date.today(), current_time)
    return 0 <= time_difference.total_seconds() < 3600  # Check if the class time is within 1 hour from now


def send_class_reminders(class_info, sender_address):
    recipients = class_info['Email'].split(';')

    for recipient in recipients:
        message = Mail(
            from_email=sender_address,
            to_emails=recipient,
            subject=f'AEP Class Reminder: {class_info["Item"]} Today',
            html_content=f'Hello {class_info["First Name"]},<br>'
                         f'Your class "{class_info["Item"]}" is scheduled for today at "{class_info["Time"]}".<br>'
                         f'Please remember to attend at the specified time.')

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
             
            # Capture recipient's email address
            sent_to = recipient

            # Create a message with the recipient's information
            discord_message = f"Email Sent!\nName: {class_info['First Name']} {class_info['Last Name']}}}Recipient: {sent_to}\nClass: {class_info['Item']}\nTime: {class_info['Time']}"

            # Send the message to Discord webhook
            webhook_url = "https://discord.com/api/webhooks/1087912305876008960/3aRKWpauzvJrhSsRL2sLTuXM8TNnv5TlaFyiqGtGKv25G2cxWsOregwsyA9hUTWAcyr5"
            data = {
                "content": discord_message
            }
            response = requests.post(webhook_url, json=data)
            if response.status_code != 204:
                print(f"Error sending to Discord webhook. Status Code: {response.status_code}")
        
        except Exception as e:
            print(str(e))


            
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
            return f.read().split()

    except FileNotFoundError:
        sys.exit(f"{f} Not Found.")


if __name__ == '__main__':
    main()
