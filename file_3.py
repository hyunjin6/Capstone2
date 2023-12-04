import cv2
import mediapipe as mp
import math

# 어깨, 왼쪽 팔꿈치, 왼쪽 손목, 오른쪽 팔꿈치, 오른쪽 손목의 인덱스
left_shoulder_index = 11
left_elbow_index = 13
left_wrist_index = 15
right_shoulder_index = 12
right_elbow_index = 14
right_wrist_index = 16

def calculate_arm_flexion(frame, bent_count, previous_flexion_state, current_arm):

    # 어깨, 왼쪽 팔, 왼쪽 손목, 오른쪽 팔, 오른쪽 손목 랜드마크 감지 (Pose 모델 사용)
    results = pose.process(frame)

    if results.pose_landmarks:
        # 랜드마크 좌표 추출
        landmarks = results.pose_landmarks.landmark

        # 왼쪽 팔, 오른쪽 팔 좌표 추출
        left_shoulder = landmarks[left_shoulder_index]
        left_elbow = landmarks[left_elbow_index]
        left_wrist = landmarks[left_wrist_index]
        right_shoulder = landmarks[right_shoulder_index]
        right_elbow = landmarks[right_elbow_index]
        right_wrist = landmarks[right_wrist_index]

        if current_arm == "left":
            shoulder = left_shoulder
            elbow = left_elbow
            wrist = left_wrist
        else:
            shoulder = right_shoulder
            elbow = right_elbow
            wrist = right_wrist

        # 디버깅을 위해 좌표값 출력
        shoulder_x, elbow_x, wrist_x = shoulder.x, elbow.x, wrist.x

        # 팔 굽힘 각도 계산 (라디안을 도로 변환)
        if shoulder_x == elbow_x:
            # 분모가 0이 되는 경우 방지
            flexion_angle = 0.0
        else:
            # 인수가 유효한 범위 [-1, 1] 내에 있는지 확인
            argument = max(-1.0, min((wrist_x - elbow_x) / (shoulder_x - elbow_x), 1.0))
            flexion_angle = math.degrees(math.acos(argument))

        # 팔 굽힘 각도에 따라 피드백 메시지 생성
        bend_threshold = 90.0
        if flexion_angle < bend_threshold:
            flexion_state = "bent"
            if previous_flexion_state != "bent":
                bent_count += 1
        else:
            flexion_state = "straight"
            if previous_flexion_state != "straight":
                bent_count += 1

        # 어깨, 팔, 손목을 화면에 그립니다.
        shoulder_coords = (int(shoulder.x * frame.shape[1]), int(shoulder.y * frame.shape[0]))
        elbow_coords = (int(elbow.x * frame.shape[1]), int(elbow.y * frame.shape[0]))
        wrist_coords = (int(wrist.x * frame.shape[1]), int(wrist.y * frame.shape[0]))

        
        cv2.line(frame, shoulder_coords, elbow_coords, (0, 0, 255), 3)
        cv2.line(frame, elbow_coords, wrist_coords, (0, 0, 255), 3)
        cv2.circle(frame, shoulder_coords, 5, (0, 255, 0), -1)
        cv2.circle(frame, elbow_coords, 5, (0, 255, 0), -1)
        cv2.circle(frame, wrist_coords, 5, (0, 255, 0), -1)

        return flexion_angle, flexion_state, bent_count

    return None, None, bent_count

# 웹캠으로부터 비디오 스트림을 가져오는 경우
cap = cv2.VideoCapture(0)

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

bent_count_left = 0  # 왼쪽 팔 굽힌 횟수 초기화
bent_count_right = 0  # 오른쪽 팔 굽힌 횟수 초기화
previous_flexion_state_left = "straight"  # 이전 프레임의 왼쪽 팔 굽힘 상태 초기화
previous_flexion_state_right = "straight"  # 이전 프레임의 오른쪽 팔 굽힘 상태 초기화
current_arm = "left"  # 시작은 왼쪽 팔에서

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 왼쪽 또는 오른쪽 팔 굽힘 각도 계산 및 피드백 메시지
    if current_arm == "left":
        flexion_angle, flexion_state, bent_count_left = calculate_arm_flexion(frame, bent_count_left, previous_flexion_state_left, current_arm)
    else:
        flexion_angle, flexion_state, bent_count_right = calculate_arm_flexion(frame, bent_count_right, previous_flexion_state_right, current_arm)

    if flexion_angle is not None:
            
        # 텍스트를 화면에 표시
        if current_arm == "left":

            # 왼쪽 팔의 피드백 메시지에 흰 배경 추가
            text = f"Left arm flexion state: {flexion_state}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

            # 흰 배경의 사각형 그리기
            cv2.rectangle(frame, (10, 60 - text_height), (15 + text_width, 60), (255, 255, 255), -1)

            # 텍스트 추가
            cv2.putText(frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            text = f"Left arm bending angle: {round(flexion_angle, 2)} degrees"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            text = f"Left bent count: {bent_count_left}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (10, 90 - text_height), (15 + text_width, 90), (255, 255, 255), -1)
            cv2.putText(frame, text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            previous_flexion_state_left = flexion_state

        else:
            # 오른쪽 팔의 피드백 메시지에 흰 배경 추가
            text = f"Right arm flexion state: {flexion_state}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (10, 60 - text_height), (15 + text_width, 60), (255, 255, 255), -1)
            cv2.putText(frame, text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            text = f"Right arm bending angle: {round(flexion_angle, 2)} degrees"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            text = f"Right bent count: {bent_count_right}"
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (10, 90 - text_height), (15 + text_width, 90), (255, 255, 255), -1)
            cv2.putText(frame, text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            previous_flexion_state_right = flexion_state


    # 화면에 프레임 표시
    cv2.imshow("Video", frame)

    # 현재 팔을 바꿈 (10번까지 왼쪽 팔, 10번 이상이면 오른쪽 팔로 전환)
    if current_arm == "left" and bent_count_left >= 10:
        current_arm = "right"
        bent_count_left = 0
    elif current_arm == "right" and bent_count_right >= 10:
        current_arm = "left"
        bent_count_right = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()