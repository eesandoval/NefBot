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
from discord.ext.commands import Bot
from models.adventurer import Adventurer
from models.wyrmprint import Wyrmprint
from models.dragon import Dragon
from models.weapon import Weapon
from models.events import Event
from utils.config import Config
from utils.parsing import convert_ISO_date_to_string, convert_args_to_dict

channel = None
adv_msgs = {}
wyr_msgs = {}
dra_msgs = {}
wep_msgs = {}
all_msgs = []
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
                description='''
                Searches for an adventurer using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released adventurer is returned.
                ''',
                brief="Gets an adventurer using a case insensitive search",
                aliases=["adventurer", "adv", "a"],
                pass_context=True)
async def get_adventurer(ctx, *, name):
    try:
        adventurer = controller.process_adventurer(name)
        await show_adventurer(adventurer)
    except Exception as e:
        await show_exception(e)


@client.command(name="get_wyrmprint",
                description='''
                Searches for a wyrmprint using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released wyrmprint is returned.
                ''',
                brief="Gets a wyrmprint using a case insensitive search",
                aliases=["wyrmprint", "wyr", "w"],
                pass_context=True)
async def get_wyrmprint(ctx, *, name):
    try:
        wyrmprint = controller.process_wyrmprint(name)
        await show_wyrmprint(wyrmprint)
    except Exception as e:
        await show_exception(e)


@client.command(name="get_dragon",
                description='''
                Searches for a dragon using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released dragon is returned.
                ''',
                brief="Gets a dragon using a case insensitive search",
                aliases=["dragon", "dra", "d"],
                pass_context=True)
async def get_dragon(ctx, *, name):
    try:
        dragon = controller.process_dragon(name)
        await show_dragon(dragon)
    except Exception as e:
        await show_exception(e)


@client.command(name="get_weapon",
                description='''
                Searches for a weapon using a name or alias.
                The search is case insensitive, and in the case of multiple
                results, the earliest released weapon is returned.
                ''',
                brief="Gets a weapon using a case insensitive search",
                aliases=["weapon", "wep"],
                pass_context=True)
async def get_weapon(ctx, *, name):
    try:
        weapon = controller.process_weapon(name)
        await show_weapon(weapon)
    except Exception as e:
        await show_exception(e)


@client.command(name="query",
                description='''
                Queries the database for adventurers, dragons, or
                wyrmprints with the given criteria. Criteria is set as
                pairs. See example below:
                {0}query type=adv ability="Burn Res +100%"
                '''.format(config.command_start),
                brief="Queries for any adventurer, print, or dragon",
                aliases=["que", "q"],
                pass_context=True)
async def query(context):
    message = handle_context(context)
    await client.send_typing(channel)
    await controller.query(convert_args_to_dict(message))


@client.command(name="update",
                description='''
                Resets the configuration and updates the bot using the
                new values set in the config.ini file
                ''',
                brief="Updates the bot's configurations",
                aliases=["u"])
async def update():
    global config
    config = Config("config.ini")
    await client.say("Update completed")


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
async def alias(alias_text, aliased_name=None):
    try:
        alias_result = controller.handle_alias(alias_text, aliased_name)
        await client.say(alias_result)
    except Exception as e:
        await show_exception(e)


@client.command(name="events",
                description='''
                Shows the latest events that are happening in the game
                This includes the current showcase(s), void battles,
                raid/facility/defense events, and limited endeavors
                ''',
                brief="Shows the latest events currently happening")
async def events():
    current_events = controller.handle_current_events()
    await show_events(current_events)


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
async def show_adventurer(adv, message=None):
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
    await show_or_edit_adventurer(e, adv, message)


@client.event
async def show_wyrmprint(wyr, message=None):
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
    await show_or_edit_wyrmprint(e, wyr, message)


@client.event
async def show_dragon(dra, message=None):
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
    await show_or_edit_dragon(e, dra, message)


@client.event
async def show_weapon(wep, message=None):
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
    await show_or_edit_weapon(e, wep, message)


@client.event
async def show_events(current_events, message=None):
    e = discord.Embed(title="Current Events", desc="Current Events",
                      color=get_color(None))
    for event in current_events:
        e.add_field(name="{0} [{1}]".format(event.name, event.type),
                    value="*{0}* - *{1}* ({2} days and {3} hours left)".format(
                        convert_ISO_date_to_string(event.start),
                        convert_ISO_date_to_string(event.end),
                        event.days, event.hours),
                    inline=False)
    await client.say(embed=e)


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
async def show_exception(e):
    print(traceback.format_exc())
    await client.say(str(e))


def get_emoji_element(elementtype):
    try:
        return config.element_emoji[elementtype]
    except KeyError:
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


@client.event
async def on_reaction_add(reaction, user):
    if user == client.user:
        return

    emoji = reaction.emoji
    message = reaction.message
    if (message.id in adv_msgs and emoji in config.adv_reactions):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        adventurer = adv_msgs[message.id]
        await process_adventurers_reaction(emoji, adventurer, message)

    elif (message.id in wyr_msgs and emoji in config.wyr_reactions):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        wyrmprint = wyr_msgs[message.id]
        await process_wyrmprint_reaction(emoji, wyrmprint, message)

    elif (message.id in dra_msgs and emoji in config.dra_reactions):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        dragon = dra_msgs[message.id]
        await process_dragon_reaction(emoji, dragon, message)

    elif (message.id in wep_msgs and emoji in config.wep_reactions):
        await client.remove_reaction(reaction.message, reaction.emoji, user)
        weapon = wep_msgs[message.id]
        await process_weapon_reaction(emoji, weapon, message)


@client.event
async def process_adventurers_reaction(emoji, adventurer, message):
    if emoji == "\U0001F5BC":  # Full picture
        await show_adventurer_full(adventurer, message)
        return

    adventurer = controller.process_adventurer(adventurer.name,
                                               get_level(emoji))
    await show_adventurer(adventurer, message)


@client.event
async def process_wyrmprint_reaction(emoji, wyrmprint, message):
    if emoji == "\U0001F5BC":  # Full picture
        await show_wyrmprint_full(wyrmprint, message)
        return
    elif emoji == "\U0001F3A8":  # Full base picture
        await show_wyrmprint_base_full(wyrmprint, message)
        return

    wyrmprint = controller.process_wyrmprint(wyrmprint.name, get_level(emoji))
    await show_wyrmprint(wyrmprint, message)


@client.event
async def process_dragon_reaction(emoji, dragon, message):
    if emoji == "\U0001F5BC":  # Full picture
        await show_dragon_full(dragon, message)
        return

    dragon = controller.process_dragon(dragon.name, get_level(emoji))
    await show_dragon(dragon, message)


@client.event
async def process_weapon_reaction(emoji, weapon, message):
    if emoji == "\U000023E9":  # Upgrades To
        await show_weapon_upgrades_to(weapon, message)
        return
    elif emoji == "\U000023EA":  # Upgrades From
        await show_weapon_upgrades_from(weapon, message)
        return

    weapon = controller.process_weapon(weapon.name, get_level(emoji))
    await show_weapon(weapon, message)


def get_level(emoji):
    level = 1
    if emoji == "\U0001F508":  # 1 unbind
        level = 1
    elif emoji == "\U0001F509":  # 2 unbinds
        level = 2
    elif emoji == "\U0001F50A":  # 3 unbinds
        level = 3
    return level


@client.event
async def show_adventurer_full(adventurer, message=None):
    url_name = "%20".join(adventurer.name.split())
    e = discord.Embed(title=adventurer.name + " - " + adventurer.title,
                      desc=adventurer.title,
                      url=config.gamepedia_url.format(url_name))
    sub_URL = "adventurers/full/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_adventurer(e, adventurer, message)


@client.event
async def show_wyrmprint_full(wyrmprint, message=None):
    url_name = "%20".join(wyrmprint.name.split())
    e = discord.Embed(title=wyrmprint.name, desc=wyrmprint.name,
                      url=config.gamepedia_url.format(url_name))
    sub_URL = "wyrmprints/full/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_wyrmprint(e, wyrmprint, message)


@client.event
async def show_wyrmprint_base_full(wyrmprint, message=None):
    url_name = "%20".join(wyrmprint.name.split())
    e = discord.Embed(title=wyrmprint.name, desc=wyrmprint.name,
                      url=config.gamepedia_url.format(url_name))
    sub_URL = "wyrmprints/base/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_wyrmprint(e, wyrmprint, message)


@client.event
async def show_dragon_full(dragon, message=None):
    url_name = "%20".join(dragon.name.split())
    e = discord.Embed(title=dragon.name, desc=dragon.name,
                      url=config.gamepedia_url.format(url_name))
    sub_URL = "dragons/full/{0}.png".format(url_name)
    e.set_image(url=config.picture_server + sub_URL)
    await show_or_edit_dragon(e, dragon, message)


@client.event
async def show_weapon_upgrades_to(weapon, message=None):
    url_name = "%20".join(weapon.name.split())
    e = discord.Embed(title="{0} - Upgrades To".format(weapon.name),
                      desc="Upgrades To",
                      url=config.gamepedia_url.format(url_name))
    for i in range(0, len(weapon.upgrades_to)):
        materials_str = ""
        upgrade_to = weapon.upgrades_to[i]
        for mat, qty in weapon.upgrades_to_materials[i].items():
            materials_str += "{0} - *{1}*\n".format(mat, str(qty))
        e.add_field(name=upgrade_to, value=materials_str, inline=False)
    await show_or_edit_weapon(e, weapon, message)


@client.event
async def show_weapon_upgrades_from(weapon, message=None):
    url_name = "%20".join(weapon.name.split())
    e = discord.Embed(title="{0} - Upgrades From".format(weapon.name),
                      desc="Upgrades From",
                      url=config.gamepedia_url.format(url_name))
    for i in range(0, len(weapon.upgrades_from)):
        materials_str = ""
        upgrade_from = weapon.upgrades_from[i]
        for mat, qty in weapon.upgrades_from_materials[i].items():
            materials_str += "{0} - *{1}*\n".format(mat, str(qty))
    for upgrade_from in weapon.upgrades_from:
        e.add_field(name=upgrade_from, value=materials_str, inline=False)
    await show_or_edit_weapon(e, weapon, message)


@client.event
async def show_or_edit_adventurer(e, adventurer, message=None):
    if message is None:
        global adv_msgs, all_msgs
        await clear_active_messages()
        msg = await client.say(embed=e)
        adv_msgs[msg.id] = adventurer
        all_msgs.append(msg)
        for emoji in config.adv_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_or_edit_wyrmprint(e, wyrmprint, message=None):
    if message is None:
        global wyr_msgs, all_msgs
        await clear_active_messages()
        msg = await client.say(embed=e)
        wyr_msgs[msg.id] = wyrmprint
        all_msgs.append(msg)
        for emoji in config.wyr_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_or_edit_dragon(e, dragon, message=None):
    if message is None:
        global dra_msgs
        await clear_active_messages()
        msg = await client.say(embed=e)
        dra_msgs[msg.id] = dragon
        all_msgs.append(msg)
        for emoji in config.dra_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_or_edit_weapon(e, weapon, message=None):
    if message is None:
        global adv_msgs, all_msgs
        await clear_active_messages()
        msg = await client.say(embed=e)
        wep_msgs[msg.id] = weapon
        all_msgs.append(msg)
        for emoji in config.wep_reactions:
            await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def show_or_edit_event(e, message=None):
    if message is None:
        global all_msgs
        await clear_active_messages()
        msg = await client.say(embed=e)
        all_msgs.append(msg)
        # for emoji in config.wep_reactions:
        #     await client.add_reaction(msg, emoji)
    else:
        msg = await client.edit_message(message, embed=e)


@client.event
async def clear_active_messages():
    global all_msgs, adv_msgs, \
        dra_msgs, wyr_msgs, wep_msgs

    while len(all_msgs) > max(0, config.message_limit - 1):
        message = all_msgs.pop(0)
        await client.clear_reactions(message)

        if message.id in adv_msgs:
            adv_msgs.pop(message.id)
        elif message.id in dra_msgs:
            dra_msgs.pop(message.id)
        elif message.id in wyr_msgs:
            wyr_msgs.pop(message.id)
        elif message.id in wep_msgs:
            wep_msgs.pop(message.id)
