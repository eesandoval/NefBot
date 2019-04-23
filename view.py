'''
MIT License

Copyright (c) 2019 Enrique Sandoval

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import controller
import discord
from discord.ext.commands import Bot
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
from utils.config import Config
from utils.parsing import convert_ISO_date_to_string, convert_args_to_dict

channel = None
active_adventurer_messages = {}
active_wyrmprint_messages = {}
active_dragon_messages = {}
config = Config("config.ini")
client = Bot(command_prefix=config.command_start)


def start_discord_bot():
    client.run(config.token)


@client.command(name="exit",
                description="Shuts down the bot",
                brief="Shuts down the bot (authorized users only)",
                aliases=["shutdown", "quit", "close"],
                pass_context=True)
async def exit(context):
    if (config.authorized_ids == [] or
            context.message.author.id in config.authorized_ids):
        await client.say("Shutting down")
        await client.close()
    else:
        await client.say("User is not authorized to exit this bot")


@client.command(name="get_adventurer",
                description="Gets an adventurer with the given name",
                brief="Gets an adventurer using a case insensitive search",
                aliases=["adv", "adventurer", "a"],
                pass_context=True)
async def get_adventurer(context):
    name = handle_context(context)
    await client.send_typing(channel)
    await controller.process_adventurers(name)


@client.command(name="get_wyrmprint",
                description="Gets a wyrmprint with the given name",
                brief="Gets a wyrmprint using a case insensitive search",
                aliases=["wyr", "wyrmprint", "w"],
                pass_context=True)
async def get_wyrmprint(context):
    name = handle_context(context)
    await client.send_typing(channel)
    await controller.process_wyrmprint(name)


@client.command(name="get_dragon",
                description="Gets a dragon with the given name",
                brief="Gets a dragon using a case insensitive search",
                aliases=["dra", "dragon", "d"],
                pass_context=True)
async def get_dragon(context):
    name = handle_context(context)
    await client.send_typing(channel)
    await controller.process_dragon(name)


@client.command(name="query",
                description="Queries for anything",
                brief="Queries for any adventurer, print, or dragon",
                aliases=["que", "q"],
                pass_context=True)
async def query(context):
    message = handle_context(context)
    await client.send_typing(channel)
    await controller.query(convert_args_to_dict(message))


@client.command(name="update",
                description="Updates the bot's config",
                brief="Updates the bot's configurations",
                aliases=["u"],
                pass_context=True)
async def update(context):
    message = handle_context(context)
    config = Config("config.ini")
    await show_completed_update()


def handle_context(context):
    global channel
    channel = context.message.channel
    received_message = context.message.content.split()
    message_content = ""
    if len(received_message) > 1:
        message_content = (' '.join(received_message[1:])).strip()
    return message_content


@client.event
async def on_ready():
    if config.streaming:
        await client.change_presence(
            game=discord.Game(
                name=config.current_event, url=config.stream_URL, type=1))
    else:
        await client.change_presence(
            game=discord.Game(
                name=config.current_event))


@client.event
async def show_adventurer(adventurer, message=None):
    e = discord.Embed(title=adventurer.name + " - " + adventurer.title,
                      desc=adventurer.title)
    url_name = "%20".join(adventurer.name.split())
    sub_portrait_URL = "adventurers/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name="Unit Type",
                value=get_emoji_element(adventurer.elementtype) +
                get_emoji_weapon(adventurer.weapontype) +
                get_emoji_unit(adventurer.unittype),
                inline=True)
    e.add_field(name="Rarity", value=get_emoji_rarity(adventurer.rarity),
                inline=True)
    e.add_field(name="Max HP/Max STR",
                value="{0}/{1}".format(adventurer.maxhp, adventurer.maxstr),
                inline=True)
    e.add_field(name="Max Co-Op Ability", value=adventurer.maxcoop,
                inline=True)
    e.add_field(name="Defense", value=adventurer.defense,
                inline=True)
    e.add_field(name="Release Date",
                value=convert_ISO_date_to_string(adventurer.releasedate),
                inline=True)
    skill_format = "Skill: {0} [SP Cost: {1}] [Frame Time: {2}]"
    ability_format = "Ability: {0}"
    for skill in adventurer.skills:
        e.add_field(name=skill_format.format(skill.name, skill.spcost,
                                             skill.frametime),
                    value=skill.description,
                    inline=False)
    for ability in adventurer.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description,
                    inline=False)
    await show_or_edit_adventurer(e, adventurer, message)


@client.event
async def show_adventurer_not_found(name):
    await client.send_message(channel, "Adventurer {0} not found".format(name))


@client.event
async def show_wyrmprint(wyrmprint, message=None):
    e = discord.Embed(title=wyrmprint.name,
                      desc=wyrmprint.name)
    url_name = "%20".join(wyrmprint.name.split())
    sub_portrait_URL = "wyrmprints/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name="Rarity", value=get_emoji_rarity(wyrmprint.rarity),
                inline=True)
    e.add_field(name="Max HP/Max STR",
                value="{0}/{1}".format(wyrmprint.maxhp, wyrmprint.maxstr),
                inline=True)
    e.add_field(name="Release Date",
                value=convert_ISO_date_to_string(wyrmprint.releasedate),
                inline=True)
    ability_format = "Ability: {0}"
    for ability in wyrmprint.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description, inline=False)
    await show_or_edit_wyrmprint(e, wyrmprint, message)


@client.event
async def show_wyrmprint_not_found(name):
    await client.send_message(channel, "Wyrmprint {0} not found".format(name))


@client.event
async def show_dragon(dragon, message=None):
    e = discord.Embed(title=dragon.name, desc=dragon.name)
    url_name = "%20".join(dragon.name.split())
    sub_portrait_URL = "dragons/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name="Element", value=get_emoji_element(dragon.elementtype),
                inline=True)
    e.add_field(name="Rarity", value=get_emoji_rarity(dragon.rarity),
                inline=True)
    e.add_field(name="Max HP/Max STR",
                value="{0}/{1}".format(dragon.maxhp, dragon.maxstr),
                inline=True)
    e.add_field(name="Release Date",
                value=convert_ISO_date_to_string(dragon.releasedate),
                inline=True)
    skill_format = "Skill: {0}"
    ability_format = "Ability: {0}"
    for skill in dragon.skills:
        e.add_field(name=skill_format.format(skill.name),
                    value=skill.description, inline=False)
    for ability in dragon.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description, inline=False)
    await show_or_edit_dragon(e, dragon, message)


@client.event
async def show_dragon_not_found(name):
    await client.send_message(channel, "Dragon {0} not found".format(name))


@client.event
async def show_invalid_name():
    await client.send_message(channel, "Invalid/no name given")


@client.event
async def show_missing_criteria(missing_criteria):
    await client.send_message(channel,
                              "Missing criteria {0}".format(missing_criteria))


@client.event
async def show_no_results_found():
    await client.send_message(channel,
                              "No results found for the given criteria")


@client.event
async def show_unknown_criteria(criteria_name, criteria):
    await client.send_message(channel,
                              "Unknown criteria: name '{0}', value '{1}'"
                              .format(criteria_name, criteria))


@client.event
async def show_exception(message, trace_message):
    print(trace_message)
    await client.send_message(channel, message)


def get_emoji_element(elementtype):
    return config.element_emoji[elementtype]


def get_emoji_weapon(weapontype):
    return config.weapon_emoji[weapontype]


def get_emoji_unit(unittype):
    return config.unit_emoji[unittype]


def get_emoji_rarity(rarity):
    return config.rarity_emoji[rarity] * rarity


@client.event
async def on_reaction_add(reaction, user):
    if (reaction.message.id in active_adventurer_messages and
            reaction.emoji in config.adventurer_reactions and
            user != client.user):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        await controller.process_adventurers_reaction(
            reaction.emoji,
            active_adventurer_messages[reaction.message.id],
            reaction.message)

    elif (reaction.message.id in active_wyrmprint_messages and
            reaction.emoji in config.wyrmprint_reactions and
            user != client.user):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        await controller.process_wyrmprint_reaction(
            reaction.emoji,
            active_wyrmprint_messages[reaction.message.id],
            reaction.message)

    elif (reaction.message.id in active_dragon_messages and
            reaction.emoji in config.dragon_reactions and
            user != client.user):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        await controller.process_dragon_reaction(
            reaction.emoji,
            active_dragon_messages[reaction.message.id],
            reaction.message)


@client.event
async def show_adventurer_full(adventurer, message=None):
    e = discord.Embed(title=adventurer.name + " - " + adventurer.title,
                      desc=adventurer.title)
    url_name = "%20".join(adventurer.name.split())
    sub_URL = "adventurers/full/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_adventurer(e, adventurer, message)


@client.event
async def show_wyrmprint_full(wyrmprint, message=None):
    e = discord.Embed(title=wyrmprint.name, desc=wyrmprint.name)
    url_name = "%20".join(wyrmprint.name.split())
    sub_URL = "wyrmprints/full/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_wyrmprint(e, wyrmprint, message)


@client.event
async def show_dragon_full(dragon, message=None):
    e = discord.Embed(title=dragon.name, desc=dragon.name)
    url_name = "%20".join(dragon.name.split())
    sub_URL = "dragons/full/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_dragon(e, dragon, message)


@client.event
async def show_or_edit_adventurer(e, adventurer, message=None):
    if message is None:
        global active_adventurer_messages
        active_adventurer_messages = {}
        msg = await client.send_message(channel, embed=e)
        active_adventurer_messages[msg.id] = adventurer
        for emoji in config.adventurer_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_or_edit_wyrmprint(e, wyrmprint, message=None):
    if message is None:
        global active_wyrmprint_messages
        active_wyrmprint_messages = {}
        msg = await client.send_message(channel, embed=e)
        active_wyrmprint_messages[msg.id] = wyrmprint
        for emoji in config.wyrmprint_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_or_edit_dragon(e, dragon, message=None):
    if message is None:
        global active_dragon_messages
        active_dragon_messages = {}
        msg = await client.send_message(channel, embed=e)
        active_dragon_messages[msg.id] = dragon
        for emoji in config.dragon_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_completed_update():
    await client.send_message(channel, "Update complete")
