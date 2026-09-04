import logging
from gui.ui_logger import GuiHandler
def setup_logger(name: str) -> logging.Logger:
    # Creates and configures a coustom logger instance.

    # Create a logger instance associated with provided module name 
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logger is called multiple times 
    if not logger.handlers:
        # Set console handler 
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # gui logger handler 
        gui_handler = GuiHandler()
        gui_handler.setLevel(logging.INFO)

        # file handler
        file_handler = logging.FileHandler("logs/app.log", mode="a", encoding="utf-8")
        file_handler.setLevel(logging.INFO)


        # Set console handler format 
        console_formmater = logging.Formatter(
            fmt= "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # set gui handler 
        gui_formmater = logging.Formatter(
            fmt= "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # set gui handler 
        file_formmater = logging.Formatter(
            fmt= "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Apply the formmater to the console handler 
        console_handler.setFormatter(console_formmater)
        gui_handler.setFormatter(gui_formmater)
        file_handler.setFormatter(file_formmater)

        # Attach the console handler to the logger instance 
        logger.addHandler(console_handler)
        logger.addHandler(gui_handler)
        logger.addHandler(file_handler)
    return logger