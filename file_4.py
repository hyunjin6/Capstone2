#face_rotation

import cv2
import mediapipe as mp
import math
import pygame

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh


# 알림 소리 파일 경로
sound_file_path = "alarm.mp3"

# Pygame 초기화
pygame.mixer.init()

# 알림 소리 재생
def play_notification_sound():
    pygame.mixer.music.load(sound_file_path)
    pygame.mixer.music.play()
    
# 얼굴 회전 각도를 계산하는 함수
def calculate_face_rotation(frame):
    # 얼굴 감지
    results = face_model.process(frame)

    if results.detections:
        for detection in results.detections:
            score = detection.score[0]
            if score > 0.5:
                # 얼굴 중심 눈 위치 계산
                bboxC = detection.location_data.relative_bounding_box
                mid_eye_x = bboxC.xmin + bboxC.width / 2
                mid_eye_y = bboxC.ymin + bboxC.height / 2

                # 코의 위치
                nose_landmark = mp_face_detection.get_key_point(detection, mp_face_detection.FaceKeyPoint.NOSE_TIP)

                # 중심 눈과 코 사이의 각도 계산 (라디안)
                angle = math.atan2(mid_eye_y - nose_landmark.y, mid_eye_x - nose_landmark.x)

                # 라디안을 각도로 변환
                angle_deg = math.degrees(angle)

                # 얼굴이 왼쪽으로 향하는지 오른쪽으로 향하는지 확인
                if -90 < angle_deg < 90:
                    face_direction_text = "Face is oriented to the right"
                    if-10 < angle_deg < 10:
                        play_notification_sound()
                else:
                    face_direction_text = "Face is oriented to the left"
                    if angle_deg > 170 or angle_deg < -170:
                        play_notification_sound()

                # 원하는 랜드마크의 인덱스 정의
                desired_landmarks = [10, 234, 454, 5]

                landmarks = face_mesh.process(frame).multi_face_landmarks
                if landmarks:
                    for face_landmarks in landmarks:
                        # 원하는 랜드마크만 표시
                        for index in desired_landmarks:
                            landmark_point = face_landmarks.landmark[index]
                            landmark_px, landmark_py = int(landmark_point.x * frame.shape[1]), int(
                                landmark_point.y * frame.shape[0])
                            cv2.circle(frame, (landmark_px, landmark_py), 2, (0, 255, 0), -1)

                return angle_deg, face_direction_text

    return None, None

face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
face_model = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# 웹캠으로부터 비디오 스트림을 가져오는 경우
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 얼굴 회전 경향 계산
    rotation_angle, face_direction_text = calculate_face_rotation(frame)

    if rotation_angle is not None:
        print("얼굴 회전 각도:", rotation_angle)
        print(face_direction_text)

        # 각도 및 방향 정보 표시
        text = f"Face Rotation Angle: {round(rotation_angle, 2)} degrees"
        (text_width, text_height), _ = cv2.getTextSize(face_direction_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(frame, (10, 60 - text_height), (15 + text_width, 60), (255, 255, 255), -1)
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, face_direction_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        
    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()