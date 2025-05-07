import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial
import direction as dir

ser = serial.Serial('/dev/ttyACM0')

mode : bool = 0 # Mode = 0 --> Déplacement / Mode = 1 --> Bras

class TrajectorySubscriber(Node):

    def __init__(self):
        super().__init__('trajectory_subscriber')
        self.pose_subscriber = self.create_subscription(Twist, "trajectory", self.listener_callback, 10)
        # TODO: Create a subscriber of type Twist, that calls listener_callback
        # Your code here

        self.get_logger().info('Subscriber node has been started.')
        # self.position = {'x': 0.0, 'z': 0.0, 'ry': 0.0}

    def listener_callback(self, msg : Twist):
        self.get_logger().info(f'received {msg.linear.x=}')
        speed = (int(msg.linear.x)).to_bytes(1, 'little')
        angle = (int(msg.angular.y)).to_bytes(1, 'little')
        self.get_logger().info(f'Speed : {speed} | Angle : {angle}')
        
        if mode == 0:
            dir.Input_speed = speed
            dir.x_joystick = angle
            
            dir.calculate_transmission()
        
        transmit_direction()

        print(ser.readline())
        print(ser.readline())


def main(args=None):
    rclpy.init(args=args)
    node = TrajectorySubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    
    
def transmit_direction():
    data_dir = [dir.MotorFR, dir.MotorMR, dir.MotorBR, dir.MotorFL, dir.MotorML, 
                dir.MotorBL, dir.ServoFR, dir.ServoBR, dir.ServoFL, dir.ServoBL]   
    ser.write(bytes(data_dir))