from io import BytesIO

import requests
from PIL import Image
import traceback


def fetch_media(img_url):
    """ Fetches submission media """
    if 'm.imgur.com' in img_url:
        img_url = img_url.replace('m.imgur.com', 'i.imgur.com')

    if not any(a in img_url for a in ('.jpg', '.png', '.jpeg')):
        return False
    try:
        with requests.get(img_url) as resp:
            try:
                return Image.open(BytesIO(resp.content))
            except:
                traceback.print_exc()
                print(f'Encountered exception when opening image in fetch_media: {img_url}')
                return False
    except:
        traceback.print_exc()
        print(f'Encountered exception when requesting image in fetch_media: {img_url}')
        return False


def diff_hash(image):
    """Generates a difference hash from an image"""
    img = image.convert("L")
    img = img.resize((8, 8), Image.ANTIALIAS)
    prev_px = img.getpixel((0, 7))
    hash_diff = 0
    for row in range(0, 8, 2):
        for col in range(8):
            hash_diff <<= 1
            pixel = img.getpixel((col, row))
            hash_diff |= 1 * (pixel >= prev_px)
            prev_px = pixel
        row += 1
        for col in range(7, -1, -1):
            hash_diff <<= 1
            pixel = img.getpixel((col, row))
            hash_diff |= 1 * (pixel >= prev_px)
            prev_px = pixel
    img.close()
    return hash_diff


async def send_embed(discord, title, description, output_channel, color=0):
    embed = discord.Embed(
        title=title,
        description=description,
        color=0xE02B2B if color == 0 else color
    )
    await output_channel.send(embed=embed)
