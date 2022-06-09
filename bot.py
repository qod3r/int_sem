import pickle
import os
from discord.ext import commands
from apikeys import BOT_TOKEN, CLIENT_ID, CLIENT_SECRET, API_KEY
from osswrapper import Api

bot = commands.Bot(command_prefix='o ')
api = Api({"client_id": CLIENT_ID,
           "client_secret": CLIENT_SECRET,
           "api_key": API_KEY})

if os.path.isfile('./users.pkl'):
    with open('users.pkl', 'rb') as f:
        usernames = pickle.load(f)
else:
    usernames = {}
    

def parse(ctx, args):
    if len(args) == 0:
        # o t
        if ctx.author.id in usernames:
            user = usernames[ctx.author.id]
        else:
            user = None
        index = None
    elif len(args) == 1:
        # o t \10
        if "\\" in args[0]:
            if ctx.author.id in usernames:
                user = usernames[ctx.author.id]
            else:
                user = None
            index = int(args[0][1:])
        # o t qod3r
        else:
            user = args[0]
            index = None
    else:
        # o t qod3r \10
        user, index = args
        index = int(index[1:])
        
    return user, index


@bot.command(name='h')
async def help(ctx):
    await ctx.send(f'''
Usage: o <command> [arguments]
Commands:
    nick - set username
    
    u - show player info
        o u <name>
    
    t - show top scores (defaults to top 3)
        o t <username> \\<index>
        
    r - show recent score (defaults to last score)
        o r <username> \\<index>
''')

@bot.command(name='nick')
async def set_name(ctx, name):
    usernames[ctx.author.id] = name
    response = f"Set username {name}."
    with open('users.pkl', 'wb') as f:
        pickle.dump(usernames, f)
    await ctx.send(response)

@bot.command(name='u')
async def player_info(ctx, *args):
    user, _ = parse(ctx, args)
    if user is None:
        await ctx.send("Name not set!")
        return
    await ctx.send(api.player_info(user))

@bot.command(name='t')
async def top_plays(ctx, *args):
    user, index = parse(ctx, args)
    if user is None:
        await ctx.send("Name not set!")
        return
        
    text, thumb = api.top_plays(user, index)
    if thumb is None:
        thumb = ""
        
    await ctx.send(text + f"\n{thumb}")
    
@bot.command(name='r')
async def recent(ctx, *args):
    user, index = parse(ctx, args)
    if user is None:
        await ctx.send("Name not set!")
        return
    
    text, thumb = api.recent(user, index)
    if thumb is None:
        thumb = ""
    
    await ctx.send(text + f"\n{thumb}")


bot.run(BOT_TOKEN)
