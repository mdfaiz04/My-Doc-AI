from pymongo import MongoClient
from django.conf import settings

# Create a single global client (MongoDB recommended best practice)
client = MongoClient(settings.MONGO_URI)

# Select database
db = client[settings.MONGO_DB_NAME]

# Collections
users_col = db["users"]
doctors_col = db["doctors"]
appointments_col = db["appointments"]
