import socket
import cStringIO
import notifier

class Socket:
    def __init__(self, socket):
        self.socket     = socket
        self.socket.setblocking(0)
        self.closed     = False
        self.__read_nf  = False
        self.__write_nf = False
        self.in_buffer  = cStringIO.StringIO()
        self.out_buffer = cStringIO.StringIO()
        self.out_fd     = None
        

    def write(self, data):
        """
        Send data to the client
        """
        if not self.__write_nf:
            notifier.addSocket(self.socket, self.__write_socket,
                               notifier.IO_OUT)
            self.__write_nf = True
        pos = self.out_buffer.tell()
        self.out_buffer.seek(0, 2)
        self.out_buffer.write(data)
        self.out_buffer.seek(pos, 0)


    def writefd(self, fd):
        """
        Send content of fd. This function is a hack. The content will
        be send after the normal write and it is not possible to send
        something after the fd. The fd will be closed after sending.
        """
        self.out_fd = fd
        if not self.__write_nf:
            notifier.addSocket(self.socket, self.__write_socket,
                               notifier.IO_OUT)
            self.__write_nf = True
        

    def __close(self):
        """
        close everything
        """
        self.socket.close()
        self.out_buffer.close()
        self.in_buffer.close()
        if self.out_fd:
            self.out_fd.close()
            self.out_fd = None
        self.__read_nf  = False
        self.__write_nf = False
        notifier.removeSocket(self.socket)

        
    def close(self):
        self.closed = True
        if not self.out_buffer.getvalue():
            # if need no more sending:
            self.__close()
        

    def set_condition(self, condition, callback):
        """
        Read from socket until 'condition' is True, than call 'callback'
        """
        self.__condition = condition
        self.__callback  = callback
        if not self.__read_nf:
            notifier.addSocket(self.socket, self.__read_socket)
            self.__read_nf = True


    def __read_socket(self, s):
        data = self.socket.recv(1000)
        if len(data) == 0:
            self.closed = True
        else:
            pos = self.in_buffer.tell()
            self.in_buffer.seek(0, 2)
            self.in_buffer.write(data)
            self.in_buffer.seek(pos, 0)

        if len(data) == 0 or self.__condition(self.in_buffer.getvalue()):
            self.__read_nf = False
            notifier.removeSocket(self.socket)
            self.__callback(self)
            return False
        return True


    def __write_socket(self, s):
        data = self.out_buffer.read(1000)
        if not data:
            if self.out_fd:
                self.out_buffer.close()
                self.out_buffer = self.out_fd
                self.out_fd = None
                return True
            self.__write_nf = False
            if self.closed:
                self.__close()
            return False
        try:
            self.socket.send(data)
            return True
        except socket.error, e:
            # This function has called because it is possible to send.
            # If it still doesn't work, the connection is broken
            self.__close()
            return False
        

    def readline(self, *args, **kwargs):
        return self.in_buffer.readline(*args, **kwargs)
