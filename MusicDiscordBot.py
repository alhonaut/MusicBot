from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio
from discord.ext import commands
import googleapiclient.discovery
import isodate
import asyncio
import requests

service = 'youtube'
version = 'v3'
API = 'API'

YDL_OPT = {'format': 'bestaudio', 'noplaylist': 'True', 'force-ipv4': 'True', 'cachedir': 'False'}

FFMPEG_OPT = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

TOKEN = 'TOKEN'

list_of_songs = []
list_of_roles = ['@everyone']

bot = commands.Bot(command_prefix='#')


@bot.command()
async def play(ctx,  *, text):
    global voice
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    if not ctx.message.author.voice:
        await ctx.send('**Ви зараз не находитесь в голосовому каналі!**')
        return
    else:
        channel = ctx.message.author.voice.channel

    try:
        voice = await channel.connect()
    except:
        pass

    youtube = googleapiclient.discovery.build(service, version, developerKey=API)
    response = youtube.search().list(part='id,snippet',
                                     type='video',
                                     order='relevance',
                                     q=text,
                                     maxResults=1).execute()

    for info in response['items']:

        video = info['id']['videoId']
        dur = youtube.videos().list(part='contentDetails',
                                    id=video,
                                    fields='items(contentDetails(duration))').execute()

        url = 'https://www.youtube.com/watch?v=' + response['items'][0]['id']['videoId']
        if len(dur['items'][0]['contentDetails']['duration']) <= 8:
            durat = str(isodate.parse_duration(dur['items'][0]['contentDetails']['duration']))[2:]
        else:
            durat = isodate.parse_duration(dur['items'][0]['contentDetails']['duration'])

        title = response['items'][0]['snippet']['title'].replace('&quot;', '"').replace('&amp;', '&')
        channel = response['items'][0]['snippet']['channelTitle']
        await ctx.send(f':dizzy:`Пісня успішно добавлена в чергу!`:dizzy:\n'
                       f'**Назва відео :** {title}\n'
                       f'**Тривалість :** {durat}\n'
                       f'**Автор :** {channel}')

        if str(text).startswith('https:'):
            music = text
            list_of_songs.append([title, music])
        else:
            music = url
            list_of_songs.append([title, music])

        print(list_of_songs)

        if voice.is_paused():
            return

        try:
            while len(list_of_songs) > 0:
                with YoutubeDL(YDL_OPT) as ydl:
                    info = ydl.extract_info(list_of_songs[0][1], download=False)

                check = ''
                URL = info['url']
                try:
                    res = requests.get(str(URL), timeout=0.1)
                    check += str(res)
                except:
                    pass

                if check == '<Response [403]>':
                    await ctx.send('**Сталася якась помилка. Повторіть спробу ще раз!**:no_entry:')
                else:
                    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPT))

                while voice.is_playing() or voice.is_paused():
                    await asyncio.sleep(1)

                list_of_songs.pop(0)
        except Exception as exc:
            if str(exc) == 'pop from empty list' or str(exc) == 'Already playing audio.':
                pass
            else:
                print(exc)
                await ctx.send('**Сталася якась помилка. Повторіть спробу ще раз!**:no_entry:')


@bot.command()
async def list(ctx):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    if len(list_of_songs) == 0:
        await ctx.send('**На данний момент ви не включили ще ніякого відео!**')
    else:
        list_title = ''
        position = 1
        for title in list_of_songs:
            if position == 1:
                list_title += f'**{position})** {title[0]} **(зараз відтворюється)**\n'
            else:
                list_title += f'**{position})** {title[0]}\n'
            position += 1
        await ctx.send(list_title)

@bot.command()
async def skip(ctx):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    server = ctx.message.guild
    voice_channel = server.voice_client
    if not ctx.message.author.voice:
        await ctx.send('**Ви зараз не находитесь в голосовому каналі!**')
        return
    else:
        voice_channel.stop()
        await ctx.send(f'**Відео пропущено користувачем `{ctx.author}`**:next_track:')

@bot.command()
async def stop(ctx):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    server = ctx.message.guild
    voice_channel = server.voice_client
    if not ctx.message.author.voice:
        await ctx.send('**Ви зараз не находитесь в голосовому каналі!**')
        return
    else:
        if not voice_channel.is_playing():
            await ctx.send('**На данний момент відео вже поставлене на паузу!**')
        else:
            voice_channel.pause()
            await ctx.send(f'**Відео поставлено на паузу користувачем `{ctx.author}`**:pause_button:')

@bot.command()
async def resume(ctx):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    server = ctx.message.guild
    voice_channel = server.voice_client
    if not ctx.message.author.voice:
        await ctx.send('**Ви зараз не находитесь в голосовому каналі!**')
        return
    else:
        if voice_channel.is_playing():
            await ctx.send('**На данний момент відео не на паузі!**')
        else:
            voice_channel.resume()
            await ctx.send(f'**Відео знято з паузи користувачем `{ctx.author}`**:arrow_forward:')

@bot.command()
async def delete(ctx, number):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    if not ctx.message.author.voice:
        await ctx.send('**Ви зараз не находитесь в голосовому каналі!**')
        return
    else:
        if int(number) < 0 or int(number) > len(list_of_songs):
            await ctx.send('**Введіть правильне значення позиції!**')
        else:
            list_of_songs.pop(int(number) - 1)
            await ctx.send(f'**Відео по позиції `{number}` успішно вилучено із черги!**:page_with_curl:')

@bot.command()
async def info(ctx):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    await ctx.send(':grey_exclamation:`Список команд`:grey_exclamation:\n'
                   '#play - **проігрування відео.**\n'
                   '#skip - **пропустити відео в черзі.**\n'
                   '#stop - **поставити відео на паузу.**\n'
                   '#resume - **вилучити відео із паузи.**\n'
                   '#list - **дізнатись список відео в черзі.**\n'
                   '#delete - **видалити відео із списку по позиції.**\n'
                   '#disconnect - **відключити бота з голосового каналу.**')

@bot.command()
async def disconnect(ctx):
    member = ctx.author
    if list_of_roles[0] in str(member.roles):
        pass
    else:
        return

    await ctx.voice_client.disconnect()
    list_of_songs.clear()

@bot.command()
@commands.has_permissions(administrator=True)
async def Only(ctx, *, role):
    list_of_roles.pop(0)
    if role == 'remove':
        list_of_roles.append('@everyone')
    else:
        list_of_roles.append(role)
    await ctx.send(f'**Тепер тільки роль `{list_of_roles[0]}` може користуватись ботом!**')

bot.run(TOKEN)
