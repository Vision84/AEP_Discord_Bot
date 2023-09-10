import os
from discord.ext import commands
from dotenv import load_dotenv
from main import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# bot = commands.Bot(intents=discord.Intents.all())
bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:')
    bot_guilds = [g for g in [o.name for o in bot.guilds]]
    print(*bot_guilds, sep='\n')


@bot.slash_command(name='greet', description='Greets You!')
async def greet(ctx):
    await ctx.respond(f'Hello {ctx.author.display_name}!')


@bot.slash_command(name='send_reminders', description='Send Reminders to Students that have a class today.')
@commands.has_role('VP')
async def send_reminders(ctx):
    await ctx.respond("# Sending Reminders!")
    messages = main()

    for subject, student  in messages.items():
        await ctx.send('## ' + subject.split('.')[0])
        for s in student:
            await ctx.send(s)
        await ctx.send('================================================================')


@bot.slash_command(name='send_reminder_to', description='Send Reminder to a specific student.')
@commands.has_role('VP')
async def send_reminder_to(ctx, fname, lname):
    student_name = (fname.strip() + ' ' + lname.strip()).title()

    path = 'class_schedules/'
    # path = 'test/'
    files = os.listdir(path)

    for file in files:
        class_schedule = read_class_schedule(path, file)
        sender_address = "academicempowermentproject@gmail.com"

        for student in class_schedule:
            current_name = student['Student First Name'].title() + ' ' + student['Student Last Name'].title()
            current_name = current_name.title()
            if student_name == current_name:
                await ctx.respond(send_class_reminders(student, sender_address))


bot.run(TOKEN)