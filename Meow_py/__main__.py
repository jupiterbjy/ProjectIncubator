import logging
import argparse
import asyncio
import itertools


from discord.ext import commands
from discord import DiscordException
from discord.errors import HTTPException


from log_initalizer import init_logger


bot = commands.Bot(command_prefix="/")


end_signature = "\u200a\u200a\u200a"
end_signature_encoded = end_signature.encode("utf8")
results_format = "Run results:\n\n{}"

codec = "utf8"
code_format = "python3 <<EOF\n{}\nEOF"
msg_format = "```\n{}\n```"
overflow_msg = "..."


def encode(string: str):
    string += end_signature

    return string.encode("utf8")


def decode(byte_string: bytes):
    decoded = byte_string.decode("utf8")

    return decoded.removeprefix(end_signature)


@bot.event
async def on_ready():
    print(f"{bot.user} connected.")

    if not any(guild.id == args.guild_id for guild in bot.guilds):
        logger.critical("Bot is not connected to given server ID %s", args.guild_id)

        raise DiscordException(f"Bot is not connected to given server ID {args.guild_id}")


@bot.command(name="run", help="Run cyan run!")
async def run_literally(context: commands.Context):

    await context.send("https://cdn.discordapp.com/attachments/783069235999014912/840531297499480084/ezgif.com-gif-maker.gif")


@bot.command(name="py", help="Execute python code in Docker(not yet)")
async def run_script(context: commands.Context, *, code: str):

    # check code safety in future
    # Extract code
    striped = code.strip()

    if striped.startswith("```python"):
        code = striped.removeprefix("```python").removesuffix("```")

    else:
        await context.reply("Please use ```python\n<code>\n``` format!")

    # Dumb way when it's not certain - put sequence of try-except, lel

    code_ = code_format.format(code)

    logger.info("Received code from %s by %s - detail: %s", context.channel, context.author, code_)

    try:
        proc = await asyncio.create_subprocess_shell(code_, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    except Exception as err_:
        await context.reply(msg_format.format(err_))
        return

    try:
        stdout, stderr = await proc.communicate()
    except Exception as err_:
        await context.reply(f"{msg_format.format(err_)}\n\nExited with return code {proc.returncode}")
        return

    output = []

    if stdout:
        output.append(stdout.decode(codec))

    if stderr:
        output.append(stderr.decode(codec))

    message = "\n".join(output)

    exit_msg = f"\nExited with return code {proc.returncode}"

    try:
        await context.reply(msg_format.format(message) + exit_msg)
    except HTTPException as err_:

        if len(message) + len(exit_msg) + (len(msg_format) - 2) >= 2000:
            fitted = message[:2000 - len(overflow_msg) - len(exit_msg) - (len(msg_format) - 2)]
            cut_target = fitted.split("\n")[-1]
            message = fitted.removesuffix(cut_target) + overflow_msg

            await context.reply(message + exit_msg)
            return

        # This shouldn't run
        logger.debug("Got other http error: %s", err_)


if __name__ == '__main__':

    logger = logging.getLogger("Meow.py")

    # Parsing start

    parser = argparse.ArgumentParser()

    parser.add_argument("bot_token", type=str, help="Bot's token")
    parser.add_argument("guild_id", type=int, help="Server's ID")

    args = parser.parse_args()

    init_logger(logger, True)

    try:
        bot.run(args.bot_token)
    except DiscordException as err:
        logger.critical("DiscordException - is token valid? Details: %s", err)
