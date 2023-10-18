import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from main import *
import google_sheets

from pprint import pprint

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# bot = commands.Bot(intents=discord.Intents.all())
bot = commands.Bot()

PATH = 'class_schedules/'
# PATH = 'test/'
FILES = os.listdir(PATH)

AEP_LOGO_BG_COLOR = discord.Color.from_rgb(194, 255, 208)


@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:')
    bot_guilds = [g for g in [o.name for o in bot.guilds]]
    print(*bot_guilds, sep='\n')


@bot.slash_command(name='hello', description='Greets You!')
async def hello(ctx):
    await ctx.respond(f'Hello {ctx.author.display_name}!')


@bot.slash_command(name='send_reminders', description='Send Reminders to Students that have a class today.')
@commands.has_role('VP')
async def send_reminders(ctx):
    await ctx.respond("# Sending Reminders!")
    messages = main()

    for subject, student in messages.items():
        await ctx.send('## ' + subject.split('.')[0])
        for s in student:
            await ctx.send(s)
        await ctx.send('================================================================')


@bot.slash_command(name='list_students', description='List the students in a class OR a teacher OR both.')
async def list_students(ctx, class_name: str = None, teacher: str = None):

    schedule = google_sheets.get_schedules()

    # Store all info here
    data = {}

    # "General Math", "General Science", etc.
    for field in schedule:

        # Variables
        students = []

        # If only class name is provided
        if class_name and not teacher:
            data[field] = {}

            # Each line in the field
            for item in schedule[field]:
                if not item: continue # If empty, skip
                
                subject = item['Subject']

                # If not the class, skip
                if subject.lower() != class_name.lower(): continue

                if subject not in data[field]:
                    data[field][subject] = []
                
                if item['Teacher'] not in [t['Teacher'] for t in data[field][subject]]:
                    students = []
                    data[field][subject].append({
                    'Day': item['Day'],
                    'Time': item['Start Time'] + " - " + item['End Time'],
                    'Teacher': item['Teacher'],
                    'Students': students
                })

                # Update students
                students.append(item['Student First Name'] + " " + item['Student Last Name'])

                data[field][subject][-1]['Students'] = students

        # If only teacher name is provided
        elif teacher and not class_name:
            data[field] = {}

            # Each line in the field
            for item in schedule[field]:
                # If empty, skip
                if not item: continue

                teacher_name = item['Teacher']

                if teacher_name.lower() != teacher.lower():
                    continue

                if item['Subject'] not in data[field]:
                    data[field][item['Subject']] = []
                    students = []

                    data[field][item['Subject']].append({
                    'Day': item['Day'],
                    'Time': item['Start Time'] + " - " + item['End Time'],
                    'Teacher': item['Teacher'],
                    'Students': students
                })

                # Update students
                students.append(item['Student First Name'] + " " + item['Student Last Name'])

                data[field][item['Subject']][-1]['Students'] = students

        # If both class and teacher is provided
        elif class_name and teacher:
            data[field] = {}

            for item in schedule[field]:
                if not item: continue # If empty, skip

                subject = item['Subject']
                teacher_name = item['Teacher']

                if subject.lower() != class_name.lower() or teacher_name.lower() != teacher.lower():
                    continue

                if item['Subject'] not in data[field]:
                    data[field][item['Subject']] = []
                    students = []

                    data[field][item['Subject']].append({
                    'Day': item['Day'],
                    'Time': item['Start Time'] + " - " + item['End Time'],
                    'Teacher': item['Teacher'],
                    'Students': students
                })

                # Update students
                students.append(item['Student First Name'] + " " + item['Student Last Name'])

                data[field][item['Subject']][-1]['Students'] = students

    # Output to Discord
    if teacher and class_name:
        await ctx.respond(f"# Information about {class_name} by {teacher.title()}.")
    elif teacher:
        await ctx.respond(f"# Information about {teacher.title()}.")
    elif class_name:
        await ctx.respond(f"# Information about {class_name}.")
    else:
        await ctx.respond(f"# Please provide a teacher or class name.")
    for field, subject in data.items():
        if not subject: continue

        await ctx.send(f"# {field}")
        for subject_name, classes in subject.items():
            if not classes: continue
            await ctx.send(f"## {subject_name}")
            for _class in classes:
                await ctx.send(f"- **__{_class['Teacher'].title()}__ ({_class['Day'].title()} {_class['Time'].upper()})**")
                for student in _class['Students']:
                    await ctx.send(f"᲼᲼᲼᲼∘ {student.title()}")
        

@bot.slash_command(name='send_reminder_to', description='Send Reminder to a specific student.')
@commands.has_role('VP')
async def send_reminder_to(ctx, fname, lname):
    student_name = (fname.strip() + ' ' + lname.strip()).title()
    schedule = google_sheets.get_schedules()
    sender_address = "academicempowermentproject@gmail.com"

    for field in schedule:
        for item in schedule[field]:
            if not item: continue
            current_name = (item['Student First Name'](
            ) + ' ' + item['Student Last Name']()).title()
            
            if student_name == current_name:
                await ctx.respond(send_class_reminders(item, sender_address))
                break


@bot.slash_command(name="links", description="Important AEP links!")
async def links(ctx):

    content = """
    [Hours Form](https://forms.gle/DWwMJmwYSMEcCjxp9)
    [Volunteer Handbook](https://docs.google.com/document/d/1Q3z9BfxmwWr4tAyUSLt_h1fcrgnkIy4kSKDiR6cDljM/edit?usp=sharing)
    [Teaching Times](https://docs.google.com/spreadsheets/d/17e00rMDT5PrvMZH2Bn8vm6RkfHi3sfdGD5WFxL5K48g/edit?usp=sharing)
    [Students List](https://docs.google.com/spreadsheets/d/191gADUNLcjJbURBXhWQ5r4v7qyecpAFVta8tZ-bCCK0/edit?usp=sharing)
    """

    embed = discord.Embed(
        title="Important AEP Links!",
        description=content,
        color=AEP_LOGO_BG_COLOR
    )
    await ctx.respond(embed=embed)


@bot.slash_command(name="hours", description="The number of hours someone has.")
async def hours(ctx, name):
    name = name.strip()
    hours = google_sheets.get_hours(name.lower())
    if hours:
        await ctx.respond(name.title() + " has " + hours + " hours!")
    else:
        await ctx.respond("Error")


@bot.slash_command(name="top_volunteers", description="The volunteers with the most hours.")
async def top_volunteers(ctx, top_number=3):
    try:
        top = google_sheets.get_top_volunteers(int(top_number))

    except Exception as e:
        await ctx.respond("Error")
        print(e)

    else:

        embed = discord.Embed(
            title=f"Top {top_number} Volunteers With The Most Hours",
            color=AEP_LOGO_BG_COLOR
        )

        count = 1
        for volunteer, hours in top:
            embed.add_field(name=f"{count}. {volunteer}",
                            value=f"{hours} Hours", inline=True)
            count += 1

        await ctx.respond(embed=embed)


bot.run(TOKEN)
