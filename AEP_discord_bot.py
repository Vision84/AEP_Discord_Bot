import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from main import *
from google_sheets import *

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
    # If only class name is provided
    if class_name and not teacher:
        for file in FILES:
            class_schedule = read_class_schedule(PATH, file)
            to_return = {}
            students = []
            current_teacher = ""
            flag = False
            for c in class_schedule:
                if c['Subject'].lower() != class_name.lower(): continue
                
                flag = True
                if current_teacher != c['Teacher']: students = []
                current_teacher = c['Teacher']

                d = {'Day': c['Day'], 'Time': c['Start Time'] + " - " + c['End Time'], 'Students': students}
                students.append(c['Student First Name'] + " " + c["Student Last Name"])
                to_return[c['Teacher']] = d

            if flag: break

        await ctx.respond("# " + class_name)
        for teacher_name, contents in to_return.items():
            await ctx.send("## " + teacher_name + " (" + contents['Day'] + " " + contents['Time'] + ")")
            for student in contents['Students']:
                await ctx.send("- " + student)
            
    # If only teacher name is provided
    elif teacher and not class_name:
        to_return = {}
        
        for file in FILES:
            class_schedule = read_class_schedule(PATH, file)
            current_subject = ""
            students = []
            for c in class_schedule:
                if c['Teacher'].lower() != teacher.lower(): continue

                if current_subject != c['Subject']: students = []
                current_subject = c['Subject']
                
                students.append(c['Student First Name'] + " " + c["Student Last Name"])
                d = {"Day": c['Day'], 'Time': c['Start Time'] + " - " + c['End Time'], 'Students': students}
                to_return[c['Subject']] = d

        await ctx.respond("# " + teacher)
        for subject, contents in to_return.items():
            await ctx.send("## " + subject + " (" + contents['Day'] + " " + contents['Time'] + ")")
            for student in contents['Students']:
                await ctx.send("- " + student)

    # If both class and teacher is provided
    elif class_name and teacher:
        for file in FILES:
            class_schedule = read_class_schedule(PATH, file)
            to_return = {}
            students = []
            flag = False

            for c in class_schedule:
                if c['Subject'].lower() != class_name.lower() or c['Teacher'].lower() != teacher.lower(): continue

                flag = True

                to_return['Day'] = c['Day']
                to_return['Time'] = c['Start Time'] + " - " + c['End Time']

                students.append(c['Student First Name'] + " " + c["Student Last Name"])
                to_return['Students'] = students

            if flag: break

        await ctx.respond("# " + class_name + " by " + teacher)
        await ctx.send("## Day: " + to_return['Day'])
        await ctx.send("## Time: " + to_return['Time'])
        for student in to_return['Students']:
            await ctx.send("- " + student)

    # If none
    else:
        ctx.respond("Provide a class name or a teacher's name or both.")


@bot.slash_command(name='send_reminder_to', description='Send Reminder to a specific student.')
@commands.has_role('VP')
async def send_reminder_to(ctx, fname, lname):
    student_name = (fname.strip() + ' ' + lname.strip()).title()

    for file in FILES:
        class_schedule = read_class_schedule(PATH, file)
        sender_address = "academicempowermentproject@gmail.com"

        for student in class_schedule:
            current_name = student['Student First Name'].title() + ' ' + student['Student Last Name'].title()
            current_name = current_name.title()
            if student_name == current_name:
                await ctx.respond(send_class_reminders(student, sender_address))


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
    hours = get_hours(name.lower())
    if hours:
        await ctx.respond(name.title() + " has " + hours + " hours!")
    else:
        await ctx.respond("Error")

bot.run(TOKEN)