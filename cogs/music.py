import discord, asyncio,  config, os, random
import google_auth_oauthlib.flow, googleapiclient.errors, googleapiclient.discovery
from youtube_dl import YoutubeDL
from discord.ext import commands
import discord.utils

# ------------------------------------------

YDL_CONFIG = YoutubeDL(config.YDL_CONFIG)
FFMPEG_CONFIG = config.FFMPEG_CONFIG
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# -- some features for YouTube API --

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "..\\secret.json"

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
        if str(url).startswith("https://www.youtube.com") or str(url).startswith("https://youtu.be"):
            return url

        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=url
        )
        return ("https://www.youtube.com/watch?v=" + request.execute()["items"][0]["id"]["videoId"])
        
    @classmethod 
    async def from_url(cls, url, *, loop=None):
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
        else:
            voice_channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await voice_channel.connect()
            else:
                await ctx.voice_client.move_to(voice_channel)

# -- func to play music from Youtube --
    @commands.command(name='yt', help='To play song from YouTube', aliases=['youtube'])
    async def yt(self, ctx, *, url):   
        if ctx.voice_client is None or ctx.voice_client != ctx.message.guild.voice_client:
            await Music.join(self, ctx)
        
        voice_client = ctx.message.guild.voice_client    
        audio = await YTDLSource.from_url(url)

        if not voice_client.is_playing():
            async with ctx.typing():
                Music.yt_play(self, ctx, audio, voice_client)
                await ctx.send(f"ok, cutie Owu\nI'll play it for u <3.")
        else:
            self.queue.append(audio)
            await ctx.send(f"ok, I'll add it to queue")
    
    def yt_play(self, ctx, audio, voice_client):
        voice_client.play(discord.FFmpegPCMAudio(audio, 
            **FFMPEG_CONFIG), after=lambda e: Music.queue(self, ctx, voice_client))

    def queue(self, ctx, voice_client):  # just a queue-logic  
        # BUG: works strange. Sometimes even doesen't works. I really don't know why, but I need to fix it.
        if len(self.queue) >= 1:
            audio = self.queue.pop(0)
            Music.yt_play(self, ctx, audio, voice_client)

    @commands.command()
    async def shuffle(self, ctx):
        self.queue = random.shuffle(self.queue)
        await ctx.send("Shuffled!")

    @commands.command()
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            if len(self.queue) >= 0: 
                del self.queue[0]
                Music.yt_play(self, ctx, voice_client)
                await ctx.send("Skipping track...")
                print("Skipping track...")
        else:
            await ctx.send("I'm not playing rn, don't u hear?")

    @commands.command()
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            voice_client.disconnect()
        else:
            await ctx.send("Goodbye!")

    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Paused!")
        else:
            await ctx.send("I'm not playing rn, don't u hear?")

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Resumed!")
        else:
            await ctx.send("I'm not playing anything before. Use yt or vk command. Or take ur pills")

    @commands.command()
    async def stop(self, ctx):
        self.queue = []
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Stoped")
        else:
            await ctx.send("I can't stop doing what I'm not doing.")
    
# ------------------------------------------
async def setup(bot):
    await bot.add_cog(Music(bot))
