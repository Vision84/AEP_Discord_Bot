import os
from tabulate import tabulate
import discord
from discord.ext import commands
from dotenv import load_dotenv
from main import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDS = os.getenv('DISCORD_GUILDS').split(',')

bot = commands.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} is connected to the following guilds:')
    bot_guilds = [g for g in [o.name for o in bot.guilds]]
    for guild in GUILDS:
        if guild in bot_guilds:
            print(f'{guild}')


@bot.slash_command(name='greet', description='Greets You!')
async def greet(ctx):
    await ctx.respond(f'Hello {ctx.author.display_name}!')


@bot.slash_command(name='send_reminders', description='Send Reminders to Students that have a class today.')
async def send_reminders(ctx):
    await ctx.respond("Sending Reminders!")
    messages = main()
    messages = [{1: '1,2,3,44,5,5,6'}, {2: '11,12,13,144,15,15,16'}]
    table = tabulate(messages, headers='keys', tablefmt='heavy_grid', stralign='center')
    print(table)

    for line in table.splitlines():
     await ctx.send(line)

    # for subject, student  in messages.items():
    #     await ctx.send(subject)
    #     await ctx.send(student)
    #     await ctx.send('================================================================')


# @bot.slash_command(name='send_reminder_to', description='Send Reminder to a specific student.')

# async def send_reminder_to(ctx, student_fname, student_lname):
#     student_name = (student_fname.strip() + ' ' + student_lname.strip()).title()
#     class_schedule = read_class_schedule("main.csv")
#     sender_address = "academicempowermentproject@gmail.com"

#     for student in class_schedule:
#         current_name = student['First Name'] + ' ' + student['Last Name']
#         current_name = current_name.title()
#         if student_name == current_name:
#             await ctx.send(send_class_reminders(student, sender_address))
#             return


bot.run(TOKEN)