from rplidar import RPLidar
import numpy as np
import time
from breezyslam.sensors import RPLidarA1 as LaserModel
from breezyslam.algorithms import RMHC_SLAM
import pygame
import os
from simple_pid import PID
import PiMotor
import RPi.GPIO as GPIO
from PIL import Image
import cv2
from datetime import datetime
import pickle
import Recording

black = (0, 0, 0)
red = (0, 0, 255)
green = (0, 255, 0)
yellow = (0, 255, 255)
blue = (255, 0, 0)
magenta = (255, 0, 255)
cyan = (255, 255, 0)
white = (255, 255, 255)
orange = (255, 69, 0)

# Ultrasonic Config
Ultrasonic_height = 1.04

# Name of Individual MOTORS
m1 = PiMotor.Motor("MOTOR1", 1)
m2 = PiMotor.Motor("MOTOR2", 1)
m3 = PiMotor.Motor("MOTOR3", 1)
m4 = PiMotor.Motor("MOTOR4", 1)

# To drive all motors together
motorAll = PiMotor.LinkedMotors(m1, m2, m3, m4)

# Names for Individual Arrows
ab = PiMotor.Arrow(1)
al = PiMotor.Arrow(2)
af = PiMotor.Arrow(3)
ar = PiMotor.Arrow(4)

# Map config
MAP_SIZE_PIXELS = 500
MAP_SIZE_METERS = 16
mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
display_surface = pygame.display.set_mode((MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))

# Lidar config
LIDAR_DEVICE = '/dev/ttyUSB0'
lidar = RPLidar(LIDAR_DEVICE)
info = lidar.get_info()
# print(info)
health = lidar.get_health()
print(health)

# Screen config
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
lcd = pygame.display.set_mode((MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
pygame.mouse.set_visible(False)
lcd.fill((0, 0, 0))
pygame.display.update()

# PID config
pid_velocity = PID(5, 0, 0, setpoint=1)
pid_theta = PID(300, 150, 30, setpoint=1)
speed_min_value = 0
speed_max_value = 25
pid_velocity.setpoint = 0  # mm/s
pid_velocity.output_limits = (speed_min_value, speed_max_value)
pid_theta.setpoint = 0  # rad
theta_max_rad_vel = 38
pid_theta.output_limits = (-theta_max_rad_vel, theta_max_rad_vel)

distance_to_GOAL_treshold = 0.1
DELTA_angle_treshold = 4.5

# measuring point counter
point_num = 0


def dis_connect_mu(connection, sock):
    print('disconnected')
    connection.close()
    sock.listen(1)
    connection, client_address = sock.accept()
    return sock, connection


def recording(connection, sock, point_num):
    print('sending ready message')
    connection.sendall(b'MU is Ready')
    print('recieving recording message')
    command = connection.recv(1024)
    # print('received "%s"' % command)
    cmd = pickle.loads(command)
    # cmd = command.decode('UTF-8')
    if cmd != '':
        # cmd = int(cmd)
        print('cmd = Recived')
    else:
        print('no more data ')
        # break
    print('Recording command')
    recording_time = cmd[1]
    recording_name = cmd[2]
    # print('Recording')
    print('sending begin recording message')
    connection.sendall(b'MU - Recording')

    ###add a counter instead of point_num###
    recording_path = recording_name + str(point_num + 1) + '.wav'

    Recording.measure(recording_time, recording_path)
    # print('Recording Complited')
    print('sending recording completed message')
    connection.sendall(b'MU - Recording Completed')
    print('sending recording file')

    print('sending end sending file message')

    # connection.send('end of file')

    # print('finished recording')
    # time.sleep(2)
    # connection,sock=send_files(connection,sock)

    
def send_files(connection, sock):
    for x in range(5):
        # path = './recording/'+recording_name
        path = './recording/Measure_point' + str(x + 1) + '.wav'
        with open(path, 'rb') as f:

            for l in f: connection.sendall(l)

            sock, connection = dis_connect_mu(connection, sock)
    return connection, sock


def measure_height(height_offset):
    """
    function for measuring height of the room using Ultrasonic sensor

    :param height_offset:  offset from the floor
    :return: averaged distance in meter
    """

    GPIO.setwarnings(False)
    trig = 29
    echo = 31

    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)

    avg_distance = 0
    num_of_measurements = 50

    for i in range(num_of_measurements):

        GPIO.output(trig, False)
        time.sleep(0.1)
        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        while GPIO.input(echo) == 0:
            pulse_start = time.time()

        while GPIO.input(echo) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 343) / 2
        avg_distance = avg_distance + distance

    avg_distance = avg_distance / num_of_measurements + height_offset

    return avg_distance


def gray(im):
    """
    function converts gray image format to colour
    for real time Lidar output plot with pygame
    :param im: image to convert
    :return: converted image
    """

    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret


def process_data(angles, distance, Rx, Ry):
    """

    :param angles:
    :param distance:
    :param Rx:
    :param Ry:
    :return:
    """
    lcd.fill((0, 0, 0))
    for ii, angle in enumerate(angles):
        if distance[ii] > 0:
            radians = angle * np.pi / 180.0
            xx = meter_to_pixel_distance(distance[ii] / 1000) * np.cos(radians)
            yy = meter_to_pixel_distance(distance[ii] / 1000) * np.sin(radians)
            point = (int(Rx + xx), int(Ry + yy))
            lcd.set_at(point, pygame.Color(255, 255, 255))
    pygame.display.update()


def pixel_to_meter_distance(distance_in_pixel):
    """

    :param distance_in_pixel:
    :return:
    """
    distance_in_meter = MAP_SIZE_METERS * distance_in_pixel / MAP_SIZE_PIXELS
    return distance_in_meter


def meter_to_pixel_distance(distance_in_meter):
    """

    :param distance_in_meter:
    :return:
    """
    distance_in_pixel = distance_in_meter * MAP_SIZE_PIXELS / MAP_SIZE_METERS
    return int(distance_in_pixel)


def line_intersection(line1, line2):
    """

    :param line1:
    :param line2:
    :return:
    """
    x1, y1, x2, y2, angle1 = line1
    a1, b1, a2, b2, angle2 = line2
    xdiff = [x1 - x2, a1 - a2]
    ydiff = [y1 - y2, b1 - b2]

    div = np.linalg.det(np.array([xdiff, ydiff]))
    if div == 0:
        print("lines do not intersect")
    else:
        d1 = np.linalg.det(np.array([[x1, y1], [x2, y2]]))
        d2 = np.linalg.det(np.array([[a1, b1], [a2, b2]]))
        d = [d1, d2]
        x = np.linalg.det(np.array([d, xdiff])) / div
        y = np.linalg.det(np.array([d, ydiff])) / div
        return int(x), int(y)


def dist_line_to_point(corner_p, new_p):
    """

    :param corner_p:
    :param new_p:
    :return:
    """
    return pixel_to_meter_distance(np.sqrt((np.mean(corner_p[..., 0]) - new_p[..., 0][0]) ** 2 +
                                           (np.mean(corner_p[..., 1]) - new_p[..., 1][0]) ** 2))


def dist_point_to_point(P1, P2):
    """

    :param P1:
    :param P2:
    :return:
    """
    return np.sqrt((P2[0] - P1[0]) ** 2 + (P2[1] - P1[1]) ** 2)


def find_corners(filter_input):
    """

    :param filter_input:
    :return:
    """
    point_treshold = 0.3  # Meter

    for i, line in enumerate(filter_input):
        if i == 0:
            first90 = True
            first_angle = line[0][4]
            angle_group_1 = line.copy()
        elif np.abs(line[0][4] - first_angle) < 10:
            angle_group_1 = np.append(angle_group_1, line, axis=0)
            first_angle = np.mean(angle_group_1[..., 4])
        elif np.abs(line[0][4] - first_angle) < 100 and np.abs(line[0][4] - first_angle) > 80 and first90:
            first90 = False
            angle_group_2 = line.copy()
        elif np.abs(line[0][4] - first_angle) < 100 and np.abs(line[0][4] - first_angle) > 80 and not first90:
            angle_group_2 = np.append(angle_group_2, line, axis=0)

    for i, line_1 in enumerate(angle_group_1):
        for line_2 in angle_group_2:
            [Corner_x, Corner_y] = line_intersection(line_1, line_2)
            new_point = np.array([[[Corner_x, Corner_y]]])
            if i == 0:
                corners = new_point.copy()
            else:
                corners = np.append(corners, new_point, axis=0)

    for i, point in enumerate(corners):
        if i == 0:
            P2_new_FLAG = True
            P3_new_FLAG = True
            P4_new_FLAG = True
            corner_1 = point.copy()
        else:
            if dist_line_to_point(corner_1, point) < point_treshold:
                corner_1 = np.append(corner_1, point, axis=0)
            else:
                if P2_new_FLAG:
                    P2_new_FLAG = False
                    corner_2 = point.copy()
                else:
                    if dist_line_to_point(corner_2, point) < point_treshold:
                        corner_2 = np.append(corner_2, point, axis=0)
                    else:
                        if P3_new_FLAG:
                            P3_new_FLAG = False
                            corner_3 = point.copy()
                        else:
                            if dist_line_to_point(corner_3, point) < point_treshold:
                                corner_3 = np.append(corner_3, point, axis=0)
                            else:
                                if P4_new_FLAG:
                                    P4_new_FLAG = False
                                    corner_4 = point.copy()
                                else:
                                    if dist_line_to_point(corner_4, point) < point_treshold:
                                        corner_4 = np.append(corner_4, point, axis=0)

    corner_1_mean = np.array([int(np.round(np.mean(corner_1[..., 0]))), int(np.round(np.mean(corner_1[..., 1])))])
    corner_2_mean = np.array([int(np.round(np.mean(corner_2[..., 0]))), int(np.round(np.mean(corner_2[..., 1])))])
    corner_3_mean = np.array([int(np.round(np.mean(corner_3[..., 0]))), int(np.round(np.mean(corner_3[..., 1])))])
    corner_4_mean = np.array([int(np.round(np.mean(corner_4[..., 0]))), int(np.round(np.mean(corner_4[..., 1])))])

    return corner_1_mean, corner_2_mean, corner_3_mean, corner_4_mean


def scan(No_itetations, MAP_name, display_FLAG):
    """

    :param No_itetations:
    :param MAP_name:
    :param display_FLAG:
    :return:
    """
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    previous_distances = []
    previous_angles = []

    lidar = RPLidar(LIDAR_DEVICE)
    info = lidar.get_info()
    print(info)
    health = lidar.get_health()
    print(health)

    for i, scan in enumerate(lidar.iter_scans()):
        if i == 0:
            # print('iteration_num = ' + str(i))
            time.sleep(0.1)
            vx = 0
            vy = 0
            previous_x = MAP_SIZE_METERS * 1000 / 2
            previous_y = MAP_SIZE_METERS * 1000 / 2
            previous_theta_rad = 0
            timetag = time.time()

        if i > 0:
            items = [item for item in scan]
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]
            # process_data(angles, distances)
            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > 100:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles = angles.copy()
            # If not adequate, use previous
            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)
            # Get current robot position
            x, y, theta = slam.getpos()
            slam.getmap(mapbytes)

            # Get current robot parameters
            theta_rad = theta * np.pi / 180
            dt = time.time() - timetag
            vx = (x - previous_x) / dt
            vy = (y - previous_y) / dt
            v = np.sqrt(np.power(vx, 2) + np.power(vy, 2))
            w = (theta_rad - previous_theta_rad) / dt
            previous_x = x
            previous_y = y
            previous_theta_rad = theta_rad
            timetag = time.time()
            # print('x = ' + str(np.round(x)) + '\ty = ' + str(np.round(y)) + '\ttheta = ' + str(np.round(theta)))

        # ------REAL TIME PLOT------
        if (not i % 10) and i != 0 and display_FLAG:
            R_loc_pixel_x = meter_to_pixel_distance(x / 1000)
            R_loc_pixel_y = meter_to_pixel_distance(y / 1000)
            graymap = np.array(
                [[mapbytes[x * MAP_SIZE_PIXELS + y] for y in range(MAP_SIZE_PIXELS)] for x in range(MAP_SIZE_PIXELS)],
                dtype=np.uint8)
            graymap_pygame = gray(np.transpose(np.array(graymap, dtype=np.uint8)))
            graymap_pygame = np.flip(graymap_pygame, 0)
            graymap_pygame = np.flip(graymap_pygame, 1)

            # graymap_pygame = graymap_pygame[::]
            surf = pygame.surfarray.make_surface(graymap_pygame)
            display_surface.blit(surf, (0, 0))

            pygame.draw.circle(display_surface, red, (R_loc_pixel_x, R_loc_pixel_y), 4)
            pygame.display.update()

        if i > No_itetations:
            R_loc_pixel_x = meter_to_pixel_distance(x / 1000)
            R_loc_pixel_y = meter_to_pixel_distance(y / 1000)
            graymap = np.array(
                [[mapbytes[x * MAP_SIZE_PIXELS + y] for y in range(MAP_SIZE_PIXELS)] for x in range(MAP_SIZE_PIXELS)],
                dtype=np.uint8)
            # graymap_pygame = gray(np.transpose(np.array(graymap, dtype=np.uint8)))
            # surf = pygame.surfarray.make_surface(graymap_pygame)
            # display_surface.blit(surf, (0, 0))
            graymap_image = Image.fromarray(graymap, 'L')
            graymap_image.save(MAP_name, format="png")
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
            break

    R_loc_pixel_x = meter_to_pixel_distance(x / 1000)
    R_loc_pixel_y = meter_to_pixel_distance(y / 1000)

    print('Scan complate')

    return R_loc_pixel_x, R_loc_pixel_y, theta


def navigation_to_point(GoalP, Rec_FLAG, display_FLAG, connection, sock):
    """

    :param GoalP:
    :param Rec_FLAG:
    :param display_FLAG:
    :param connection:
    :param sock:
    :return:
    """
    first_angle_FLAG = True
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    previous_distances = []
    previous_angles = []
    lidar = RPLidar(LIDAR_DEVICE)
    info = lidar.get_info()
    print(info)
    health = lidar.get_health()
    print(health)

    for i, scan in enumerate(lidar.iter_scans()):
        if i == 0:
            vx = 0
            vy = 0
            speed_percent = 0
            turn_percent = 0
            previous_x = pixel_to_meter_distance(MAP_SIZE_PIXELS / 2) * 1000
            previous_y = pixel_to_meter_distance(MAP_SIZE_PIXELS / 2) * 1000

            timetag = time.time()
        if (not i % 10) and i != 0 and display_FLAG:
            pass
            # R_loc_pixel_x = meter_to_pixel_distance(x/1000)
            # R_loc_pixel_y = meter_to_pixel_distance(y/1000)
            # graymap = np.array([[mapbytes[x * MAP_SIZE_PIXELS + y] for y in range(MAP_SIZE_PIXELS)] for x in range(MAP_SIZE_PIXELS)], dtype=np.uint8)
            # graymap_pygame = gray(np.transpose(np.array(graymap, dtype=np.uint8)))
            # surf = pygame.surfarray.make_surface(graymap_pygame)
            # display_surface.blit(surf, (0, 0))

            # pygame.draw.circle(display_surface, red, (R_loc_pixel_x, R_loc_pixel_y), 4)
            # pygame.draw.circle(display_surface, green, (GoalP[0], GoalP[1]), 4)
            # pygame.display.update()

        if i > 5:
            items = [item for item in scan]
            distances = [item[2] for item in items]
            angles = [item[1] for item in items]

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > 100:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles = angles.copy()
            # If not adequate, use previous
            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)
            # Get current robot position
            x, y, theta = slam.getpos()

            slam.getmap(mapbytes)

            # Get current robot parameters
            theta_rad = theta * np.pi / 180
            dt = time.time() - timetag
            vx = (x - previous_x) / dt
            vy = (y - previous_y) / dt
            v = np.sqrt(np.power(vx, 2) + np.power(vy, 2))
            previous_x = x
            previous_y = y
            timetag = time.time()

            R_loc_pixel_x = meter_to_pixel_distance(x / 1000)
            R_loc_pixel_y = meter_to_pixel_distance(y / 1000)

            distance_to_GOAL = pixel_to_meter_distance(dist_point_to_point([R_loc_pixel_x, R_loc_pixel_y], GoalP))
            # print('distance_to_GOAL = ' + str(distance_to_GOAL))

            if distance_to_GOAL > distance_to_GOAL_treshold:
                angle_to_GOAL = np.arctan2(GoalP[1] - R_loc_pixel_y, GoalP[0] - R_loc_pixel_x)
                # print('angle_to_GOAL = ' + str(angle_to_GOAL))
                DELTA_angle = np.abs(angle_to_GOAL * 180 / np.pi - theta)
                # print('DELTA_angle = ' + str(DELTA_angle))
                if DELTA_angle // 360:
                    DELTA_angle = DELTA_angle - (DELTA_angle // 360) * 360

                if first_angle_FLAG:
                    fangle = angle_to_GOAL * 180 / np.pi
                    first_angle_FLAG = False

                if i > 5:
                    if DELTA_angle < DELTA_angle_treshold:
                        pid_velocity.setpoint = 300  # mm/s
                        turn_percent = 0
                        speed_percent = pid_velocity(v)
                        pid_theta(theta_rad)
                        first_angle_FLAG = True
                    else:
                        if np.abs(DELTA_angle) > 90:
                            if fangle > 0:
                                turn_percent = np.abs(pid_theta(theta_rad))
                            else:
                                turn_percent = - np.abs(pid_theta(theta_rad))
                        else:
                            turn_percent = pid_theta(theta_rad)

                        pid_velocity.setpoint = 0  # mm/s
                        pid_theta.setpoint = angle_to_GOAL
                        pid_velocity.setpoint = 0
                        speed_percent = 0

                    left_speed = speed_percent + turn_percent
                    right_speed = speed_percent - turn_percent
                    print('left_speed = ' + str(left_speed))
                    print('right_speed = ' + str(right_speed))

                    drive(left_speed, right_speed, speed_min_value)

            else:
                motorAll.stop()
                lidar.stop()
                time.sleep(.002)
                lidar.stop_motor()

                if Rec_FLAG is True:
                    global point_num
                    # recording(connection,sock,point_num)
                    point_num += 1

                lidar.disconnect()
                break

            process_data(angles, distances, R_loc_pixel_x, R_loc_pixel_y)
            # pygame.draw.circle(display_surface, red, (R_loc_pixel_x, R_loc_pixel_y), 4)
            # pygame.draw.circle(display_surface, green, (GoalP[0], GoalP[1]), 4)
            pygame.display.update()

    return


def drive(Left_speed, right_speed, speed_min_value):
    """

    :param Left_speed:
    :param right_speed:
    :param speed_min_value:
    :return:
    """
    if Left_speed > speed_min_value:
        m1.forward(np.abs(Left_speed))
        m2.forward(np.abs(Left_speed))
    else:
        m1.reverse(np.abs(Left_speed - 2 * speed_min_value))
        m2.reverse(np.abs(Left_speed - 2 * speed_min_value))

    if right_speed > speed_min_value:
        m3.forward(np.abs(right_speed))
        m4.forward(np.abs(right_speed))
    else:
        m3.reverse(np.abs(right_speed - 2 * speed_min_value))
        m4.reverse(np.abs(right_speed - 2 * speed_min_value))


def dist_to_wall(p0, line_p1, line_p2):
    """

    :param p0:
    :param line_p1:
    :param line_p2:
    :return:
    """
    x_0 = p0[0]
    y_0 = p0[1]
    x_1 = line_p1[0]
    y_1 = line_p1[1]
    x_2 = line_p2[0]
    y_2 = line_p2[1]
    distance = pixel_to_meter_distance(np.abs((x_2 - x_1) * (y_1 - y_0) - (x_1 - x_0) * (y_2 - y_1))
                                       / np.sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2))
    return distance


def midP(P1, P2):
    """

    :param P1:
    :param P2:
    :return:
    """
    return np.array([(P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2])


def find_points(c1, c2, c3, c4):
    """

    :param c1: room corner 1 coordinates
    :param c2: room corner 2 coordinates
    :param c3: room corner 3 coordinates
    :param c4: room corner 4 coordinates

    :return:
    m_points: points where measurement done
    h_points: middle points for navigation help
    c_point: center point
    """
    mid_p1 = midP(c1, c2)
    mid_p2 = midP(c1, c3)
    mid_p3 = midP(c1, c4)
    mid_p4 = midP(c2, c3)
    mid_p5 = midP(c2, c4)
    mid_p6 = midP(c3, c4)

    mid_points = np.array([mid_p1, mid_p2, mid_p3, mid_p4, mid_p5, mid_p6])

    center_p = np.array([(c1[0] + c2[0] + c3[0] + c4[0]) / 4, (c1[1] + c2[1] + c3[1] + c4[1]) / 4])

    meas_p1 = midP(c1, center_p)
    meas_p2 = midP(c2, center_p)
    meas_p3 = midP(c3, center_p)
    meas_p4 = midP(c4, center_p)
    m_points = np.array([meas_p1, meas_p2, meas_p3, meas_p4])

    dist_to_center = np.sqrt((mid_points[..., 0] - center_p[0]) ** 2 + (mid_points[..., 1] - center_p[1]) ** 2)
    dist_to_center_inx = np.argpartition(dist_to_center, 2)

    mid_points = np.delete(mid_points, dist_to_center_inx[:2], 0)

    dist_1 = dist_point_to_point(c1, c2)
    dist_2 = dist_point_to_point(c1, c3)
    dist_3 = dist_point_to_point(c1, c4)
    dist_4 = dist_point_to_point(c2, c3)
    dist_5 = dist_point_to_point(c2, c4)
    dist_6 = dist_point_to_point(c3, c4)

    room_distances = np.array([dist_1, dist_2, dist_3, dist_4, dist_5, dist_6])
    s_wall_indexes = np.argpartition(room_distances, 2)

    s_walls = [int(s_wall_indexes[0]), int(s_wall_indexes[1])]

    if s_walls[0] == 0:
        help_p1 = midP(meas_p1, meas_p2)
    elif s_walls[0] == 1:
        help_p1 = midP(meas_p1, meas_p3)
    elif s_walls[0] == 2:
        help_p1 = midP(meas_p1, meas_p4)
    elif s_walls[0] == 3:
        help_p1 = midP(meas_p2, meas_p3)
    elif s_walls[0] == 4:
        help_p1 = midP(meas_p2, meas_p4)
    elif s_walls[0] == 5:
        help_p1 = midP(meas_p3, meas_p4)

    if s_walls[1] == 0:
        help_p2 = midP(meas_p1, meas_p2)
    elif s_walls[1] == 1:
        help_p2 = midP(meas_p1, meas_p3)
    elif s_walls[1] == 2:
        help_p2 = midP(meas_p1, meas_p4)
    elif s_walls[1] == 3:
        help_p2 = midP(meas_p2, meas_p3)
    elif s_walls[1] == 4:
        help_p2 = midP(meas_p2, meas_p4)
    elif s_walls[1] == 5:
        help_p2 = midP(meas_p3, meas_p4)

    m_points = m_points.astype(int)
    h_points = np.array([help_p1, help_p2]).astype(int)
    c_point = center_p.astype(int)

    return m_points, h_points, c_point


def room_parameters(map_name, step_num):
    """

    :param map_name:
    :param step_num:
    :return:
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    thickness = 1

    graymap_png = cv2.imread(map_name, 0)
    img_color = cv2.imread(map_name)

    ret_walls, walls_threshold = cv2.threshold(graymap_png, 100, 255, cv2.THRESH_BINARY)
    inverted = cv2.bitwise_not(walls_threshold)

    kernel = np.ones((2, 2), np.uint8)
    erosion = cv2.erode(inverted, kernel, 1)
    dilation = cv2.dilate(erosion, kernel, 1)

    lines = cv2.HoughLinesP(dilation, rho=1, theta=1 * np.pi / 180, threshold=35, minLineLength=30, maxLineGap=60)
    angle_sum = np.array([(180 / np.pi) * np.arctan2(lines[:, :, 3] - lines[:, :, 1], lines[:, :, 2] - lines[:, :, 0])])
    angle_sum = angle_sum.reshape(angle_sum.shape[1], angle_sum.shape[0], angle_sum.shape[2])
    data = np.append(lines, angle_sum, axis=2)

    for line in data:
        x1, y1, x2, y2, angle = line[0]
        cv2.line(img_color, (int(x1), int(y1)), (int(x2), int(y2)), blue, 1)
    cv2.imwrite('/home/pi/Python Projects/map/Htransform' + step_num + '.png', img_color)
    cv2.imwrite('/home/pi/Python Projects/map/wall_thr' + step_num + '.png', inverted)
    cv2.imwrite('/home/pi/Python Projects/map/morph' + step_num + '.png', dilation)
    corner_1, corner_2, corner_3, corner_4 = find_corners(data)
    m_points, h_points, center_p = find_points(corner_1, corner_2, corner_3, corner_4)

    dist_1 = pixel_to_meter_distance(np.sqrt((corner_2[0] - corner_1[0]) ** 2 + (corner_2[1] - corner_1[1]) ** 2))
    dist_2 = pixel_to_meter_distance(np.sqrt((corner_3[0] - corner_1[0]) ** 2 + (corner_3[1] - corner_1[1]) ** 2))
    dist_3 = pixel_to_meter_distance(np.sqrt((corner_4[0] - corner_1[0]) ** 2 + (corner_4[1] - corner_1[1]) ** 2))

    room_distances = np.array([dist_1, dist_2, dist_3])
    room_distances = np.delete(room_distances, np.argmax(room_distances), 0)
    area = room_distances[0] * room_distances[1]

    corner1_text = str('(' + str(corner_1[0]) + ', ' + str(corner_1[1]) + ')')
    corner2_text = str('(' + str(corner_2[0]) + ', ' + str(corner_2[1]) + ')')
    corner3_text = str('(' + str(corner_3[0]) + ', ' + str(corner_3[1]) + ')')
    corner4_text = str('(' + str(corner_4[0]) + ', ' + str(corner_4[1]) + ')')

    cv2.circle(img_color, (m_points[0][0], m_points[0][1]), 3, (56, 171, 255), thickness=-1)
    cv2.circle(img_color, (m_points[1][0], m_points[1][1]), 3, (56, 171, 255), thickness=-1)
    cv2.circle(img_color, (m_points[2][0], m_points[2][1]), 3, (56, 171, 255), thickness=-1)
    cv2.circle(img_color, (m_points[3][0], m_points[3][1]), 3, (56, 171, 255), thickness=-1)
    cv2.circle(img_color, (h_points[0][0], h_points[0][1]), 3, (3, 191, 255), thickness=-1)
    cv2.circle(img_color, (h_points[1][0], h_points[1][1]), 3, (3, 191, 255), thickness=-1)
    cv2.circle(img_color, (center_p[0], center_p[1]), 3, (12, 255, 244), thickness=-1)
    cv2.circle(img_color, (corner_1[0], corner_1[1]), 3, (0, 255, 0), thickness=-1)
    cv2.circle(img_color, (corner_2[0], corner_2[1]), 3, (0, 255, 0), thickness=-1)
    cv2.circle(img_color, (corner_3[0], corner_3[1]), 3, (0, 255, 0), thickness=-1)
    cv2.circle(img_color, (corner_4[0], corner_4[1]), 3, (0, 255, 0), thickness=-1)

    cv2.putText(img_color, corner1_text, (corner_1[0], corner_1[1]), font, font_scale, (0, 0, 170), thickness,
                cv2.LINE_AA)
    cv2.putText(img_color, corner2_text, (corner_2[0], corner_2[1]), font, font_scale, (0, 0, 170), thickness,
                cv2.LINE_AA)
    cv2.putText(img_color, corner3_text, (corner_3[0], corner_3[1]), font, font_scale, (0, 0, 170), thickness,
                cv2.LINE_AA)
    cv2.putText(img_color, corner4_text, (corner_4[0], corner_4[1]), font, font_scale, (0, 0, 170), thickness,
                cv2.LINE_AA)

    cv2.imwrite('/home/pi/Python Projects/map/CV_ALGO' + step_num + '.png', img_color)

    return area, np.array([m_points]), np.array([h_points]), center_p


def nextPfinder(MPoints, HPoints, CPoint, step):
    """

    :param MPoints:
    :param HPoints:
    :param CPoint:
    :param step:
    :return:
    """
    x_index = 0
    y_index = 1
    angle_index = 2
    dist_index = 3

    x_robot = int(MAP_SIZE_PIXELS / 2)
    y_robot = int(MAP_SIZE_PIXELS / 2)

    # Measure points
    angle_to_mp = np.array([(180 / np.pi) * np.arctan2(MPoints[:, :, 1] - y_robot, MPoints[:, :, 0] - x_robot)])
    angle_to_mp = angle_to_mp.reshape(angle_to_mp.shape[1], angle_to_mp.shape[2], angle_to_mp.shape[0])
    MPoints = np.append(MPoints, angle_to_mp, axis=2)

    distance_to_mp = np.array([np.sqrt((x_robot - MPoints[..., 0]) ** 2 + (y_robot - MPoints[..., 1]) ** 2)])
    distance_to_mp = distance_to_mp.reshape(distance_to_mp.shape[1], distance_to_mp.shape[2], distance_to_mp.shape[0])
    MPoints = np.append(MPoints, distance_to_mp, axis=2)

    # Help points
    angle_to_hp = np.array([(180 / np.pi) * np.arctan2(HPoints[:, :, 1] - y_robot, HPoints[:, :, 0] - x_robot)])
    angle_to_hp = angle_to_hp.reshape(angle_to_hp.shape[1], angle_to_hp.shape[2], angle_to_hp.shape[0])
    HPoints = np.append(HPoints, angle_to_hp, axis=2)

    distance_to_hp = np.array([np.sqrt((x_robot - HPoints[..., 0]) ** 2 + (y_robot - HPoints[..., 1]) ** 2)])
    distance_to_hp = distance_to_hp.reshape(distance_to_hp.shape[1], distance_to_hp.shape[2], distance_to_hp.shape[0])
    HPoints = np.append(HPoints, distance_to_hp, axis=2)

    if step == 1 or step == 6:
        mp_with_angle = MPoints[MPoints[..., angle_index] > 0]
        next_point = np.array([int(mp_with_angle[np.argmin(mp_with_angle[..., dist_index])][x_index]),
                               int(mp_with_angle[np.argmin(mp_with_angle[..., dist_index])][y_index])])
        return next_point

    elif step == 2 or step == 7:
        MPoints = np.array([np.delete(MPoints[0], np.argmin(MPoints[..., dist_index]), 0)])
        next_point = np.array([int(MPoints[0][np.argmin(MPoints[..., dist_index])][x_index]),
                               int(MPoints[0][np.argmin(MPoints[..., dist_index])][y_index])])
        return next_point

    elif step == 3:
        next_point = np.array([int(HPoints[0][np.argmin(HPoints[..., dist_index])][x_index]),
                               int(HPoints[0][np.argmin(HPoints[..., dist_index])][y_index])])
        return next_point

    elif step == 4:
        return CPoint

    elif step == 5:
        hp_with_angle = HPoints[HPoints[..., angle_index] < 90]
        hp_with_angle = hp_with_angle[hp_with_angle[..., angle_index] > -90]
        next_point = np.array([int(hp_with_angle[np.argmin(hp_with_angle[..., dist_index])][x_index]),
                               int(hp_with_angle[np.argmin(hp_with_angle[..., dist_index])][y_index])])
        return next_point


def measurement_process(connection, sock):
    """

    :param connection:
    :param sock:
    :return:
    """
    lidar_scan_iterations = 100
    display_flag = True
    num_of_steps = 8
    steps = range(1, num_of_steps)

    for step in steps:
        print('Step = ' + str(step))
        map_image_name = '/home/pi/Python Projects/map/MAP_Step_' + str(step) + '.png'

        scan(lidar_scan_iterations, map_image_name, display_flag)
        area, m_points, h_points, center_p = room_parameters(map_image_name, str(step))
        height_of_room = measure_height(Ultrasonic_height)

        if step == 1:
            area_measurements = area
            height_measurements = height_of_room
        else:
            area_measurements = np.append(area_measurements, area)
            height_measurements = np.append(height_measurements, area)

        if step == 1 or step == 2 or step == 4 or step == 6 or step == 7:
            rec_flag = True
        else:
            rec_flag = False

        img_color = cv2.imread(map_image_name)
        next_p = nextPfinder(m_points, h_points, center_p, step)

        for point in m_points[0]:
            cv2.circle(img_color, (point[0], point[1]), 3, blue, thickness=-1)
        for point in h_points[0]:
            cv2.circle(img_color, (point[0], point[1]), 3, blue, thickness=-1)
        cv2.circle(img_color, (center_p[0], center_p[1]), 3, magenta, thickness=-1)
        cv2.circle(img_color, (int(MAP_SIZE_PIXELS / 2), int(MAP_SIZE_PIXELS / 2)), 3, red, thickness=-1)
        cv2.circle(img_color, (next_p[0], next_p[1]), 3, green, thickness=-1)
        cv2.imwrite('/home/pi/Python Projects/map/NextP' + str(step) + '.png', img_color)

        navigation_to_point(next_p, rec_flag, display_flag, connection, sock)

    area_mean = np.mean(area_measurements)
    height_mean = np.mean(height_measurements)
    send_files(connection, sock)
    return area_mean, height_mean


def create_directory(Folder_name):
    """

    :param Folder_name:
    :return:
    """
    # benchmark_num = datetime.now().strftime("%d_%m_%y_%H%M%S")
    Folder_name = '/home/pi/Python Projects/map'
    if os.path.isdir(Folder_name) == False:
        try:
            os.mkdir(Folder_name)
        except OSError:
            print("Creation of the directory %s failed" % Folder_name)

    bench_path = './Room/' + room_name + '/' + benchmark_num
    try:
        os.mkdir(bench_path)
    except OSError:
        print("Creation of the directory %s failed" % bench_path)

    for point_num in range(5):
        point_path = './Room/' + room_name + '/' + benchmark_num + '/' + str(point_num + 1)
        try:
            os.mkdir(point_path)
        except OSError:
            print("Creation of the directory %s failed" % point_path)

    for point_num in range(5):
        map_path = './Room/' + room_name + '/' + benchmark_num + '/' + str(point_num + 1) + '/Maps'
        record_path = './Room/' + room_name + '/' + benchmark_num + '/' + str(point_num + 1) + '/Records'
        plot_path = './Room/' + room_name + '/' + benchmark_num + '/' + str(point_num + 1) + '/Plots'

        try:
            os.mkdir(record_path)
        except OSError:
            print("Creation of the directory %s failed" % record_path)
        try:
            os.mkdir(map_path)
        except OSError:
            print("Creation of the directory %s failed" % map_path)
        try:
            os.mkdir(plot_path)
        except OSError:
            print("Creation of the directory %s failed" % plot_path)
        return benchmark_num



