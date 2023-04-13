import os

from dotenv import load_dotenv


load_dotenv()

DISABLED = os.getenv("DISABLED", r'(?<=class=lbutdis value=").+(?=" DISABLED>)')  # DISABLED page

# r'(?<=class=lbut onclick="location='main\.php)\S+(?='" value="Инвентарь")'
BUT_INV = os.getenv("BUT_INV")  # go to inv page


# r'(?<=Bi_w27_54\.gif border=0 width=40 height=40 onclick="location='main\.php)\S+(?=')'
TEXT = os.getenv("TEXT")

TEXT2 = os.getenv("TEXT2", r"(?<=get_id=43&act=101&)\S+(?=')")
