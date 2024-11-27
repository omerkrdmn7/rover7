#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import threading

class ReactiveRobot:
    def _init_(self):
        # Node başlatılıyor
        rospy.init_node('reactive_robot_node', anonymous=True)

        # Twist mesajları için bir publisher oluşturuluyor
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Robot hareket sürelerini kontrol etmek için değişkenler
        self.start_time = None
        self.is_active = False

        # Klavye kontrolü için ayrı bir thread başlatılıyor
        self.keyboard_thread = threading.Thread(target=self.keyboard_control)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()

        rospy.loginfo("Reactive Robot node started. Use keyboard controls (w, s, a, d).")

    def keyboard_control(self):
        """Klavye girdisi ile robotun kontrolünü sağlar."""
        while not rospy.is_shutdown():
            key = input("Enter w (forward), s (stop), a (left), d (right): ").lower()
            twist = Twist()

            if key == 'w':
                twist.linear.x = 0.5  # İleri hareket
                rospy.loginfo("Started moving forward.")
            elif key == 's':
                twist.linear.x = 0.0  # Dur
                rospy.loginfo("Stopped.")
            elif key == 'a':
                twist.angular.z = 0.5  # Sol dönüş
                rospy.loginfo("Started rotating left.")
            elif key == 'd':
                twist.angular.z = -0.5  # Sağ dönüş
                rospy.loginfo("Started rotating right.")
            else:
                rospy.loginfo("Invalid key pressed. Use w, s, a, d.")

            self.pub.publish(twist)

            # Robot harekete geçtiğinde zaman başlatılır
            if not self.is_active and (twist.linear.x != 0.0 or twist.angular.z != 0.0):
                self.is_active = True
                self.start_time = rospy.Time.now()
                rospy.loginfo("Robot is active. Countdown started.")

    def monitor_robot(self):
        """Robotun çalışma süresini izler ve 60 saniye sonra hareketi durdurur."""
        rate = rospy.Rate(10)  # 10 Hz döngü
        while not rospy.is_shutdown():
            if self.is_active and self.start_time:
                elapsed_time = (rospy.Time.now() - self.start_time).to_sec()

                if elapsed_time >= 60:
                    rospy.loginfo("Time limit reached. Stopping...")
                    self.stop_robot()
                    rospy.signal_shutdown("60 seconds completed. Node shutting down.")

            rate.sleep()

    def stop_robot(self):
        """Robotun hareketini durdurur."""
        twist = Twist()
        self.pub.publish(twist)
        rospy.loginfo("Robot stopped.")

if __name__ == "reactive_robot_node":
    try:
        robot = ReactiveRobot()
        robot.monitor_robot()
    except rospy.ROSInterruptException:
        pass
