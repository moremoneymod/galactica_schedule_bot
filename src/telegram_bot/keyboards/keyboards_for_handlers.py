from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_keyboard_for_study_type():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Очная форма обучения", callback_data="full_time")
    keyboard.button(text="Заочная форма обучения", callback_data="part_time")
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


def create_keyboard_for_study_groups(study_groups):
    keyboard = InlineKeyboardBuilder()
    for group in study_groups:
        keyboard.button(text=group, callback_data=f"ftgroup_{group}")
    keyboard.button(text="Назад", callback_data="select_type")
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


def create_keyboard_for_study_days(study_days: list[str], study_group: str, study_type: str):
    keyboard = InlineKeyboardBuilder()
    for day in study_days:
        keyboard.button(text=day, callback_data=f"{study_type}{study_group}!d_{day}")
    keyboard.button(text="Назад", callback_data="full_time")
    keyboard.adjust(1, 1)
    return keyboard.as_markup()


def create_keyboard_for_selected_study_day(callback_data: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Назад", callback_data=callback_data)
    keyboard.adjust(1, 1)
    return keyboard.as_markup()