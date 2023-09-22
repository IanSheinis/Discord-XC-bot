import typing
from typing import Any, Coroutine
import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import pytz
import retrieval


#utc converter
def get_utc_time_for_local_hour(hour: int, minute: int, second: int, tz_name: str) -> datetime.time:
     #Convert local time wanted to utc time
     local_tz = pytz.timezone(tz_name)
     now = datetime.datetime.now(tz=local_tz)
     local_time = local_tz.localize(datetime.datetime(now.year, now.month, now.day, hour, minute, second))
     utc_time = local_time.astimezone(pytz.utc)
     return utc_time.time()


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


'''#Select weekday
class SelectWeekday(discord.ui.View):
     @discord.ui.select(
          placeholder="Select Weekday",
          max_values=7,
          options=[
               discord.SelectOption(label="Monday",value="0"),
               discord.SelectOption(label="Tuesday",value="1"),
               discord.SelectOption(label="Wednesday",value="2"),
               discord.SelectOption(label="Thursday",value="3"),
               discord.SelectOption(label="Friday",value="4"),
               discord.SelectOption(label="Saturday",value="5"),
               discord.SelectOption(label="Sunday",value="6"),
          ]
     )
     async def selectWeekday(self, interactions: discord.Interaction, select_item:discord.ui.Select):
          self.answer = select_item.values
          self.children[0].disabled = True
          await interactions.message.edit(view=self)
          await interactions.response.defer()
          self.stop()'''

#Select option
'''class SelectWeekday(discord.ui.Select):
     def __init__(self):
          placeholder = "Select weekday..."
          options=[
               discord.SelectOption(label="Monday",value="0"),
               discord.SelectOption(label="Tuesday",value="1"),
               discord.SelectOption(label="Wednesday",value="2"),
               discord.SelectOption(label="Thursday",value="3"),
               discord.SelectOption(label="Friday",value="4"),
               discord.SelectOption(label="Saturday",value="5"),
               discord.SelectOption(label="Sunday",value="6"),
          ]
          super().__init__(placeholder=placeholder,options=options)'''

#Weekday modal
'''class ModalWeekday(discord.ui.Modal, title = "Change Daily Announcement"):
     
     weekday = SelectWeekday()
     announcement = discord.ui.TextInput(label="Monday", placeholder="Leave empty for no changes", style=discord.TextStyle.short, max_length= 200)
     

     async def on_submit(self, interactions:discord.Interaction):
          await interactions.response.send_message("Changed announcement/s",ephemeral=True)
          self.change = [self.weekday.value, self.announcement.value]
          await interactions.response.send_message(self.change)'''
'''class EnumWeekday(enum.Enum):
     Monday = 0
     Tuesday = 1
     Wednesday = 2
     Thursday = 3
     Friday = 4
     Saturday = 5
     Sunday = 6
     monday = 0
     tuesday = 1
     wednesday = 2
     thursday = 3
     friday = 4
     saturday = 5
     sunday = 6   ''' 




'''#Announcement group
class Announcement(app_commands.Group):
    pass
announcement = Announcement(name = "announcement",description="The daily announcement")'''


class CustomChannelIdError(Exception):
    
    """
    If channel id is not a real channel
    """

    pass


"""
Query data to Retrieval.data
"""
retrieval.Retrieval.retrieve("json/save.json")
prevData: dict = retrieval.Retrieval.data

class Calender(commands.Cog):


     
     #Check if daylight savings happened
     timeList = prevData["time1"].split(':')
     time1 = localize_time_wHour(int(timeList[0]),int(timeList[1]),int(timeList[2]),"US/Pacific")
     time1 = get_utc_time_for_local_hour(time1.hour,time1.minute,time1.second, "US/Pacific")


     def __init__(self, bot: commands.Bot
                 ) -> None:
          self.bot = bot
          self.WEEKDAYLIST = ["monday",
                              "tuesday",
                              "wednesday",
                              "thursday",
                              "friday",
                              "saturday",
                              "sunday"]
          self.announcements: list = prevData["announcements"]
          self.channelId: int = prevData["channelId"]

          #Is channelId a real id
          
          
          #Start tasks        
          self.dailyAnnouncement.start()



     #Cog unload
     def cog_unload(self) -> Coroutine[Any, Any, None]:
         self.announcements.stop()
         return super().cog_unload()


     #Save to json/save.json
     def save_data(self) -> None:
         timeToStr = self.time1.strftime("%H:%M:%S")
         dataDict = {
                    "time1":timeToStr,
                    "channelId":self.channelId,
                    "announcements":self.announcements
                    }
         retrieval.Retrieval.send("json/save.json", dataDict)
         

     #The daily announcement
     @tasks.loop(time = time1)
     async def dailyAnnouncement(self) -> None:
          date: datetime.date = datetime.date.today()
          if(self.announcements[date.weekday()]!=""):
               await self.bot.get_channel(self.channelId).send(self.announcements[date.weekday()])
          else:
              print(f"Nothing at {date}")
         

     #Set announcement time
     @app_commands.command(description="Set time of day for announcement")
     @app_commands.describe(hour = "The hour (MILITARY TIME)")
     @app_commands.describe(minute = "The minute")
     @app_commands.describe(second = "The second")
     async def announcement_set_time(self, interactions: discord.Interaction, hour: int, minute: int, second: int) -> None:
          timeFmt: str = f"{'0' if hour<10 else ''}{hour}:{'0' if minute<10 else ''}{minute}:{'0' if second<10 else ''}{second}"
          if(hour < 0 or 
          hour >24 or
          minute < 0 or
          minute > 60 or
          second < 0 or
          second > 60):
               await interactions.response.send_message(f"Time {timeFmt} is invalid", ephemeral=True)
          else:  
               time = get_utc_time_for_local_hour(hour,minute,second,"US/Pacific")
               self.time1 = time
               self.dailyAnnouncement.change_interval(time=time)
               await interactions.response.send_message(f"Changed to {timeFmt}",ephemeral=True)
               self.save_data()

 
     #Set_announcement autocomplete
     async def day_autocomplete(self, 
                               interaction: discord.Interaction,
                                current: str
                                ) -> typing.List[app_commands.Choice[str]]:
         listWeekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]  
         return[
              app_commands.Choice(name=d,value=d)
              for d in listWeekdays if current.lower() in d.lower()
         ]

     #Set announcement 
     @app_commands.command(description="Set announcement on given day")
     @app_commands.autocomplete(day = day_autocomplete)
     @app_commands.describe(day = "Enter a weekday",announcement = 'Enter the announcement, enter "None" to erase the announcement')
     @app_commands.rename(day = "weekday")
     async def announcement_set(self, interaction: discord.Interaction, day: str, announcement: str) -> None:
         if day.lower() not in self.WEEKDAYLIST:
             await interaction.response.send_message(f'"{day}" is not a day!', ephemeral=True)
         else:
             self.setterAnnouncement(day.lower(),announcement)
             await interaction.response.send_message("Message changed!",ephemeral=True)
       
     def setterAnnouncement(self, day: str, msg: str) -> None:
          if msg.lower() == "none":
             self.announcements[self.WEEKDAYLIST.index(day)] = ""
          else:
               self.announcements[self.WEEKDAYLIST.index(day)] = msg
          self.save_data()


     #Set channel
     @app_commands.command(description = "Select channel for daily announcement")
     @app_commands.describe(id = "id for channel, put 0 for this channel")
     async def set_announcement_channel(self, interaction: discord.Interaction, id: str) -> None:
          try:
              id = int(id)
          except ValueError:
              await interaction.response.send_message(f'"{id}" is not a valid channel id')
              return
          if(id == 0):
               self.setter_channel(interaction.channel.id)
               await interaction.response.send_message("Channel id changed to this channel!", ephemeral=True)
          else:
               channel = self.bot.get_channel(id)
               if channel is None:
                    await interaction.response.send_message("Could not find channel\n*Note that I can only find channels within this server*", ephemeral=True)
               else:
                    self.setter_channel(id)
                    await interaction.response.send_message(f'Channel id changed to "{id}"!', ephemeral=True)
                   
     def setter_channel(self, id: int) -> None:
         self.channelId = id
         self.save_data()


     #Return Weekday Embed 
     @app_commands.command(description="Creates a list of weekday announcements")
     async def announcement_show(self, interactions: discord.Interaction) -> None:
         
         #Format time1
         localTime = (localize_time(self.time1,"US/Pacific"))
         fmtTime = localTime.strftime("%H:%M:%S")

         embed = discord.Embed(colour=discord.Colour.green(),
                               title="**Weekday announcements**",
                               description=f"Scheduled for {fmtTime}")
         embed.add_field(name="*Monday*",
                         value=f"```{self.announcements[0]} ```",
                         inline=False)
         embed.add_field(name="*Tuesday*",
                         value=f"```{self.announcements[1]} ```",
                         inline=False)
         embed.add_field(name="*Wednesday*",
                         value=f"```{self.announcements[2]} ```",
                         inline=False)
         embed.add_field(name="*Thursday*",
                         value=f"```{self.announcements[3]} ```",
                         inline=False)
         embed.add_field(name="*Friday*",
                         value=f"```{self.announcements[4]} ```",
                         inline=False)
         embed.add_field(name="*Saturday*",
                         value=f"```{self.announcements[5]} ```",
                         inline=False)
         embed.add_field(name="*Sunday*",
                         value=f"```{self.announcements[6]} ```",
                         inline=False)
         embed.set_footer(text = f"Channel id: {self.channelId}")
         await interactions.response.send_message(embed=embed,ephemeral=True)     


     #Calender group
     @commands.group()
     async def Calender(self,ctx) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Input a command")

            
    #Return current time
     @Calender.command()
     async def returnCurrentTime(self,ctx) -> None:
        date: datetime.datetime = datetime.datetime.now(pytz.timezone("US/Pacific"))
        strDate: str = discord.utils.format_dt(date)
        await ctx.send(strDate)

    

    

    

  
async def setup(bot: commands.Bot) -> None:
     try:
          await bot.fetch_channel(prevData["channelId"])
     except discord.NotFound:
          raise CustomChannelIdError
     await bot.add_cog(Calender(bot))