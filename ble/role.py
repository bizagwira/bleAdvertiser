class BleRole(object):
    def __init__(self, connection, params):
        self.serial = connection
        self.params = params

    def start(self):
        pass

    def stop(self):
        pass

    def config(self, attrname, value):
        pass