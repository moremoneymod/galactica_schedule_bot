import asyncio
import os
import logging

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
os.makedirs(LOG_DIR, exist_ok=True)


def configure_logging():
    """Настроить логирование для всех процессов (главного и дочерних)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(processName)s] [%(filename)s:%(lineno)d] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
            logging.StreamHandler()  # Чтобы видеть логи в консоли
        ],
    )


configure_logging()
logger = logging.getLogger(__name__)
logger.info("Логирование настроено.")

update_lock = asyncio.Lock()
update_complete = asyncio.Event()


def create_lessons_message(day: str, lessons: dict) -> str:
    message = f'<b>{day.upper()}</b>\n\n'
    if lessons is None:
        message += f'<b>Пар нет</b>'
    else:
        for lesson in lessons.items():
            message += f'<b>{lesson[0]}</b>  {lesson[1]}\n\n'
    return message
