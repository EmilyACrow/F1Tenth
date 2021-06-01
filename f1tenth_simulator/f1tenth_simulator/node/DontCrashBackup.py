#!/usr/bin/env python
# coding: utf-8

#Bastardization of UVA steering_control code from f1/10 2018 competition, see here
#https://github.com/f1tenth/F110CPSWeek2018/blob/master/UVA/src/steering_control.py

# In[ ]:


import rospy
import std_msgs.msg #import Float64, String
from ackermann_msgs.msg import AckermannDriveStamped
from ackermann_msgs.msg import AckermannDrive
from sensor_msgs.msg import LaserScan
import math

#include ackermann_msgs/AckermannDrive, mav_msgs/Odometry

max_speed = 0.5                     #arbitrary value, set properly in constructor
max_steering_angle = 0.15           #arbitrary value, set properly in constructor
prev_angle = 0.0
points_per_degree = 1080/360        # number of points per degree
drive_topic = rospy.get_param('~/drive_topic', '/dont_crash_drive')
drive_pub = rospy.Publisher(drive_topic,AckermannDriveStamped, queue_size = 1)  

prev_error = 0.0
prev_wall_dist = 0.0
prev_alpha = 0.0

alpha = 0.0

def DontCrash():
    drive_topic = rospy.get_param("~/drive",'/drive')
    odom_topic = rospy.get_param("~/odom_topic",'/odom_topic')
    
    max_speed = rospy.get_param("~/max_speed", 7.0)
    max_steering_angle = rospy.get_param("~/max_steering_angle", 0.4189)

def getRange(data,angle):
	if angle > 270:
		angle = 270
	index = len(data.ranges)*angle/angle_range
	dist = data.ranges[int(index)]
	if math.isinf(dist) or math.isnan(dist):
		return 10.0
	return data.ranges[int(index)]


# Basic wall-follow prototype
# just tries to keep 2 perpendicular rays at the same range
# return a steering_angle
'''
def basic_wall_follow(data, distance, left_side):
    ray_a = 135
    ray_b = 45
    if left_side:
        ray_a = 225
        ray_b = 315
    
    range_a = data.ranges[ray_a * points_per_degree] 
    range_b = data.ranges[ray_b * points_per_degree]
    range_a = distance if range_a > distance else range_a
    range_b = distance if range_b > distance else range_b
    
    steering_angle = 0.0
    if range_a > range_b:
        steering_angle = max_steering_angle * -1
        if left_side:
            steering_angle = max_steering_angle
    elif range_b < range_a:
        steering_angle = max_steering_angle
        if left_side:
            steering_angle = max_steering_angle * -1
    return steering_angle
'''

'''
# Finds the angle between a side wall and the side of the car
# parameters:
# data: LIDAR data
# theta: angle between ray_a (leading ray) and ray_b (trailing ray)
# distance: Distance to maintain from the wall
# left_side: Boolean, true if checking left wall, false if checking right wall
def wall_follow_error(data, theta, distance, left_side):
    if left_side:
        start_point = 1080/2
        #the angle that goes perpendiuclar to direction the car is pointing, depending on left or right side
        car_perp_angle = 270
        #multiplier to get values that are closer to the front of the car
        front_multiplier = -1
    else:
        start_point = 0
        car_perp_angle = 90
        front_multiplier = 1
        
    end_point = 1080/2 + start_point
    side_ranges = list(data.ranges[start_point:end_point]
    
    closest_point_idx = index(min(side_ranges))

    idx_a = (car_perp_angle + (theta * front_multiplier)) * points_per_degree
    dist_a = side_ranges(idx_a)
    dist_b = side_ranges(car_perp_angle * points_per_degree)
    
    alpha_calc = math.atan((dist_a * math.cos(theta * front_multiplier) - dist_b)/(dist_a * math.sin(theta * front_multiplier)
    alpha_meas = car_per_angle - (closest_point_idx * points_per_degree)
    
    
    wall_dist_calc = dist_b * math.cos(alpha_calc)
    wall_dist_meas = side_ranges(closest_point_idx)
    
    desired_alpha = 0.0
    desired_dist = distance
    
    steering_angle = steering_angle -  
    '''
def followRight(data,desired_trajectory):
	global alpha
	a = getRange(data,45)
	b = getRange(data,80)
	swing = math.radians(35)
	alpha = math.atan((a*math.cos(swing)-b)/(a*math.sin(swing)))
	print "Alpha right",math.degrees(alpha)
	curr_dist = b*math.cos(alpha)
	future_dist = curr_dist+car_length*math.sin(alpha)
	print "Right : ",future_dist
	error = desired_trajectory - future_dist
	print "Error : ",error
	return error

def followLeft(data,desired_trajectory):
	global alpha
	a = getRange(data,190)
	b = getRange(data,225)
	swing = math.radians(35)
	alpha = -math.atan((a*math.cos(swing)-b)/(a*math.sin(swing)))
	print "Alpha left",math.degrees(alpha)
	curr_dist = b*math.cos(alpha)
	future_dist = curr_dist-car_length*math.sin(alpha)
	print "Left : ",future_dist
	error = future_dist - desired_trajectory
	return error

def obs_particles(data, start, end, distance):
    num_points = 0
    obs = 0
    start_point = 1080/2 - (90 - start) * points_per_degree
    end_point = 1080/2 - (90 - end) * points_per_degree
    front_values = list(data.ranges[start_point:end_point])
    counter = 0
    for i in front_values:
        if i <= distance:
            num_points = num_points + 1
        counter = counter + 1;
    #print "counter: ", counter
    return front_values,num_points

def obs_decide(data):
	start = 80
	end = 100
	distance = 2.0
	values,num_points = obs_particles(data,start,end,distance)
	#print "In range", values
	obs_start_point = 0
	obs_end_point = 0
	#print "Num Points", num_points
	if num_points < 3:
		#print(num_points)
		return -1,-1
	elif num_points <= 15:
		#print "normal obstacle"
		k =-1
		for i in values:
			k = k + 1
			if i<= (distance):
				obs_start_point = k + start
				break
		k = -1
		for i in reversed(values):
			k = k+1
			if i<= (distance):
				obs_end_point = end - k
				break
		if obs_start_point <= (start+1):
			#print "Start point extended"
			start1 = start - 10
			end1 = start
			obs_start_point = start1
			values,num_points = obs_particles(data,start1,end1,distance)
			#print "Right extended", values
			k = 0
			for i in reversed(values):
				k = k + 1
				if i > (distance):
					obs_start_point = end1 - k
					break
		if obs_end_point >= (end-1):
			start2 = end + 1
			end2 = end + 10
			obs_end_point = end2
			values,num_points = obs_particles(data,start2,end2,distance)
			#print "Right extended", values
			k = len(values)-1
			for i in values:
				k = k-1
				if i > (distance):
					obs_end_point = end2 - k
					break
		#print "Start Point", obs_start_point
		#print "End Point", obs_end_point
		return obs_start_point,obs_end_point
	else:
		#print "wide obstacle"
		start1 = start - 10
		end1 = start - 1
		obs_start_point = end1 + 3
		values,num_points = obs_particles(data,start1,end1,distance)
		k = len(values) - 1
		for i in reversed(values):
			k = k - 1
			if i > (distance):
				obs_start_point = k + start1
				break
		start2 = end + 1
		end2 = end + 10
		obs_end_point = start2 - 3
		values,num_points = obs_particles(data,start2,end2,distance)
		k = len(values)-1
		for i in values:
			k = k-1
			if i > (distance):
				obs_end_point = end2 - k
				break
		#print "wall"
		if obs_start_point <= start1+1:
			obs_start_point = -1
		if obs_end_point >= end2-1:
			obs_end_point = -1
		#print "Start Point", obs_start_point
		#print "End Point", obs_end_point
		return obs_start_point,obs_end_point
    
def test_callback(data):
    ack_msg = AckermannDriveStamped()
    
    #Speed: Set constant half max speed
    ack_msg.drive.speed = max_speed

    start_point,end_point = obs_decide(data)

    if end_point - start_point > (10 * points_per_degree):  
        #If the obstacle takes more than 10 degrees of the scan in points, stop the car to avoid crash
        #value chosen as placeholder, needs tuning
        ack_msg.drive.steering_angle = 0.0
        ack_msg.drive.speed = 0.0
    else:
        ack_msg.drive.steering_angle = basic_wall_follow(data, 1.5, False)
    
    #reset prev_angle
    prev_angle = ack_msg.drive.steering_angle
    
    ack_msg.header.stamp = rospy.Time.now()
    
    drive_pub.publish(ack_msg)

def laser_callback(data):
    ack_msg = AckermannDriveStamped()
    
    #Speed: Set constant half max speed
    ack_msg.drive.speed = max_speed

    

    start_point,end_point = obs_decide(data)
    
	
    if start_point and end_point == -1:         #way ahead is clear
        ack_msg.drive.steering_angle = 0.0
    elif end_point - start_point > (10 * points_per_degree):  
        #If the obstacle takes more than 10 degrees of the scan in points, stop the car to avoid crash
        #value chosen as placeholder, needs tuning
        ack_msg.drive.steering_angle = 0.0
        ack_msg.drive.speed = 0.0
    else:
        if end_point - start_point < 1080/2:    #center of obstacle is to the left of car center
            ack_msg.drive.steering_angle = max_steering_angle
        else:
            ack_msg.drive.steering_angle = max_steering_angle * -1

    
    #reset prev_angle
    prev_angle = ack_msg.drive.steering_angle
    
    ack_msg.header.stamp = rospy.Time.now()
    
    drive_pub.publish(ack_msg)
	

if __name__ == '__main__':
    rospy.init_node('dont_crash')
    rospy.Subscriber("scan", LaserScan, test_callback)
      
    dont_crash = DontCrash()
    rospy.spin()
