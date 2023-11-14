import typing
from typing import Any, Coroutine, Literal
import discord
from discord.ext import commands, tasks
from discord import app_commands
import settings
import datetime
import pytz
import retrieval


logger = settings.logging.getLogger("bot")
"""
Query data to Retrieval.data
"""

#Convert seperated ints to string stime
def change_to_time_string(hour: int, minute: int, second: int):
     return f"{'0' if hour<10 else ''}{hour}:{'0' if minute<10 else ''}{minute}:{'0' if second<10 else ''}{second}"

#utc converter
def get_utc_time_for_local_hour(hour: int, minute: int, second: int, tz_name: str) -> datetime.time:
     #Convert local time wanted to utc time
     local_tz = pytz.timezone(tz_name)
     now = datetime.datetime.now(tz=local_tz)
     local_time = local_tz.localize(datetime.datetime(now.year, now.month, now.day, hour, minute, second))
     utc_time = local_time.astimezone(pytz.utc)
     return utc_time.time()

def get_utc_time_for_local_datetime(date: datetime.datetime, tz_name: str) -> datetime.time:
     #Convert local time wanted to utc time
     local_tz = pytz.timezone(tz_name)
     now = datetime.datetime.now(tz=local_tz)
     local_time = local_tz.localize(date)
     utc_time = local_time.astimezone(pytz.utc)
     return utc_time


#Localize w/ datetime
def localize_time(date: datetime.time, tz_name: str) -> datetime.time:
     local_tz = pytz.timezone(tz_name)
     now = datetime.datetime.now()
     aware_datetime = pytz.utc.localize(datetime.datetime(now.year, now.month, now.day, date.hour, date.minute, date.second))
     changed_time = aware_datetime.astimezone(local_tz)
     return changed_time.time()

#localize with hour
def localize_time_wHour(hour:int, minute:int, second:int, tz_name: str) -> datetime.time:
     local_tz = pytz.timezone(tz_name)
     now = datetime.datetime.now()
     aware_datetime = pytz.utc.localize(datetime.datetime(now.year, now.month, now.day, hour, minute, second))
     changed_time = aware_datetime.astimezone(local_tz)
     return changed_time.time()

#Localize w/ datetime returning datetime
def localize_datetime(date: datetime.datetime, tz_name: str) -> datetime.datetime:
     local_tz = pytz.timezone(tz_name)
     aware_datetime = pytz.utc.localize(datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second))
     changed_time = aware_datetime.astimezone(local_tz)
     return changed_time

#Check to see if owner or allowed to send msg
def is_allowed(interaction: discord.Interaction):
     user_id = interaction.user.id
     if user_id == interaction.guild.owner_id:
          return True
     if user_id in settings.allowed_users:
          return True
     #Leader role
     for r in interaction.user.roles:
          if r.id == 1110951519194468363:
               return True
     
     return False


class Calender(commands.Cog):


     def __init__(self, bot: commands.Bot
                 ) -> None:
          self.bot = bot
          self.MONTHLIST = ["January","Febuary","March","April","May","June","July","August","September","October","November","December"]
          self.remindLoop.start()
          

     #Cog unload
     def cog_unload(self) -> Coroutine[Any, Any, None]:
         self.announcements.stop()
         return super().cog_unload()

     #Log send to
     async def sendRemind(self,msgTuple: tuple):
          """
          Queries from sql table and sends reminder
          """
          msg: str = msgTuple[6]
          #DM
          if(msgTuple[1]!=0):
               user: discord.User = await self.bot.fetch_user(msgTuple[3])
               await user.send(msg)
               logger.info(f"Sending to user {user.name}, {msgTuple}")
          #CHANNEL
          else:
               channel = await self.bot.fetch_channel(msgTuple[2])
               await channel.send(msg)
               logger.info(f"Sending to channel {channel.name}, {msgTuple}")

     def repeatRemind(self,msgTuple: tuple):
          """
          Adds time to date int for next reminder
          """
          repeat = msgTuple[5]
          if(repeat!=0):
               repeatTuple = (msgTuple[1],msgTuple[2],msgTuple[3],msgTuple[4]+repeat,msgTuple[5],msgTuple[6])


               retrieval.Retrieval.insert(repeatTuple)
     #Maybe stop the loop all together and then changetime and put it back, (what original set time does)
     # def changeTime(self):
     #      msgList = retrieval.Retrieval.querySoon()
     #      if msgList:
     #           date : datetime.datetime = datetime.datetime.fromtimestamp(msgList[0][4])
     #           time : datetime.time = date.time()
     #           self.remindLoop.change_interval(time=time)
     #           logger.info(f"Time changed to {time}")
     #      else:
     #           self.remindLoop.cancel()
     #           logger.info("Stopped loop")
     def isTime(self) -> bool:
          """
          Check if reminder is right time
          """
          msgList = retrieval.Retrieval.querySoon()
          if msgList:
               reminder_utc_date = datetime.datetime.fromtimestamp(msgList[0][4],pytz.timezone("US/Pacific"))
               reminder_int = msgList[0][4]
               dt = datetime.datetime.now(pytz.utc) 
               utc_time = dt.replace(tzinfo=pytz.utc) 
               utc_timestamp = utc_time.timestamp()
               daylight_datetime: datetime.datetime = localize_datetime(reminder_utc_date,"US/Pacific")
               #daylight
               if daylight_datetime.dst() == datetime.timedelta(hours = 0):
                    reminder_int-=3600
               #Adjust to utc timestamp
               reminder_int-=3600*7

               if(reminder_int<=utc_timestamp):
                    logger.info(f"Sending at {reminder_utc_date}")
                    return True
          return False



     @tasks.loop(minutes=1)
     async def remindLoop(self) -> None:
          """
          Loop to send reminder
          """
          if not self.isTime():
               return
          msgList: list = retrieval.Retrieval.querySoon()
          for tup in msgList:
               await self.sendRemind(tup)
               self.repeatRemind(tup)
               retrieval.Retrieval.delete(tup[0])
          
          

     async def month_autocomplete(self, 
                               interaction: discord.Interaction,
                                current: str
                                ) -> typing.List[app_commands.Choice[str]]:
         return[
              app_commands.Choice(name=m,value=m)
              for m in self.MONTHLIST if current.lower() in m.lower()
         ]

     #Set announcement 
     @app_commands.autocomplete(month = month_autocomplete)
     @app_commands.command(description="Set a reminder")
     @app_commands.describe(id = "Channel id, input 0: This channel, input 1: DM")
     @app_commands.describe(hour = "The hour (MILITARY TIME)")
     @app_commands.describe(minute = "The minute, leave blank for 0")
     @app_commands.describe(month = "Enter a month")
     @app_commands.describe(day = "Enter a day of the month")
     @app_commands.describe(msg = 'Enter your message')
     @app_commands.describe(repeat_days = "Repeats every _ days, leave blank for no repeat")
     @app_commands.describe(repeat_hours = "Repeats after _ hours (Plus days), leave blank for no repeat")
     @app_commands.rename(msg = "message")
     @app_commands.check(is_allowed)
     async def reminder_set(self, interaction: discord.Interaction, id:str, hour:int, month: str, day: int, msg: str, minute:int = 0, repeat_days: int = 0, repeat_hours: int = 0) -> None:
          """
          COMMAND TO LET USER EASILY INSERT REMINDER INTO SQLTABLE  
          """
          #AUTOMATE YEAR
          int_month = self.MONTHLIST.index(month)+1
          date_now = datetime.datetime.now()
          now_month = date_now.month
          if(now_month<=int_month):
               year = 2023
          else:
               year = 2024
          #REPEATS EVERY ? SECONDS
          repeat = repeat_days*86400 + repeat_hours*3600
          dm=False
          #ASSERT YEAR IS APPROPIATE
          if(year>2024):
               await interaction.response.send_message(f"Year {year} is too big",ephemeral=True)
               return
          #ASSERT IF DATE IS VALID
          try:
               input_datetime = datetime.datetime(year,int_month,day,hour,minute,0)
               reminder_date = get_utc_time_for_local_datetime(input_datetime,tz_name="US/Pacific")
          except:
               await interaction.response.send_message(f'Something went wrong!\nDate "{month}/{day}/{year}, {hour}:{minute}:00" does not exist',ephemeral=True)
               return
          #TO TEST W/ UTC TIMESTAMP AND FOR EASY STRFTIME
          fmtTime = input_datetime.strftime(f"%m/%d/%Y, %H:%M:%S")
          reminder_date_int : int = reminder_date.timestamp()
          #CHECK FOR DAYLIGHT
          daylight_datetime: datetime.datetime = localize_datetime(reminder_date,"US/Pacific")

          if daylight_datetime.dst() == datetime.timedelta(hours = 1):
               reminder_date_int-=3600
          #Adjust time for timezone
          reminder_date_int+= 3600*8
          #IF DATE OF REMINDER ALREADY HAPPENED
          dt = datetime.datetime.now(pytz.utc) 
          utc_time = dt.replace(tzinfo=pytz.utc) 
          utc_timestamp = utc_time.timestamp()
          timestampTest = input_datetime.timestamp()
          if(timestampTest<=utc_timestamp+10):
               await interaction.response.send_message(f'Date "{fmtTime}" already happened!',ephemeral=True)
               return
          #MAKE CHANNEL
          try:
               id = int(id)
          except:
               await interaction.response.send_message(f"{id} is not a valid id",ephemeral=True)
               return
          if(id==1):
               dm = True
               msg_tuple = (1,None,interaction.user.id,reminder_date_int,repeat,msg)
          else:
               #Check for perms
               if not is_allowed(interaction):
                    await interaction.response.send_message("You do not have perms to use this command\n*Can stil use dm feature*",ephemeral=True)
                    return
               #Current channel
               if(id==0):
                    id = interaction.channel.id
               else:
                    channel = self.bot.get_channel(id)
                    if channel is None:
                         await interaction.response.send_message("Could not find channel\n*Note that I can only find channels within this server*", ephemeral=True)
                         return
               channel = self.bot.get_channel(id)
               msg_tuple = (0,id,None,reminder_date_int,repeat,msg)


          retrieval.Retrieval.insert(msg_tuple)

          

          #Embed to send
          embed = discord.Embed(colour=discord.Colour.dark_gold(),
                               title="**Reminder set!**",
                               description=f"Scheduled for {discord.utils.format_dt(input_datetime)}")
          #Show message
          embed.add_field(name="*Message:*",
                         value=f"```{msg} ```",
                         inline=False)
          #Show repeat
          if(repeat!=0):
               embed.add_field(name="*Repeats:*",
                              value=f"Every {int(repeat/86400)} days, {int(repeat%86400)/3600} hours",
                              inline=False)
          else:
               embed.add_field(name="*Repeats:*",
                              value=f"No",
                              inline=False)
          #Set footer for sending destination
          if(dm):
               embed.set_footer(text=f'Sending as a dm')
          else:
               embed.set_footer(text=f'Sending to channel "{channel.name}"')

          await interaction.response.send_message(embed=embed,ephemeral=True)

          logger.info(f"User {interaction.user.name} input {msg_tuple}")

          # if not self.remindLoop.is_running():
          #      self.remindLoop.start()
          #      logger.info(f"Started loop at {fmtTime}")

     @app_commands.command(description="Returns all reminders")
     async def all_reminders(self, interaction:discord.Interaction):
          queriedList = retrieval.Retrieval.queryAllDate()
          await interaction.response.send_message(await self.fmtReminder(queriedList),ephemeral=True)

     @app_commands.command(description="Returns all of your dm reminders")
     async def dm_reminders(self,interaction:discord.Interaction):
          queriedList = retrieval.Retrieval.queryAllDateDM(interaction.user.id)
          await interaction.response.send_message(await self.fmtReminder(queriedList),ephemeral=True)
          
     @app_commands.command(description="Delete chosen reminder")
     async def delete_reminder(self,interaction: discord.Interaction, id: int):
          retrieval.Retrieval.delete(id)
          await interaction.response.send_message(f"Deleted ID {id}",ephemeral=True)


     async def fmtReminder(self,msgList : list) -> str:
          """
          Formats tuples to user friendly str
          Insert tuple with rowid
          """
          result: list = []
          for msgTuple in msgList:
               assert (len(msgTuple) == 8 and msgTuple[4]==msgTuple[7]) or len(msgTuple)==7
               reminder_utc_date = datetime.datetime.fromtimestamp(msgTuple[4],pytz.timezone("US/Pacific"))
               reminder_date = localize_datetime(reminder_utc_date,"US/Pacific")
               #REPEATS
               if(msgTuple[5]!=0):
                    repeat = f"Repeats every {int(int(msgTuple[5])/86400)} days, {int(int(msgTuple[5])%86400)/3600} hours"
               else:
                    repeat = "Does not repeat"
               #DM TEST
               if(msgTuple[1]==1):
                    result.append( f'{discord.utils.format_dt(reminder_date)}: DM "{msgTuple[6]}", ID {msgTuple[0]} {repeat} ')
               else:
                    try:
                         channel = await self.bot.fetch_channel(int(msgTuple[2]))
                         channel = channel.name
                    except:
                         channel = "Unknown"
                    result.append(f'{discord.utils.format_dt(reminder_date)}: Channel "{channel}", Message: "{msgTuple[6]}", ID: {msgTuple[0]}, {repeat}')
          return "\n".join(result)
          

     #Calender group
     @commands.group()
     async def Calender(self,ctx) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Input a command")

     #Return next time
     @Calender.command()
     async def nextInterval(self,ctx) -> None:
          await ctx.send(self.remindLoop.next_iteration)

     #Return current time
     @Calender.command()
     async def returnCurrentTime(self,ctx) -> None:
        date: datetime.datetime = datetime.datetime.now(pytz.timezone("US/Pacific"))
        strDate: str = discord.utils.format_dt(date)
        await ctx.send(strDate)

     @Calender.command()
     async def input(self,ctx) -> None:
          date: datetime.datetime = datetime.datetime.now(pytz.UTC)
          #CHANGE MESSAGE CONTENT
          msgTuple: tuple = (0,ctx.channel.id,None,date.timestamp(),ctx.message.content)
          #Only accepts lists of tuples
          msgList: list = [msgTuple]
          retrieval.Retrieval.insert(msgList)
          
          await ctx.send(", ".join(map(str,msgTuple)))

     @Calender.command()
     async def testRemind(self,ctx) -> None:
          dt = datetime.datetime.now(pytz.utc) 
          utc_time = dt.replace(tzinfo=pytz.utc) 
          utc_timestamp = utc_time.timestamp()
          await ctx.send(dt)

     @Calender.command()
     async def querySoon(self,ctx) -> None:
          queriedList = retrieval.Retrieval.querySoon()
          await ctx.send(queriedList)



     



    

    

    

  
async def setup(bot: commands.Bot) -> None:
     await bot.add_cog(Calender(bot))