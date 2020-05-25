# Copyright (C) 2020 TeamDerUntergang.
#
# SedenUserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SedenUserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

""" Telegram'dan kod ve terminal komutlarını yürütmek için UserBot modülü. """

import asyncio

from getpass import getuser
from os import remove
from sys import executable

from sedenbot import CMD_HELP, BOTLOG, BOTLOG_CHATID
from sedenbot.events import extract_args, sedenify

@sedenify(outgoing=True, pattern="^.eval")
async def evaluate(query):
    """ .eval komutu verilen Python ifadesini değerlendirir. """
    if query.is_channel and not query.is_group:
        await query.edit("`Eval komutlarına kanallarda izin verilmiyor`")
        return
    args = extract_args(query)
    if len(args) > 1:
        expression = args
    else:
        await query.edit("``` Değerlendirmek için bir ifade verin. ```")
        return

    if expression in ("userbot.session", "config.env"):
        await query.edit("`Bu tehlikeli bir operasyon! İzin verilemedi!`")
        return

    try:
        evaluation = str(eval(expression))
        if evaluation:
            if isinstance(evaluation, str):
                if len(evaluation) >= 4096:
                    file = open("output.txt", "w+")
                    file.write(evaluation)
                    file.close()
                    await query.client.send_file(
                        query.chat_id,
                        "output.txt",
                        reply_to=query.id,
                        caption="`Çıktı çok büyük, dosya olarak gönderiliyor`",
                    )
                    remove("output.txt")
                    return
                await query.edit("**Sorgu: **\n`"
                                 f"{expression}"
                                 "`\n**Sonuç: **\n`"
                                 f"{evaluation}"
                                 "`")
        else:
            await query.edit("**Sorgu: **\n`"
                             f"{expression}"
                             "`\n**Sonuç: **\n`Sonuç döndürülemedi / Yanlış`")
    except Exception as err:
        await query.edit("**Sorgu: **\n`"
                         f"{expression}"
                         "`\n**İstisna: **\n"
                         f"`{err}`")

    if BOTLOG:
        await query.client.send_message(
            BOTLOG_CHATID,
            f"Eval sorgusu {expression} başarıyla yürütüldü")

@sedenify(outgoing=True, pattern=r"^.exec")
async def run(run_q):
    """ .exec komutu dinamik olarak oluşturulan programı yürütür """
    if run_q.is_channel and not run_q.is_group:
        await run_q.edit("`Exec komutlarına kanallarda izin verilmiyor`")
        return

    code = extract_args(run_q)

    if len(code) < 1:
        await run_q.edit("``` Yürütmek için en az bir değişken gereklidir \
.seden exec kullanarak örnek alabilirsiniz.```")
        return

    if code in ("userbot.session", "config.env"):
        await run_q.edit("`Bu tehlikeli bir operasyon! İzin verilemedi!`")
        return

    if len(code.splitlines()) <= 5:
        codepre = code
    else:
        clines = code.splitlines()
        codepre = clines[0] + "\n" + clines[1] + "\n" + clines[2] + \
            "\n" + clines[3] + "..."

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        executable,
        '-c',
        command.strip(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
        + str(stderr.decode().strip())

    if result:
        if len(result) > 4096:
            file = open("output.txt", "w+")
            file.write(result)
            file.close()
            await run_q.client.send_file(
                run_q.chat_id,
                "output.txt",
                reply_to=run_q.id,
                caption="`Çıktı çok büyük, dosya olarak gönderiliyor`",
            )
            remove("output.txt")
            return
        await run_q.edit("**Sorgu: **\n`"
                         f"{codepre}"
                         "`\n**Sonuç: **\n`"
                         f"{result}"
                         "`")
    else:
        await run_q.edit("**Sorgu: **\n`"
                         f"{codepre}"
                         "`\n**Sonuç: **\n`Sonuç döndürülemedi / Yanlış`")

    if BOTLOG:
        await run_q.client.send_message(
            BOTLOG_CHATID,
            "Exec sorgusu " + codepre + " başarıyla yürütüldü")

@sedenify(outgoing=True, pattern="^.term")
async def terminal_runner(term):
    """ .term komutu sunucunuzda bash komutlarını ve komut dosyalarını çalıştırır. """
    curruser = getuser()
    command = extract_args(term)
    try:
        from os import geteuid
        uid = geteuid()
    except ImportError:
        uid = "Bu değil şef!"

    if term.is_channel and not term.is_group:
        await term.edit("`Term komutlarına kanallarda izin verilmiyor`")
        return

    if not command:
        await term.edit("``` Yardım almak için .seden term yazarak \
            örneğe bakabilirsin.```")
        return

    if command in ("userbot.session", "config.env"):
        await term.edit("`Bu tehlikeli bir operasyon! İzin verilemedi!`")
        return

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
        + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await term.client.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Çıktı çok büyük, dosya olarak gönderiliyor`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")

    if BOTLOG:
        await term.client.send_message(
            BOTLOG_CHATID,
            "Terminal Komutu " + command + " başarıyla yürütüldü",
        )

CMD_HELP.update({"eval": ".eval 2 + 3\nKullanım: Mini ifadeleri değerlendirin."})
CMD_HELP.update(
    {"exec": ".exec print('merhaba')\nKullanım: Küçük python komutları yürütün."})
CMD_HELP.update(
    {"term": ".term ls\nKullanım: Sunucunuzda bash komutlarını ve komut dosyalarını çalıştırın."})
