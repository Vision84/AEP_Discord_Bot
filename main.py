import csv
import os
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import date, datetime
import pytz


def main():

    # Read files
    # class_schedule = read_class_schedule("class_schedules/")
    # class_schedule = read_class_schedule("test.csv")
    sender_address = "academicempowermentproject@gmail.com"

    # Gets the current day of the week
    dt_us_central = datetime.now(pytz.timezone('US/Central'))
    current_day_of_week = dt_us_central.strftime("%A")

    # path = 'class_schedules/'
    path = 'test/'
    files = os.listdir(path)

    messages = {}
    
    for file in files:
        message = []

        class_schedule = read_class_schedule(path, file)

        for class_info in class_schedule:
            day = class_info['Day']

            if day == current_day_of_week:
                message.append(send_class_reminders(class_info, sender_address))
        
        messages[file] = message

    return messages


# Send email to student
def send_class_reminders(class_info, sender_address):
    fname = class_info["Student First Name"].strip().capitalize()
    lname = class_info["Student Last Name"].strip().capitalize()
    recipient = class_info['Email']
    start_time = class_info['Start Time'].strip()
    end_time = class_info['End Time'].strip()
    subject = class_info['Subject'].strip()
    teacher = class_info['Teacher'].strip().title()
    
    message = Mail(
        from_email=sender_address,
        to_emails=recipient,
        subject='AEP Class Reminder',
        html_content=f"""
                    Hello {fname} {lname},<br><br>
                    Your class, {subject}, is scheduled for today at {start_time} - {end_time}. Your teacher is {teacher}.<br>
                    Please remember to join at the specified time.
                    <br><br>
                    Check the google classroom for the link to the meeting.<br>
                    Google Classrrom: https://classroom.google.com/c/NjE2OTI0NjAyNjQ3
                    """
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)

        # Create a message with the recipient's information
        discord_message = f"""
        Email Sent!
        Name: {fname} {lname}
        Email: {recipient}
        Class: {subject}
        Time: {start_time} - {end_time}
        Teacher: {teacher}\n
        """

        return discord_message

    except Exception as e:
        print(e)


def read_class_schedule(path, filename):
    class_schedule = []
    with open(path + filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            class_schedule.append(row)
    return class_schedule


if __name__ == '__main__':
    main()
