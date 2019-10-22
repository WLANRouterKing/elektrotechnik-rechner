import os
import datetime


class System:

    def write_file(self, path, content, overwrite):
        if not overwrite:
            f = open(path, "a+", encoding='utf-8')
        else:
            f = open(path, "wb")
        f.write(content)
        f.close()

    def read_file(self, path):
        f = open(path, "rb")
        content = f.read()
        f.close()
        return content

    def file_exists(self, path):
        return os.path.isfile(path)

    def log(self, data):
        message = datetime.datetime.now().strftime("d.m.Y H:i:s")
        message += " " + data + "\n"
        self.write_file("debug.log", message, False)

    def log_exception(self, data):
        message = "Ausnahme: " + format(data)
        self.log(message)
