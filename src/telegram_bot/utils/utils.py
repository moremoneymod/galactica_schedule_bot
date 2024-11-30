from typing import Dict


def create_lessons_message(day: str, lessons: Dict, time: Dict) -> str:
    message = f"<b>{day.upper()}</b>\n\n"
    if lessons is None:
        message += f"<b>Пар нет</b>"
    else:
        for lesson in lessons.items():
            message += f"<b>{lesson[0]} ({time[lesson[0]]})</b>  {lesson[1]}\n\n"
    return message
