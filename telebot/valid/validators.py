import os
from dotenv import load_dotenv
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))
def validate_age(age: str):
    if not age.isdigit():
        return "Введите число"
    if not 16 <= int(age) <= 50:
        return "Возраст должен быть от 16 до 50"
    return None
def validate_name(name: str):
    name = name.strip()
    if not name.isalpha():
        return "Имя должно содержать только буквы.🫸"
    if len(name) < 3 or len(name) > 20:
        return "Имя должно быть от 3 до 30 символов.🫸"
    name.capitalize()
    return None
def is_admin(user_id: int):
    return user_id == ADMIN_ID