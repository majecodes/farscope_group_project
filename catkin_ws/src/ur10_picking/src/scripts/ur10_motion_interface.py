#!/usr/bin/env python
import rospy
import sys
import moveit_commander
from geometry_msgs.msg import Pose
from ur10_picking.msg import poseMessage

class PoseTalker():

    def __init__(self, publisher_name):

        self.pub = rospy.Publisher(publisher_name, poseMessage, queue_size=10)

    def send(self, pose, incremental=False):
        pose_msg = poseMessage()
        pose_msg.pose = pose
        pose_msg.incremental = incremental
        self.pub.publish(pose_msg)


class MoveitInterface():
    
    def __init__(self):
        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node('moveit_interface', anonymous=False)
        
        self.robot = moveit_commander.RobotCommander()
        self.scene = moveit_commander.PlanningSceneInterface()
        self.move_group = moveit_commander.MoveGroupCommander('manipulator')
        
        self.pose_talker = PoseTalker('/moveit_interface/cartesian_pose_feedback')
        self.sub = rospy.Subscriber('/pipeline/next_cartesian_pose', poseMessage, self.move_to_pose)

        self.move_group.set_joint_value_target([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.move_group.go(wait=True)
        self.move_group.stop()
        self.move_group.clear_pose_targets()

    def move_to_pose(self, pose_message):

        if pose_message.incremental:
            pose = self.move_group.get_current_pose()
            pose.x += pose_message.pose.position.x
            pose.y += pose_message.pose.position.y
            pose.z += pose_message.pose.position.z
        else:
            pose = pose_message.pose

        self.move_group.set_pose_target(pose)
        self.move_group.go(wait=True)
        self.move_group.stop()
        self.move_group.clear_pose_targets()

    def feedback(self):
    
        pose = self.move_group.get_current_pose().pose
        self.pose_talker.send(pose)


if __name__ == "__main__":

    interface = MoveitInterface()
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        interface.feedback()
        rate.sleep()

