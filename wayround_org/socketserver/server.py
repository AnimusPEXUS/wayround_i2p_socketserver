
"""
I don't like socketserver realization in PSL, so here is My version
"""

import socket
import threading
import logging
import datetime
import time
import select
import ssl


def _ssfw(
        func,
        transaction_id,
        serv,
        serv_stop_event,
        sock,
        addr
        ):
    """
    This function is simply a wrapper for adding possible actions around func
    call
    """
    func(
        transaction_id,
        serv,
        serv_stop_event,
        sock,
        addr
        )
    return


class SSLConfig:

    def __init__(self, data_dict):
        self.keyfile = None
        if 'keyfile' in data_dict:
            self.keyfile = data_dict['keyfile']

        self.certfile = data_dict['certfile']
        return

    def repr_as_text(self):
        ret = "keyfile: {}, certfile: {}".format(
            self.keyfile,
            self.certfile
            )
        return ret


class SocketServer:

    def __init__(
            self,
            sock,
            func,
            unique_transaction_id_generator=datetime.datetime.utcnow,
            ssl_config=None,
            thread_name=None
            ):
        """

        The socket must be bound to an address and listening for connections.
        You can pass None here, but be sure to use set_sock method
        before start method

        This class is designated to work with non-blocking sockets.
        Work with blocking sockets - not tested.

        func - must be callable and accept arguments:
            utc_datetime - probably taken from datetime.utcnow()
                (utc_datetime is meant to be used as unique transaction
                 identifier, and ought to be passed to http (or any other
                 server) and from there to other functionalities which might
                 require such a thing)
                 (I don't like time zone gradations: I think they are only
                  adding trash to information field. life can be mutch easier
                  if everybody will use utc. so this is default.
                  but You can specify `unique_transaction_id_generator'
                  to override this.
                  )
            serv - for this server instance
            serv_stop_event - threading.Event for server stop
            sock - for new socket
            addr - for remote address
        """

        if not callable(func):
            raise ValueError("`func' must be callable")

        if not ssl_config is None and not isinstance(ssl_config, SSLConfig):
            raise TypeError(
                "`ssl_config' must be of type SSLConfig"
                )

        if (unique_transaction_id_generator is not None
                and not callable(unique_transaction_id_generator)):
            raise ValueError(
                "`unique_transaction_id_generator' must be callable if defined"
                )

        self.ssl_config = ssl_config

        self.thread_name = thread_name

        self._func = func

        self._trans_id_gen = unique_transaction_id_generator

        self._server_stop_flag = threading.Event()
        self._server_stop_flag.clear()

        self._acceptor_thread = None

        self.set_sock(sock)

        return

    def get_is_ssl_config_defined(self):
        return isinstance(self.ssl_config, SSLConfig)

    def wrap(self):

        if not self.get_is_ssl_config_defined():
            raise Exception("`ssl_config' is invalid")

        self.sock = ssl.wrap_socket(
            self.sock,
            server_side=True,

            keyfile=self.ssl_config.keyfile,
            certfile=self.ssl_config.certfile,

            # TODO: need conf
            # cert_reqs=CERT_NONE,
            # ssl_version={see docs},
            # ciphers=None

            # ca_certs=None,
            # do_handshake_on_connect=True,
            # suppress_ragged_eofs=True,
            do_handshake_on_connect=False
            )
        return

    def unwrap(self):
        self.sock = self.sock.unwrap()
        return

    def set_sock(self, sock):
        """
        If You need to change socket after construction, but before start
        """
        self.sock = sock
        return

    def get_sock(self):
        return self.sock

    def start(self):
        if self._acceptor_thread is None:
            self._server_stop_flag.clear()
            self._acceptor_thread = threading.Thread(
                name=self.thread_name,
                target=self._acceptor_thread_method
                )
            self._acceptor_thread.start()
        return

    def wait(self):
        while True:
            if self._acceptor_thread is None:
                break
            time.sleep(1)
        return

    def stop(self):
        self._server_stop_flag.set()

        if self._acceptor_thread:
            self._acceptor_thread.join()

        return

    def _acceptor_thread_method(self):

        while True:

            if self._server_stop_flag.is_set():
                break

            selres = select.select([self.sock], [], [], 0.5)

            if len(selres[0]) != 0:
                try:
                    res = self.sock.accept()
                except OSError as err:
                    if err.errno in [9, 22]:
                        break
                    else:
                        raise
                # NOTE: do not make child sockets non-blocking here.
                #       do them so in threads
                # res[0].setblocking(False)

                thr = threading.Thread(
                    name="_acceptor_thread_method child",
                    target=_ssfw,
                    args=(
                        self._func,
                        self._trans_id_gen(),
                        self,
                        self._server_stop_flag,
                        res[0],
                        res[1]
                        )
                    )
                thr.start()

        self._acceptor_thread = None
        return
