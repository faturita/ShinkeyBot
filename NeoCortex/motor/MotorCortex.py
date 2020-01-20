import serial


class MotorCortex:
    def __init__(self, *, connection, speed = 120):
        # TODO: not used now. To be done
        self.connection = connection
        self.speed = speed

    def stop(self):
        self.connection.send(b'1')

    def move_forward(self):
        #self.connection.send(bytes('A3'+'{:3d}'.format(self.speed),'ascii'))
        self.connection.send(b'2')

    def move_backwards(self):
        self.connection.send(b'3')
    
    def move_left(self):
        self.connection.send(b'5')

    def move_right(self):
        self.connection.send(b'4')

    def increase_speed(self):
        self.speed = self.speed + 10
        self.connection.send(b'-')
    
    def decrease_speed(self):
        self.speed = self.speed - 10
        self.connection.send(b'+')

