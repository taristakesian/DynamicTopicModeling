import dotenv
import os


dotenv.load_dotenv()


API_ID = int(os.environ.get("API_ID"))
API_HASH = str(os.environ.get("API_HASH"))