import logging
from gui.ui_logger import GuiHandler

# Global instance
gui_handler = GuiHandler()
gui_formatter = logging.Formatter(fmt="%(levelname)s - %(message)s")
gui_handler.setFormatter(gui_formatter)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        console_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(filename)s]:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(gui_handler)

    return logger