from datetime import datetime


def create_unique_social_id_number():
    return datetime.now().strftime("%r")
