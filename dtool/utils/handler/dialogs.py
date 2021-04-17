import datetime
from time import sleep
import os


class Logger:

    # LEVEL = {
    #     0: 'success',
    #     1: 'error',
    #     2:  'warning',
    #     3: 'info'
    # }
    COLORS = {
        'Task': '\x1b[34m',
        'SUCCESS': '\x1b[32m',
        'ERROR': '\x1b[31m',
        'WARNING': '\x1b[33m',
        'INFO': '\x1b[0;2m',
    }
    RESET = '\x1b[0m'
    TIME_COLOR = COLORS['INFO']

    def __init__(self, settings):
        self.settings = settings
        self.__message = 'Logger'
        self.__log_level = ''
        self.__time_enabled = False
        self.TIME = settings.logger_times

    def success(self, msg, time=False, end='\n', start=''):
        self.__message = msg
        self.__time_enabled = time
        self.__log_level = '    SUCCESS'
        self.log(end=end, start=start)

    def info(self, msg, time=False, end='\n', start=''):
        self.__message = msg
        self.__time_enabled = time
        self.__log_level = '    INFO'
        self.log(end=end, start=start)

    def warning(self, msg, time=False, end='\n', start=''):
        self.__message = msg
        self.__time_enabled = time
        self.__log_level = '    WARNING'
        self.log(end=end, start=start)

    def error(self, msg, time=False, end='\n', start=''):
        self.__message = msg
        self.__time_enabled = time
        self.__log_level = '    ERROR'
        self.log(end=end, start=start)

    def task(self, msg, time=False, end='\n', start=''):
        self.__message = msg
        self.__time_enabled = time
        self.__log_level = '  Task'
        self.log(end=end, start=start)

    def log(self, msg=False, end='\n', start=''):
        log_time = self.settings.logger_times['NORMAL']
        if not isinstance(msg, str):
            color = self.COLORS[self.__log_level.strip()]

            message = ""
            if self.__time_enabled:
                message = f"{start}{self.TIME_COLOR}{self.__get_time}{self.RESET} -> "
                self.__log_level = self.__log_level.strip()

            if self.__log_level.strip() == 'INFO':
                message = f"{start}{message}{color}{self.__log_level}:{self.RESET} {self.__message}"
            else:
                message = f"{start}{message}{color}{self.__log_level}: {self.__message}{self.RESET}"

            log_time = self.settings.logger_times[self.__log_level.strip()]
        else:
            message = f"{self.COLORS['INFO']}{start}{msg}{self.RESET}"

        print(message, end=end)
        sleep(log_time)
        self.__log_level = ''
        self.line = Logger.line

    def cancel(self, msg, start='', level='INFO'):
        """
        Create a Cancel/Exit dialog, this should be used,
        while program is running task

        :param msg: Dialog message
        :param start: ''
        :param level: Give colored output based on level 'INFO', 'WARNING', 'ERROR'
        
        """
        keys = "([y]/n)? "
        msg = f"{start}{self.COLORS[level]}{msg} {keys}{self.RESET}"
        try:
            result = input(msg)
            if result in ('y', '', 'Y'):
                return True
            else:
                return False
            
        except (KeyboardInterrupt, EOFError):
            return True

    def ask_user(self, msg, start='', level='INFO', keys='([y]/n)? '):
        """
        Create a Cancel/Exit dialog, this should be used,
        while program is running task

        :param msg: Dialog message
        :param start: ''
        :param level: Give colored output based on level 'INFO', 'WARNING', 'ERROR'
        
        """
        msg = f"{start}{self.COLORS[level]}{msg} {keys}{self.RESET}"
        try:
            result = input(msg)
            if result in ('y', '', 'Y'):
                return True
            else:
                return False
            
        except (KeyboardInterrupt, EOFError):
            return True

    def write_log(self, file_name, data, fmode='a', time=True):
        with open(file_name, fmode) as f:
            try:
                for log_line in data:
                    if time:
                        log_line = self.__get_time + ' - ' + log_line
                    f.writelines(log_line + '\n')
            except (ValueError, TypeError):
                f.write(f"{self.__get_time} - Log error: Data error, 1unknown data")

    @property
    def __get_time(self):
        return datetime.datetime.now().strftime('At %H:%M:%Ss')

    @staticmethod
    def line(fill_char='-', spaces=0, end='\n', start=''):
        terminal_size = os.get_terminal_size().columns
        output = ''
        if spaces > 0:
            output = f"{' ' * spaces}"
            terminal_size -= spaces * 2 + 1

        for i in range(terminal_size):
            output += fill_char

        print(f"{start}{output}", end=end)
