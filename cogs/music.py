import discord, asyncio,  config, os, random
import google_auth_oauthlib.flow, googleapiclient.errors, googleapiclient.discovery
from youtube_dl import YoutubeDL
from discord.ext import commands
from requests import get
import discord.utils

# ------------------------------------------

YDL_CONFIG = YoutubeDL(config.YDL_CONFIG)
FFMPEG_CONFIG = config.FFMPEG_CONFIG
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# -- some features for YouTube API --

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "secret.json"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# -- some other features for YouTube API --

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

# -- class to search and extract audio file from Youtube video --
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume) 
        self.data = data
        self.title = data.get('title')
        self.url = ""
    
    def search(url):   # will take audio from first video from request
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=url
        )
        return ("https://www.youtube.com/watch?v=" + request.execute()["items"][0]["id"]["videoId"])

    @classmethod 
    async def from_url(cls, url, *, loop=None):
        if not url.startswith("https://www.youtube.com/") or not url.startswith("https://youtu.be/"):
            url = YTDLSource.search(url)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: YDL_CONFIG.extract_info(url, download = False))
        if 'entries' in data:
            data = data['entries'][0]
        music = data['url'] 
        return music



# -- class to play music from youtube and vk (will be soon) --
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music cog is loaded Owu")



    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not in voice channel, moron")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)



# -- func to play music from Youtube --
    @commands.command()
    async def yt(self, ctx, *, url):   
        if ctx.voice_client is None or ctx.voice_client != ctx.message.guild.voice_client:
            await Music.join(self, ctx)
        
        
        voice_client = ctx.message.guild.voice_client    
        music_file = await YTDLSource.from_url(url)
        self.queue.append(music_file)

        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(self.queue[0], 
                **FFMPEG_CONFIG), after=lambda e: Music.queue(self, ctx, voice_client))

            await ctx.send("ok, cutie Owu\nI'll play it for u.")
        else:
            await ctx.send("ok, I'll add it to queue")



    def queue(self, ctx, voice_client):  # just a queue-logic 
        if len(self.queue) >= 1:
            if self.queue[0].startswith("https://www.youtube.com/") or self.queue[0].startswith("https://youtu.be/"):
                voice_client.play(discord.FFmpegPCMAudio(self.queue[0], **FFMPEG_CONFIG), 
                    after=lambda e: Music.queue(self, ctx, voice_client))
                self.queue = self.queue[1:]
                


    @commands.command()
    async def shuffle(self, ctx):
        self.queue = random.shuffle(self.queue)



    @commands.command()
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            if len(self.queue) >= 0: 
                self.queue = self.queue[1:]
                voice_client.play(discord.FFmpegPCMAudio(self.queue[0], 
                    **FFMPEG_CONFIG), after=lambda e: Music.queue(self, ctx, voice_client))
        else:
            await ctx.send("I'm not playing rn, don't u hear?")

    @commands.command()
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send()



    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("I'm not playing, u bastard.")
        

        
    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("I'm not playing anything before. Use yt or vk command. Or take ur pills")



    @commands.command()
    async def stop(self, ctx):
        self.queue = []
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("I'm not playing rn, don't u hear?")

# ------------------------------------------

async def setup(bot):
    await bot.add_cog(Music(bot))
