<<<<<<< HEAD
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
=======
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
>>>>>>> c200fa104957a35c0f1c32ba4d452005911b92e7
    raise ValueError("BOT_TOKEN topilmadi!")