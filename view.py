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
import traceback
import asyncio
from discord.ext.commands import Bot
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
from models.weapon import Weapon
from models.events import Event
from utils.config import Config
from utils.parsing import convert_ISO_date_to_string, convert_args_to_dict

config = Config("config.ini")
channel = None
active_messages = {}
emoji_reactions = {"adv": config.adv_reactions, "wyr": config.wyr_reactions,
                   "dra": config.dra_reactions, "wep": config.wep_reactions}
client = Bot(command_prefix=config.command_start)


def start_discord_bot():
    client.run(config.token)


# region Reaction Processing
def process_adventurers_reaction(emoji, adv):
    if emoji == "\U0001F5BC":  # Full picture
        return create_dynamic_portrait_embed(adv, "adventurers/full")
    adv = controller.process_adventurer(adv.name, get_level(emoji))
    return create_adventurer_embed(adv)


def process_wyrmprint_reaction(emoji, wyr):
    if emoji == "\U0001F5BC":  # Full picture
        return create_dynamic_portrait_embed(wyr, "wyrmprints/full")
    elif emoji == "\U0001F3A8":  # Full base picture
        return create_dynamic_portrait_embed(wyr, "wyrmprints/base")
    wyr = controller.process_wyrmprint(wyr.name, get_level(emoji))
    return create_wyrmprint_embed(wyr)


def process_dragon_reaction(emoji, dra):
    if emoji == "\U0001F5BC":  # Full picture
        return create_dynamic_portrait_embed(dra, "dragons/full")
    dra = controller.process_dragon(dra.name, get_level(emoji))
    return create_dragon_embed(dra)


def process_weapon_reaction(emoji, wep):
    if emoji == "\U000023E9":  # Upgrades To
        return create_weapon_upgrades_to_embed(wep)
    elif emoji == "\U000023EA":  # Upgrades From
        return create_weapon_upgrades_from_embed(wep)
    wep = controller.process_weapon(wep.name, get_level(emoji))
    return create_weapon_embed(wep)


def get_level(emoji):
    levels = {"\U0001F508": 1, "\U0001F509": 2, "\U0001F50A": 3}
    if emoji not in levels:
        return 1
    return levels[emoji]


reaction_functions = {"adv": process_adventurers_reaction,
                      "wyr": process_wyrmprint_reaction,
                      "dra": process_dragon_reaction,
                      "wep": process_weapon_reaction}
# endregion


# region Discord Commands
@client.command(name="exit",
                description="Shuts down the bot",
                brief="Shuts down the bot (authorized users only)",
                aliases=["shutdown", "quit", "close"])
async def exit(ctx):
    ctx.typing()
    if (config.authorized_ids == [] or
            ctx.message.author.id in config.authorized_ids):
        await ctx.send("Shutting down")
        for _, msg in active_messages.items():
            await msg.clear_reactions()
        await client.close()
    else:
        await ctx.send("User is not authorized to exit this bot")


@client.command(name="get_adventurer",
                description='''
                Searches for an adventurer using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released adventurer is returned.
                ''',
                brief="Gets an adventurer using a case insensitive search",
                aliases=["adventurer", "adv", "a"])
async def get_adventurer(ctx, *, name):
    await _get_adventurer(ctx, name)


@client.event
async def _get_adventurer(ctx, name):
    try:
        adventurer = controller.process_adventurer(name)
        embed = create_adventurer_embed(adventurer)
        await display_embed(embed, "adv", adventurer, ctx)
    except Exception as e:
        await show_exception(ctx, e)


@client.command(name="get_wyrmprint",
                description='''
                Searches for a wyrmprint using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released wyrmprint is returned.
                ''',
                brief="Gets a wyrmprint using a case insensitive search",
                aliases=["wyrmprint", "wyr", "w"])
async def get_wyrmprint(ctx, *, name):
    await _get_wyrmprint(ctx, name)


@client.event
async def _get_wyrmprint(ctx, name):
    try:
        wyrmprint = controller.process_wyrmprint(name)
        embed = create_wyrmprint_embed(wyrmprint)
        await display_embed(embed, "wyr", wyrmprint, ctx)
    except Exception as e:
        await show_exception(ctx, e)


@client.command(name="get_dragon",
                description='''
                Searches for a dragon using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released dragon is returned.
                ''',
                brief="Gets a dragon using a case insensitive search",
                aliases=["dragon", "dra", "d"])
async def get_dragon(ctx, *, name):
    await _get_dragon(ctx, name)


@client.event
async def _get_dragon(ctx, name):
    try:
        dragon = controller.process_dragon(name)
        embed = create_dragon_embed(dragon)
        await display_embed(embed, "dra", dragon, ctx)
    except Exception as e:
        await show_exception(ctx, e)


@client.command(name="get_weapon",
                description='''
                Searches for a weapon using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released weapon is returned.
                ''',
                brief="Gets a weapon using a case insensitive search",
                aliases=["weapon", "wep"])
async def get_weapon(ctx, *, name):
    await _get_weapon(ctx, name)


@client.event
async def _get_weapon(ctx, name):
    try:
        weapon = controller.process_weapon(name)
        embed = create_weapon_embed(weapon)
        await display_embed(embed, "wep", weapon, ctx)
    except Exception as e:
        await show_exception(ctx, e)


@client.command(name="query",
                description='''
                Queries the database for adventurers, dragons, or
                wyrmprints with the given criteria. Criteria is set as
                pairs. See example below:
                {0}query type=adv ability="Burn Res +100%"
                '''.format(config.command_start),
                brief="Queries for any adventurer, print, or dragon",
                aliases=["que", "q"])
async def query(ctx, *, criteria):
    values = []
    channel = ctx.channel
    get_commands = {"Adventurer": _get_adventurer, "Dragon": _get_dragon,
                    "Wyrmprint": _get_wyrmprint, "Weapon": _get_weapon}

    def check(m):
        return (m.channel == channel and m.content.isdigit() and
                int(m.content) in values)
    try:
        unit_list = controller.query(convert_args_to_dict(criteria))
        values = [i for i in range(1, len(unit_list) + 1)]
        embed = create_unit_list_embed(unit_list)
        query_message = await ctx.send(embed=embed)
    except Exception as e:
        await show_exception(ctx, e)
    try:
        message = await client.wait_for("message", check=check, timeout=60.0)
        unit_type = unit_list[int(message.content) - 1][1]
        unit_name = unit_list[int(message.content) - 1][0]
        await message.delete()
        await query_message.delete()
        await get_commands[unit_type](ctx, unit_name)
    except asyncio.TimeoutError:
        await query_message.delete()


@client.command(name="update",
                description='''
                Resets the configuration and updates the bot using the
                new values set in the config.ini file
                ''',
                brief="Updates the bot's configurations",
                aliases=["u"])
async def update(ctx):
    global config
    if (not(config.authorized_updates) or
            config.authorized_ids == [] or
            ctx.message.author.id in config.authorized_ids):
        config = Config("config.ini")
        controller.handle_update(config.picture_server)
        await ctx.send("Update completed")
    else:
        await ctx.send("User is not authorized to update this bot")


@client.command(name="alias",
                description='''
                Creates, updates, and deletes aliases. Aliases are shorthand
                or alternative ways to search for items. If the second
                parameter of the aliased_name is not specified, this will
                delete the alias_text from the database. If this alias
                already exists, it will update the alias. The same alias
                may exist that refers to an adventurer, dragon, and print.
                ''',
                brief="Creates a new alias to search by")
async def alias(ctx, alias_text, aliased_name=None):
    try:
        alias_result = controller.handle_alias(alias_text, aliased_name)
        await ctx.send(alias_result)
    except Exception as e:
        await show_exception(ctx, e)


@client.command(name="events",
                description='''
                Shows the latest events that are happening in the game
                This includes the current showcase(s), void battles,
                raid/facility/defense events, and limited endeavors
                ''',
                brief="Shows the latest events currently happening")
async def events(ctx):
    current_events = controller.handle_current_events()
    embed = create_events_embed(current_events)
    await ctx.send(embed=embed)
# endregion


# region Client Events
@client.event
async def on_ready():
    activity = discord.Game(name=config.current_event)
    if config.streaming:
        activity = discord.Streaming(name=config.current_event,
                                     url=config.stream_URL)
    await client.change_presence(activity=activity)


@client.event
async def display_embed(embed, embed_type, dynamic, ctx=None, message=None):
    reaction_list = emoji_reactions[embed_type]

    def check(reaction, user):
        return user != client.user and reaction.message.id == message.id

    if message is None:
        message = await ctx.send(embed=embed)
        active_messages[message.id] = message
        for emoji in reaction_list:
            await message.add_reaction(emoji)
    else:
        await message.edit(embed=embed)
    try:
        reaction, user = await client.wait_for("reaction_add", timeout=60.0,
                                               check=check)
        await message.remove_reaction(reaction, user)
        embed = reaction_functions[embed_type](reaction.emoji, dynamic)
        await display_embed(embed, embed_type, dynamic, ctx, message)
    except asyncio.TimeoutError:
        await message.clear_reactions()
        del active_messages[message.id]


@client.event
async def show_exception(ctx, e):
    print(traceback.format_exc())
    await ctx.send(str(e))
# endregion


# region Embed Functions
def create_dynamic_portrait_embed(dynamic, url):
    url_name = "%20".join(dynamic.name.split())
    e = discord.Embed(title=dynamic.name, desc=dynamic.name,
                      url=config.gamepedia_url.format(url_name))
    sub_URL = "{0}/{1}.png".format(url, url_name)
    e.set_image(url=config.picture_server + sub_URL)
    return e


def create_adventurer_embed(adv):
    url_name = "%20".join(adv.name.split())
    e = discord.Embed(title=adv.name + " - " + adv.title,
                      desc=adv.title,
                      url=config.gamepedia_url.format(url_name),
                      color=get_color(adv.elementtype))
    sub_portrait_URL = "adventurers/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name=get_emoji_rarity(adv.rarity),
                value="**HP** {0}\n**STR** {1}\n**DEF** {2}\n**Co-Op** {3}"
                .format(adv.maxhp, adv.maxstr, adv.defense, adv.maxcoop),
                inline=True)
    e.add_field(name=get_emoji_element(adv.elementtype) +
                get_emoji_weapon(adv.weapontype) +
                get_emoji_unit(adv.unittype) +
                get_emoji_limited(adv.limited),
                value="**Released**\n{0}"
                .format(convert_ISO_date_to_string(adv.releasedate)),
                inline=True)
    skill_format = "Skill: {0} [SP Cost: {1}] [Frame Time: {2}]"
    ability_format = "Ability: {0}"
    for skill in adv.skills:
        e.add_field(name=skill_format.format(skill.name, skill.spcost,
                                             skill.frametime),
                    value=skill.description,
                    inline=False)
    for ability in adv.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description,
                    inline=False)
    return e


def create_wyrmprint_embed(wyr):
    url_name = "%20".join(wyr.name.split())
    e = discord.Embed(title=wyr.name,
                      desc=wyr.name,
                      url=config.gamepedia_url.format(url_name),
                      color=get_color(None))
    sub_portrait_URL = "wyrmprints/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name=get_emoji_rarity(wyr.rarity),
                value="**HP** {0}\n**STR** {1}"
                .format(wyr.maxhp, wyr.maxstr),
                inline=True)
    e.add_field(name=get_emoji_eldwater(wyr.rarity) +
                get_emoji_limited(wyr.limited),
                value="**Released**\n{0}"
                .format(convert_ISO_date_to_string(wyr.releasedate)),
                inline=True)
    ability_format = "Ability: {0}"
    for ability in wyr.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description, inline=False)
    return e


def create_dragon_embed(dra):
    url_name = "%20".join(dra.name.split())
    e = discord.Embed(title=dra.name,
                      desc=dra.name,
                      url=config.gamepedia_url.format(url_name),
                      color=get_color(dra.elementtype))
    sub_portrait_URL = "dragons/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name=get_emoji_rarity(dra.rarity),
                value="**HP** {0}\n**STR** {1}"
                .format(dra.maxhp, dra.maxstr),
                inline=True)
    e.add_field(name=get_emoji_element(dra.elementtype) +
                get_emoji_limited(dra.limited),
                value="**Released**\n{0}"
                .format(convert_ISO_date_to_string(dra.releasedate)),
                inline=True)
    skill_format = "Skill: {0}"
    ability_format = "Ability: {0}"
    for skill in dra.skills:
        e.add_field(name=skill_format.format(skill.name),
                    value=skill.description, inline=False)
    for ability in dra.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description, inline=False)
    return e


def create_weapon_embed(wep):
    url_name = "%20".join(wep.name.split())
    e = discord.Embed(title=wep.name,
                      desc=wep.name,
                      url=config.gamepedia_url.format(url_name),
                      color=get_color(wep.elementtype))
    sub_portrait_URL = "weapons/portraits/{0}.png".format(url_name)
    portrait_URL = config.picture_server + sub_portrait_URL
    e.set_thumbnail(url=portrait_URL)
    e.add_field(name=get_emoji_rarity(wep.rarity),
                value="**HP** {0}\n**STR** {1}".format(wep.maxhp, wep.maxstr),
                inline=True)
    e.add_field(name=get_emoji_element(wep.elementtype) +
                get_emoji_weapon(wep.weapontype) +
                get_emoji_limited(wep.limited),
                value=convert_ISO_date_to_string(wep.releasedate),
                inline=True)
    skill_format = "Skill: {0} [SP Cost: {1}] [Frame Time: {2}]"
    ability_format = "Ability: {0}"
    for skill in wep.skills:
        e.add_field(name=skill_format.format(skill.name, skill.spcost,
                                             skill.frametime),
                    value=skill.description,
                    inline=False)
    for ability in wep.abilities:
        e.add_field(name=ability_format.format(ability.name),
                    value=ability.description,
                    inline=False)
    return e


def create_weapon_upgrades_to_embed(wep):
    url_name = "%20".join(wep.name.split())
    e = discord.Embed(title="{0} - Upgrades To".format(wep.name),
                      desc="Upgrades To",
                      url=config.gamepedia_url.format(url_name))
    for i in range(0, len(wep.upgrades_to)):
        materials_str = ""
        upgrade_to = wep.upgrades_to[i]
        for mat, qty in wep.upgrades_to_materials[i].items():
            materials_str += "{0} - *{1}*\n".format(mat, str(qty))
        e.add_field(name=upgrade_to, value=materials_str, inline=False)
    return e


def create_weapon_upgrades_from_embed(wep):
    url_name = "%20".join(wep.name.split())
    e = discord.Embed(title="{0} - Upgrades From".format(wep.name),
                      desc="Upgrades From",
                      url=config.gamepedia_url.format(url_name))
    for i in range(0, len(wep.upgrades_from)):
        materials_str = ""
        upgrade_from = wep.upgrades_from[i]
        for mat, qty in wep.upgrades_from_materials[i].items():
            materials_str += "{0} - *{1}*\n".format(mat, str(qty))
    for upgrade_from in wep.upgrades_from:
        e.add_field(name=upgrade_from, value=materials_str, inline=False)
    return e


def create_unit_list_embed(unit_list):
    e = discord.Embed(title="Query Results", desc="Query Results",
                      color=get_color(None))
    index = 1
    for name, unit_type in unit_list:
        e.add_field(name="{0}. {1}".format(index, name),
                    value="*{0}*".format(unit_type), inline=False)
        index += 1
    return e


def create_events_embed(current_events):
    e = discord.Embed(title="Current Events", desc="Current Events",
                      color=get_color(None))
    for event in current_events:
        e.add_field(name="{0} [{1}]".format(event.name, event.type),
                    value="*{0}* - *{1}* ({2} days and {3} hours left)".format(
                        convert_ISO_date_to_string(event.start),
                        convert_ISO_date_to_string(event.end),
                        event.days, event.hours),
                    inline=False)
    return e
# endregion


# region Helper Functions
def get_emoji_element(elementtype):
    if elementtype in config.element_emoji:
        return config.element_colors[elementtype]
    return ""


def get_emoji_weapon(weapontype):
    return config.weapon_emoji[weapontype]


def get_emoji_unit(unittype):
    return config.unit_emoji[unittype]


def get_emoji_rarity(rarity):
    return config.rarity_emoji[rarity] * rarity


def get_emoji_limited(limited):
    if limited == 1:
        return config.limited_emoji
    return ""


def get_color(elementtype):
    if elementtype is None:
        return 0x00eaff
    return int(config.element_colors[elementtype], 16)


def get_emoji_eldwater(rarity):
    cost = 1700
    if rarity == 4:
        cost = 17000
    elif rarity == 5:
        cost = 37000
    return "{0} x{1}".format(config.eldwater_emoji, str(cost))
# endregion
