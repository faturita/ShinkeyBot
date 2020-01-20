import serial

CMD_STOP = b'x'
CMD_FORWARD = b'w'
CMD_BACKWARDS = b's'
CMD_MOVE_RIGHT = b'd'
CMD_MOVE_LEFT = b'a'
CMD_ROTATE_RIGHT = b'l'
CMD_ROTATE_LEFT = b'k'

class SerialMotorController:
    def __init__(self, *, connection, speed = 120):
        # TODO: not used now. To be done
        self.connection = connection
        self.speed = speed

    def stop(self):
        self.connection.send(CMD_STOP)

    def move_forward(self):
        self.connection.send(CMD_FORWARD)

    def move_backwards(self):
        self.connection.send(CMD_BACKWARDS)
    
    def move_left(self):
        self.connection.send(CMD_MOVE_LEFT)

    def move_right(self):
        self.connection.send(CMD_MOVE_RIGHT)

    def rotate_left(self):
        self.connection.send(CMD_ROTATE_LEFT)

    def rotate_right(self):
        self.connection.send(CMD_ROTATE_RIGHT)

    def increase_speed(self):
        self.speed = self.speed + 10
    
    def decrease_speed(self):
        self.speed = self.speed - 10