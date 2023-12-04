import cv2
import mediapipe as mp
import math
import time
import numpy as np

# 초기 설정을 위한 전역 변수
initial_setup_complete = False
initial_setup_start_time = 0
squeeze_strength_history = []
threshold = 0
squeeze_strength = 0
start_time = time.time()  # 프로그램 시작 시간 저장

# 초기 설정 수행 함수
def perform_initial_setup():
    global initial_setup_complete, threshold, squeeze_strength_history

    if squeeze_strength is not None:
        squeeze_strength_history.append(squeeze_strength)

        current_time = time.time()
        if current_time - initial_setup_start_time > 10:
            initial_setup_complete = True
            squeeze_strength_array = np.array(squeeze_strength_history)
            mean_squeeze_strength = np.mean(squeeze_strength_array)
            std_squeeze_strength = np.std(squeeze_strength_array)
            threshold = mean_squeeze_strength + std_squeeze_strength - 10
            print("초기 설정 완료.")
            print("평균 스퀴즈 강도:", mean_squeeze_strength)
            print("표준 편차:", std_squeeze_strength)
            print("임계값 설정 완료:", threshold)

# 손가락 스퀴즈 강도 계산 함수
def calculate_finger_squeeze(frame):
    global initial_setup_start_time, squeeze_strength

    # 프레임을 그레이스케일로 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 손 감지
    results = hands.process(frame)

    if results.multi_hand_landmarks:
        # 손가락 랜드마크 추출
        hand_landmarks = results.multi_hand_landmarks[0]

        # 랜드마크를 이미지에 그림
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # 각 손가락에 대해 두 개의 동그라미를 그림
        finger_tips = [(int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])) for landmark in hand_landmarks.landmark]
        for tip in finger_tips:
            cv2.circle(frame, tip, 5, (0, 0, 255), -1)

        # 두 손가락 끝 사이의 거리 계산
        distance_between_fingers = math.dist(finger_tips[0], finger_tips[4])

        return distance_between_fingers

    return None

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 미디어 파이프의 Hand 모델 로드
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 손가락 스퀴즈 강도 계산
    squeeze_strength = calculate_finger_squeeze(frame)

    # 초기 설정이 완료되지 않았으면 설정 수행
    if not initial_setup_complete:
        current_time = time.time()
        if initial_setup_start_time == 0:
            initial_setup_start_time = current_time
        print("초기 설정 진행 중...")
        cv2.putText(frame, f"<Initial setup> Keep squeezing ..", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 초기 설정 수행
        perform_initial_setup()

    # 초기 설정이 완료되었으면 정상 기능 진행
    else:
        # 스퀴즈 강도에 따라 피드백 주기
        if squeeze_strength is not None:
            squeeze_strength = int(squeeze_strength)
            print("Squeeze Strength :", squeeze_strength)

            if squeeze_strength > threshold:  
                feedback = "sqeeze more!"
            else:
                feedback = "Great!"

            # 화면에 피드백 표시
            text_position = (50, 100)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 2
            text_size = cv2.getTextSize(feedback, font, font_scale, font_thickness)[0]

            # 텍스트 배경 추가
            text_background_position = (text_position[0], text_position[1] - text_size[1])
            text_background_size = (text_size[0], text_size[1] + 5)
            cv2.rectangle(frame, (text_background_position[0], text_background_position[1]),
                          (text_background_position[0] + text_background_size[0], text_background_position[1] + text_background_size[1]),
                          (255, 255, 255), cv2.FILLED)

            # 텍스트 표시
            cv2.putText(frame, feedback, (50, 100), font, font_scale, (0, 0, 255), font_thickness)

            # 스퀴즈 강도 및 피드백를 화면에 표시
            cv2.putText(frame, f"squeeze_strength : {squeeze_strength}", (50, 50), font, font_scale, (0, 0, 255), font_thickness)

    # 현재 시간을 가져와서 프레임에 표시
    elapsed_time = time.time() - start_time
    cv2.putText(frame, f"Run-Time : {round(elapsed_time, 2)} s", (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # 화면에 프레임 표시
    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
