
class SocketService:
    """
    Example of socket service code

    this class (or it's instances) is not intended for direct initialization.
    it's created, used and destroyed by SocketServicePool class instance
    """

    def __init__(self, socket_data_dict, callable_target):
        raise Exception("this is not working code. this is only example")
        return

    def start(self):
        return

    def stop(self):
        return

    def wait(self):
        return


class SocketServicePool2:

    def __init__(self, socket_list=None):
        if socket_list is None:
            socket_list = []

        if not isinstance(socket_list, list):
            raise TypeError("`socket_list' must be list")

        self._socket_pool = socket_list
        return

    def get_socket_pool(self):
        return self._socket_pool

    def start(self):
        for i in self._socket_pool:
            i.start()
        return

    def stop(self):
        for i in self._socket_pool:
            i.stop()
        return

    def wait(self):
        for i in self._socket_pool:
            i.wait()
        return

    def append(self, value):
        self._socket_pool.append(value)
        return


class SocketServicePool:

    def __init__(self, cfg, callable_target, cls_to_use=SocketService):
        self._socket_pool = SocketServicePool2()
        for i in cfg['sockets']:
            self._socket_pool.append(cls_to_use(i, callable_target))
        return

    def get_socket_pool(self):
        return self._socket_pool.get_socket_pool()

    def start(self):
        self._socket_pool.start()
        return

    def stop(self):
        self._socket_pool.stop()
        return

    def wait(self):
        self._socket_pool.wait()
        return
