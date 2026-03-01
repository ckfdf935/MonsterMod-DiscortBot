from os import getenv
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord import app_commands
import datetime

import database


load_dotenv()
TOKEN = getenv('TOKEN')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class ModBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        database.init_db()
        await self.tree.sync()
        print("Бот запущен ")


bot = ModBot()


@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Новичок")
    if role:
        await member.add_roles(role)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    lvl_up = database.update_xp(message.author.id)
    if lvl_up:
        await message.channel.send(f"⬆️ **{message.author.mention}**, вы подняли уровень до **{lvl_up}**!")

    await bot.process_commands(message)



@bot.tree.command(name="ban", description="Забанить пользователя")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Нарушение правил"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} забанен. Причина: {reason}")
    await log_action(interaction.guild, f"Бан: {member}", interaction.user, reason)


@bot.tree.command(name="mute", description="Тайм-аут пользователя")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Тишина"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 {member.mention} в муте на {minutes} мин.")
    await log_action(interaction.guild, f"Мут ({minutes} мин): {member}", interaction.user, reason)


@bot.tree.command(name="unmute", description="Снять тайм-аут с пользователя")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "Помилован"):

    await member.timeout(None, reason=reason)

    await interaction.response.send_message(f"🔊 {member.mention} был размучен.")
    await log_action(interaction.guild, f"Размут: {member}", interaction.user, reason)


@bot.tree.command(name="profile", description="Посмотреть свой уровень и опыт")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user

    xp, lvl = database.get_profile(member.id)

    embed = discord.Embed(title=f"📊 Профиль: {member.display_name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Уровень", value=f"⭐ {lvl}", inline=True)
    embed.add_field(name="Опыт", value=f"🧪 {xp}/{lvl * 10}", inline=True)
    embed.set_footer(text="Активно общайся, чтобы получать опыт!")

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="server_info", description="Статистика сервера")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🏰 Сервер: {guild.name}", color=discord.Color.green())
    embed.add_field(name="👑 Владелец", value=guild.owner.mention, inline=False)
    embed.add_field(name="👥 Участников", value=guild.member_count, inline=True)
    embed.add_field(name="📅 Создан", value=guild.created_at.strftime("%d.%m.%Y"), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await interaction.response.send_message(embed=embed)


async def log_action(guild, action, admin, reason):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(title="🛡 Действие модератора", color=discord.Color.red())
        embed.add_field(name="Действие", value=action)
        embed.add_field(name="Админ", value=admin.mention)
        embed.add_field(name="Причина", value=reason)
        await log_channel.send(embed=embed)


bot.run(TOKEN)