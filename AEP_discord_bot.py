import os
from discord.ext import commands
from dotenv import load_dotenv
from main import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# bot = commands.Bot(intents=discord.Intents.all())
bot = commands.Bot()

path = 'class_schedules/'
# path = 'test/'
files = os.listdir(path)

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


@bot.slash_command(name='list_students', description='List the students in a class OR a teacher.')
async def list_students(ctx, class_name: str = None, teacher: str = None):
    
    # If only class name is provided
    if class_name and not teacher:
        for file in files:
            class_schedule = read_class_schedule(path, file)
            list_to_return = {}
            students = []
            current_teacher = ""
            flag = False
            for c in class_schedule:
                if c['Subject'] != class_name: continue
                
                flag = True
                if current_teacher != c['Teacher']: students = []
                current_teacher = c['Teacher']

                d = {'Day': c['Day'], 'Time': c['Start Time'] + " - " + c['End Time'], 'Students': students}
                students.append(c['Student First Name'] + " " + c["Student Last Name"])
                list_to_return[c['Teacher']] = d

            if flag: break
            
        await ctx.respond("# " + class_name)
        for teacher_name, contents in list_to_return.items():
            await ctx.send("## " + teacher_name + " (" + contents['Day'] + " " + contents['Time'] + ")")
            for student in contents['Students']:
                await ctx.send("- " + student)
            




@bot.slash_command(name='send_reminder_to', description='Send Reminder to a specific student.')
@commands.has_role('VP')
async def send_reminder_to(ctx, fname, lname):
    student_name = (fname.strip() + ' ' + lname.strip()).title()

    for file in files:
        class_schedule = read_class_schedule(path, file)
        sender_address = "academicempowermentproject@gmail.com"

        for student in class_schedule:
            current_name = student['Student First Name'].title() + ' ' + student['Student Last Name'].title()
            current_name = current_name.title()
            if student_name == current_name:
                await ctx.respond(send_class_reminders(student, sender_address))


bot.run(TOKEN)