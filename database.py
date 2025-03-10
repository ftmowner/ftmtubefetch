import os
from pymongo import MongoClient
from ftmconfig import MONGO_URI, OWNER_ID, DEFAULT_ADMINS

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["ftm_ytdl_bot"]
users_col = db["users"]
admins_col = db["admins"]

# Ensure Default Admins Exist
for admin_id in DEFAULT_ADMINS:
    admins_col.update_one({"user_id": admin_id}, {"$set": {"role": "admin"}}, upsert=True)

# Function to Add a Premium User
def add_premium_user(user_id, plan, expiry_date):
    users_col.update_one({"user_id": user_id}, {"$set": {"plan": plan, "expiry": expiry_date}}, upsert=True)

# Function to Remove a Premium User
def remove_premium_user(user_id):
    users_col.delete_one({"user_id": user_id})

# Function to Check User Plan
def get_plan(user_id):
    user = users_col.find_one({"user_id": user_id})
    return user["plan"] if user and "plan" in user else "Free"

# Function to Get Expiry Date
def get_expiry(user_id):
    user = users_col.find_one({"user_id": user_id})
    return user["expiry"] if user and "expiry" in user else "No Plan"

# Function to Add Admin
def add_admin(user_id):
    admins_col.update_one({"user_id": user_id}, {"$set": {"role": "admin"}}, upsert=True)

# Function to Remove Admin
def remove_admin(user_id):
    if user_id in DEFAULT_ADMINS:
        return False  # Cannot remove default admins
    admins_col.delete_one({"user_id": user_id})
    return True

# Function to Check if User is Admin
def is_admin(_, __, message):
    return admins_col.find_one({"user_id": message.from_user.id}) is not None

# Function to Get List of Admins
def get_admins():
    return [admin["user_id"] for admin in admins_col.find({}, {"_id": 0, "user_id": 1})]
