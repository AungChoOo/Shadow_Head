import math
import cv2
import mediapipe as mp
import pyfirmata

cap = cv2.VideoCapture(0)
cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

board = pyfirmata.Arduino('/dev/ttyACM0')
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

pin9 = board.get_pin('d:9:s')
pin10 = board.get_pin('d:10:s')
pin11 = board.get_pin('d:11:s')

pin9.write(90)
pin10.write(90)
pin11.write(30)

servo1Prev = 0
servo2Prev = 0
servo3Prev = 0

def cosine_law(intput_point,opposite_point,last_point, y_axis = False):
    BC = math.dist(opposite_point, last_point)
    AB = math.dist(intput_point, last_point)
    AC = math.dist(intput_point, opposite_point)
    angle = int(math.degrees(math.acos((((AB**2)+(AC**2))-(BC**2))/(2*AB*AC))))
    if y_axis:
        if last_point[1] > intput_point[1]:
            angle = abs(angle+90)
        elif last_point[1] < intput_point[1]:
            angle = abs(angle-90)
        else:
            angle = 90
    return angle

def remap(OldValue, OldMin, OldMax, NewMin, NewMax):
    NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    return NewValue

def limit(value, minm, maxm):
    return max(min(maxm, value), minm)

while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.flip(frame,1)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame.flags.writeable = False

    results = face_mesh.process(frame)

    frame.flags.writeable = True
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(image = frame,
            landmark_list = face_landmarks,
            connections = None,
            landmark_drawing_spec = drawing_spec,
            connection_drawing_spec = drawing_spec)

            middle_point_xyz = [(face_landmarks.landmark[234].x + face_landmarks.landmark[454].x)/2, 
                            (face_landmarks.landmark[234].y + face_landmarks.landmark[454].y)/2,
                            (face_landmarks.landmark[234].z + face_landmarks.landmark[454].z)/2]

            x = cosine_law((middle_point_xyz[2],middle_point_xyz[1]), (middle_point_xyz[2],0), (face_landmarks.landmark[5].z,face_landmarks.landmark[5].y))
            y = cosine_law((middle_point_xyz[0],middle_point_xyz[2]), (1,middle_point_xyz[2]), (face_landmarks.landmark[454].x,face_landmarks.landmark[454].z), y_axis = True)
            z = cosine_law((face_landmarks.landmark[175].x,face_landmarks.landmark[175].y), (0,face_landmarks.landmark[175].y), (face_landmarks.landmark[197].x,face_landmarks.landmark[197].y))
            
            x = limit(x, 55, 110)
            y = limit(y, 70, 110)
            z  = limit(z, 60, 120)
            analogdata1 = remap(z, 60, 120, -90, 90)
            analogdata2 = remap(x , 55, 110, -90, 90)
            analogdata3 = int(remap(y, 70, 110, 145, 10))

            servo1 = int(limit(analogdata1-analogdata2+90, 0, 170))
            servo2 = int(limit(analogdata1+analogdata2+90, 0, 170))

            servo1 = int((servo1 * 0.1) + (servo1Prev * 0.90))
            servo2 = int((servo2 * 0.1) + (servo2Prev * 0.90))
            servo3 = int((analogdata3 * 0.1) + (servo3Prev * 0.90))
            servo1Prev = servo1
            servo2Prev = servo2
            servo3Prev = servo3

            pin9.write(servo2)
            pin10.write(servo1)
            pin11.write(servo3)
    
    cv2.imshow("window", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()