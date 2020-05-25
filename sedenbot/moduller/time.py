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

""" Bir konumun ya da UserBot sunucusunun tarih/saatini gösterebilecek modüldür. """

from datetime import datetime as dt
from pytz import country_names as c_n
from pytz import country_timezones as c_tz
from pytz import timezone as tz

from sedenbot import CMD_HELP, COUNTRY, TZ_NUMBER
from sedenbot.events import extract_args, sedenify

async def get_tz(con):
    """ Seçilen bölgenin saat dilimini elde etmek içindir. """
    if "(Uk)" in con:
        con = con.replace("Uk", "UK")
    if "(Us)" in con:
        con = con.replace("Us", "US")
    if " Of " in con:
        con = con.replace(" Of ", " of ")
    if "(Western)" in con:
        con = con.replace("(Western)", "(western)")
    if "Minor Outlying Islands" in con:
        con = con.replace("Minor Outlying Islands", "minor outlying islands")
    if "Nl" in con:
        con = con.replace("Nl", "NL")

    for c_code in c_n:
        if con == c_n[c_code]:
            return c_tz[c_code]
    try:
        if c_n[con]:
            return c_tz[con]
    except KeyError:
        return

@sedenify(outgoing=True, pattern="^.time")
async def time_func(tdata):
    """ .time komutu şu şekilde kullanılabilir
        1- Bölge belirtilerek.
        2. Varsayılan userbot bölgesi (.settime komutuyla ayarlanabilir)
        3. UserBot'un barındığı sunucunun tarihi.
    """
    arr = extract_args(tdata).split(' ', 1)
    if len(arr) < 2:
        await tdata.edit("`Komut kullanımı hatalı.`")
        return

    con = arr[0]
    tz_num = arr[1]

    t_form = "%H:%M"
    c_name = None

    if len(con) > 4:
        try:
            c_name = c_n[con]
        except KeyError:
            c_name = con
        timezones = await get_tz(con)
    elif COUNTRY:
        c_name = COUNTRY
        tz_num = TZ_NUMBER
        timezones = await get_tz(COUNTRY)
    else:
        await tdata.edit(f"Burada saat  **{dt.now().strftime(t_form)}** ")
        return

    if not timezones:
        await tdata.edit("`Geçersiz ülke.`")
        return

    if len(timezones) == 1:
        time_zone = timezones[0]
    elif len(timezones) > 1:
        if tz_num:
            tz_num = int(tz_num)
            time_zone = timezones[tz_num - 1]
        else:
            return_str = f"`{c_name} ülkesi birden fazla saat dilimine sahip:`\n\n"

            for i, item in enumerate(timezones):
                return_str += f"`{i+1}. {item}`\n"

            return_str += "\n`Şunlardan birini numara belirterek seçin."
            return_str += f"`Örnek: .time {c_name} 2`"

            await tdata.edit(return_str)
            return

    dtnow = dt.now(tz(time_zone)).strftime(t_form)

    if c_name != COUNTRY:
        await tdata.edit(
            f"{c_name} ülkesinde saat **{dtnow}** ({time_zone} saat diliminde).")
        return

    elif COUNTRY:
        await tdata.edit(f"{COUNTRY} ülkesinde saat **{dtnow}**  "
                         f"({time_zone} saat diliminde).")
        return

@sedenify(outgoing=True, pattern="^.date(?: |$)(.*)(?<![0-9])(?: |$)([0-9]+)?")
async def date_func(dat):
    """ .date komutu şu şekilde kullanılabilir
        1- Bölge belirtilerek.
        2. Varsayılan userbot bölgesi (.settime komutuyla ayarlanabilir)
        3. UserBot'un barındığı sunucunun tarihi.
    """
    con = dat.pattern_match.group(1).title()
    tz_num = dat.pattern_match.group(2)

    d_form = "%d/%m/%y - %A"
    c_name = ''

    if len(con) > 4:
        try:
            c_name = c_n[con]
        except KeyError:
            c_name = con
        timezones = await get_tz(con)
    elif COUNTRY:
        c_name = COUNTRY
        tz_num = TZ_NUMBER
        timezones = await get_tz(COUNTRY)
    else:
        await dat.edit(f"Burada tarih: **{dt.now().strftime(d_form)}** ")
        return

    if not timezones:
        await dat.edit("`Geçersiz ülke`")
        return

    if len(timezones) == 1:
        time_zone = timezones[0]
    elif len(timezones) > 1:
        if tz_num:
            tz_num = int(tz_num)
            time_zone = timezones[tz_num - 1]
        else:
            return_str = f"`{c_name} ülkesi birden fazla saat dilimine sahip:`\n"

            for i, item in enumerate(timezones):
                return_str += f"`{i+1}. {item}`\n"

            return_str += "\n`Şunlardan birini numara belirterek seçin"
            return_str += f"Örnek: .date {c_name} 2"

            await dat.edit(return_str)
            return

    dtnow = dt.now(tz(time_zone)).strftime(d_form)

    if c_name != COUNTRY:
        await dat.edit(
            f"{c_name} ülkesinde tarih **{dtnow}** ({time_zone} saat diliminde).`")
        return

    elif COUNTRY:
        await dat.edit(f"{COUNTRY} ülkesinde tarih **{dtnow}**"
                       f" ({time_zone} saat diliminde).")
        return

CMD_HELP.update({
    "time":
    ".time <ülke ismi/kodu> <saat dilimi numarası>"
    "\nKullanım: Bir ülkenin saatini gösterir. Eğer bir ülke "
    "birden fazla saat dilimine sahipse, tümü birden gösterilir "
    "ve seçim sana bırakılır."
})
CMD_HELP.update({
    "date":
    ".date <ülke ismi/kodu> <saat dilimi numarası>"
    "\nKullanım: Bir ülkenin tarihini gösterir. Eğer bir ülke"
    "birden fazla saat dilimine sahipse, tümü birden gösterilir."
    "ve seçim sana bırakılır."
})
