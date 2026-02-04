import discord
import asyncio
import a2s
import datetime
import os


# ================== НАСТРОЙКИ ==================

TOKEN = os.getenv("TOKEN")

SERVER_IP = "31.25.244.232"
SERVER_PORT = 50275

TARGET_ID = 1468676614568018022  # ID ветки ИЛИ канала

UPDATE_INTERVAL = 60  # секунд

# Логотип SCP
SCP_LOGO_URL = "https://cdn.discordapp.com/attachments/1246188377670287362/1468646794534715544/3378969168_preview_1687263703_new_preview_previewfile_1768974884.jpg"

# ==============================================


intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_obj = None
round_start_time = None


# ================== ПОЛУЧЕНИЕ ДАННЫХ ==================

def get_server_info():
    global round_start_time

    try:
        address = (SERVER_IP, SERVER_PORT)
        info = a2s.info(address)

        name = info.server_name

        # Убираем Exiled, сохраняя регистр
        if "Exiled" in name or "exiled" in name:

            parts = name.split("Exiled")

            if len(parts) == 1:
                parts = name.split("exiled")

            name = parts[0].strip()


        # Время раунда (примерно)
        if info.player_count > 0 and round_start_time is None:
            round_start_time = datetime.datetime.now()

        if info.player_count == 0:
            round_start_time = None


        return {
            "online": True,
            "players": info.player_count,
            "max_players": info.max_players,
            "name": name,
            "round_start": round_start_time
        }

    except Exception as e:

        print("Ошибка получения сервера:", e)

        return {
            "online": False
        }


# ================== EMBED ==================

async def build_embed():

    data = await asyncio.to_thread(get_server_info)

    embed = discord.Embed(
        color=0xF1C40F  # Жёлтая рамка
    )

    # Author с логотипом
    embed.set_author(
        name="[RST] Anomaly Classic",
        icon_url=SCP_LOGO_URL
    )

    # Картинка справа
    embed.set_thumbnail(
        url=SCP_LOGO_URL
    )


    # Сервер оффлайн
    if not data["online"]:

        embed.add_field(
            name="❌ Сервер",
            value="Недоступен",
            inline=False
        )

        return embed


    # Игроки
    embed.add_field(
        name="👥 Игроки",
        value=f"{data['players']} / {data['max_players']}",
        inline=True
    )

    # IP (копируемый)
    embed.add_field(
        name="🌐 IP сервера",
        value=f"`{SERVER_IP}:{SERVER_PORT}`",
        inline=True
    )

    # Сервер
    embed.add_field(
        name="📡 Сервер",
        value=data["name"],
        inline=False
    )


    # Время раунда
    if data["round_start"]:

        delta = datetime.datetime.now() - data["round_start"]

        minutes = int(delta.total_seconds() // 60)
        seconds = int(delta.total_seconds() % 60)

        time_text = f"{minutes} мин {seconds} сек"

    else:
        time_text = "Раунд не идёт"


    embed.add_field(
        name="⏱ Время начала раунда",
        value=time_text,
        inline=False
    )


    return embed


# ================== ОБНОВЛЕНИЕ ==================

async def updater():

    global message_obj

    await client.wait_until_ready()

    target = client.get_channel(TARGET_ID)

    if target is None:
        print("❌ Канал/ветка не найдены")
        return


    # Если это ветка — подключаемся
    if isinstance(target, discord.Thread):
        await target.join()


    while not client.is_closed():

        embed = await build_embed()

        try:

            if message_obj is None:

                message_obj = await target.send(embed=embed)

            else:

                await message_obj.edit(embed=embed)


        except Exception as e:

            print("Ошибка обновления:", e)
            message_obj = None


        await asyncio.sleep(UPDATE_INTERVAL)



# ================== ЗАПУСК ==================

@client.event
async def on_ready():

    print(f"✅ Бот запущен как {client.user}")

    client.loop.create_task(updater())


client.run(TOKEN)
