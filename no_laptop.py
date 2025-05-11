import rclpy
import re
from rclpy.node import Node
from geometry_msgs.msg import Twist
import pygame
from pygame.locals import *

pygame.init()

pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
deadzone = 0.1

class TrajectoryPublisher(Node):

    msg = Twist()
    def __init__(self):
        super().__init__('trajectory_publisher')
        # TODO: Create a publisher of type Twist
        # Your code here
        self.cmd_vel_pub_ = self.create_publisher(Twist,"trajectory", 10)
        self.timer = self.create_timer(0.05, self.cmd_acquisition)
        self.get_logger().info('Publisher node has been started.')

        # TODO: Create a loop here to ask users a prompt and send messages accordingly

    def cmd_acquisition(self):

        for event in pygame.event.get() :
            if event.type == JOYAXISMOTION :
                if event.axis == 0 and abs(event.value) > deadzone :
                    self.msg.angular.y = 90+event.value*90

                # if event.axis == 4 : #left trigger
                #     self.msg.linear.x = -(event.value+1)*255/2

                if event.axis == 5 : #right trigger
                    self.msg.linear.x = 255*(event.value+1)/2
                    print(f"{self.msg.linear.x=}")

            # if event.type == JOYBUTTONDOWN :
            #     if event.button == 4 : #left_bumper down
            #         print("left_bumper_down")
            #     if event.button == 5 : #right bumper down
            #         print("right_bumper_down")

            # if event.type == JOYBUTTONUP :
            #     if event.button == 4 : #left_bumper up
            #         print("left_bumper_up")
            #     if event.button == 5 : #right_bumper up
            #         print("right_bumper_up")

        self.cmd_vel_pub_.publish(self.msg)
        #pass

def main(args=None):
    rclpy.init(args=args)   # Init ROS python
    node = TrajectoryPublisher()  # Create a Node instance
    rclpy.spin(node)  # Run the node in a Thread
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
