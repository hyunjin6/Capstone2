#wrist_rotation

import cv2
import mediapipe as mp
import math
import time

# 초기 손목-엄지 각도
prev_wrist_thumb_angle = None
mp_drawing = mp.solutions.drawing_utils

# 타이머 관련 전역 변수
start_time = None
total_rotation_time = 0  # 회전 총 시간을 저장할 변수

# 각도 변화에 대한 임계값
angle_change_threshold = 1.0

def start_timer():
    global start_time
    start_time = time.time()

def stop_timer():
    global start_time, total_rotation_time
    if start_time:
        total_rotation_time += time.time() - start_time
        start_time = None

def calculate_wrist_thumb_angle(frame):
    # (이전 프레임의) 이전 손목-엄지 각도를 전역 변수로 사용
    global prev_wrist_thumb_angle, total_rotation_time

    # 손 감지
    results = hands.process(frame)

    if results.multi_hand_landmarks:
        # 손목 랜드마크 추출 
        hand_landmarks = results.multi_hand_landmarks[0]

        # 손목 중심과 엄지 손끝의 랜드마크 위치 추출
        wrist_center = hand_landmarks.landmark[0]
        thumb_tip = hand_landmarks.landmark[4]

        # 손목에서 엄지 손끝까지의 벡터 계산
        wrist_thumb_vector = (thumb_tip.x - wrist_center.x, thumb_tip.y - wrist_center.y)

        # x, y 좌표를 사용하여 손목-엄지 각도 계산 (라디안) -> 각도로 변환
        wrist_thumb_angle_rad = math.atan2(wrist_thumb_vector[1], wrist_thumb_vector[0])
        wrist_thumb_angle_deg = math.degrees(wrist_thumb_angle_rad)

        # 현재 손목-엄지 각도 출력
        print("현재 손목-엄지 각도:", wrist_thumb_angle_deg)

         # 이전 프레임의 손목-엄지 각도가 있을 경우 변화 계산
        if prev_wrist_thumb_angle is not None:
            # 각도 변화를 통해 회전 여부 확인
            angle_change = wrist_thumb_angle_deg - prev_wrist_thumb_angle

            # 글씨 색 설정
            text_color = (0, 0, 255)  # 빨간색

            if abs(angle_change) > angle_change_threshold:
                if angle_change > 0: 
                    print("손목이 시계방향으로 회전 중")
                    feedback = "Rotating left .."
                    start_timer()
                elif angle_change < 0:  
                    print("손목이 반시계방향으로 회전 중")
                    feedback = "Rotating right .."
                    start_timer()
            else:
                feedback = ""
                stop_timer()

            # 텍스트 크기 및 폰트 설정
            font_scale = 0.5
            font_thickness = 2
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_position = (50, 100)

            # 텍스트 크기 계산
            (text_width, text_height), baseline = cv2.getTextSize(feedback, font, font_scale, font_thickness)
            
            # 텍스트 배경 추가
            text_background_position = (text_position[0], text_position[1] - text_height)
            text_background_size = (text_width, text_height + 5)
            cv2.rectangle(frame, (text_background_position[0], text_background_position[1]),
                          (text_background_position[0] + text_background_size[0], text_background_position[1] + text_background_size[1]),
                          (255, 255, 255), cv2.FILLED)

            # 텍스트 표시
            cv2.putText(frame, feedback, text_position, font, font_scale, text_color, font_thickness)


        # 이전 손목-엄지 각도 갱신
        prev_wrist_thumb_angle = wrist_thumb_angle_deg

        # 랜드마크를 이미지에 그림
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 각 손가락에 대해 두 개의 동그라미를 그림
        for landmark in hand_landmarks.landmark:
            x = int(landmark.x * frame.shape[1])  # 너비
            y = int(landmark.y * frame.shape[0])  # 높이
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

    else:
        # 손이 감지되지 않은 경우 이전 손목-엄지 각도 초기화
        prev_wrist_thumb_angle = None

    # 타이머가 실행 중이면 화면에 표시
    if start_time is not None:
        elapsed_time = total_rotation_time + (time.time() - start_time)
        cv2.putText(frame, f"Total Rotation Time: {round(elapsed_time, 2)} s", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


# 미디어 파이프의 Hand 모델 로드
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# 웹캠으로부터 비디오 스트림을 가져오는 경우
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 손목-엄지 각도 계산
    calculate_wrist_thumb_angle(frame)

    # 화면에 프레임 표시
    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()