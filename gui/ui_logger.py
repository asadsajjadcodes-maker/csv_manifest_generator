import logging
from PySide6.QtCore import QObject, Signal


class GuiHandler(QObject, logging.Handler):

    """
    Custom logging handler that routes log messages to PySide6 GUI signals.
    Inherits from QObject to support Qt Signals and logging.Handler to receive log records.
    """
    # Qt Signal emitted whenever a log record is processed
    log_message = Signal(str)

    def __init__(self):
        # Initialize parent classes
        QObject.__init__(self)
        logging.Handler.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Formats the log record and emits the message via Qt Signal.
        """
        message = self.format(record)
        self.log_message.emit(message)