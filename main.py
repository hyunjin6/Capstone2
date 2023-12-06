#1 Tkinter 및 필요한 라이브러리 가져오기

import tkinter as tk
import os
from PIL import Image, ImageTk, ImageSequence

#2 파일 실행 함수 정의
def run_python_file(file_number):
    file_path = f"file_{file_number}.py"
    if os.path.exists(file_path):
        print(f"Running {file_path}...")
        os.system(f"python {file_path}")
        print(f"{file_path} execution complete.")
    else:
        print(f"Error: {file_path} not found.")


#3 마우스 클릭 이벤트 콜백 함수 정의
def on_mouse_click(event):
    x, y = event.x, event.y
    for i, (startX, startY, endX, endY) in enumerate(rectangles):
        if startX <= x <= endX and startY <= y <= endY:
            run_python_file(i + 1)
            break  # 동작 실행 후 반복문 탈출

def on_enter(event):
    x, y = event.x, event.y
    for i, (startX, startY, endX, endY) in enumerate(rectangles):
        if startX <= x <= endX and startY <= y <= endY:
            canvas.itemconfig(rectangle_texts[i], fill="yellow")

def on_leave(event):
    x, y = event.x, event.y
    for i in range(len(rectangles)):
        canvas.itemconfig(rectangle_texts[i], fill="blue")


#4 Tkinter 윈도우 및 캔버스 생성
root = tk.Tk()
root.title("Action Selection")

# Tkinter 캔버스 생성
canvas_width = 700  # 원하는 너비로 수정
canvas_height = 500  # 원하는 높이로 수정
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

#5 배경 및 텍스트 생성
# 전체 화면에 대한 배경 채우기
canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="lightblue")

# 사각형 및 텍스트 좌표 정의
rectangles = [(30, 50, 130, 90), (180, 50, 280, 90), (330, 50, 430, 90), (480, 50, 580, 90)]


descriptions = [
    "<Squeeze finger> Squeeze your fingers together and then release them. Repeat this motion for 10 seconds. Initial setup may vary based on individual capabilities.",
    "<Wrist rotation> Extend your fingers and rotate your wrist in both left and right.",
    "<Arm flexion> Bend your arms and open them. Repeat 10 times from left to right.",
    "<Face rotation> Rotate your face to the left and right, maintaining a comfortable range of motion."
]

canvas.create_text(canvas_width // 2, 30, text="Select Action", font=("Helvetica", 14), fill="black")

#6 정적 이미지 로딩 및 표시
# 정적 이미지 리스트
image_list = []

# 텍스트 및 사각형 그리기
rectangle_texts = []  # 새로운 리스트 추가

for i, (startX, startY, endX, endY) in enumerate(rectangles):
    # 하늘색으로 채우기
    rectangle = canvas.create_rectangle(startX + 30, startY, endX + 30, endY, fill="skyblue")

    # 흰색 텍스트 표시
    text_x = (startX + endX) // 2 + 30
    text_y = (startY + endY) // 2
    text = canvas.create_text(text_x, text_y, text=f"Start !", fill="blue", font=("Helvetica", 10))

    # 설명 텍스트 표시
    desc_x = (startX + endX) // 2 + 30
    desc_y = endY + 100  # 텍스트 아래 여백 확보
    canvas.create_text(desc_x, desc_y, text=descriptions[i], fill="black", font=("Helvetica", 10), width=120)

    rectangle_texts.append(text)
    canvas.tag_bind(rectangle, "<Enter>", on_enter)
    canvas.tag_bind(rectangle, "<Leave>", on_leave)

    # 정적 이미지 로딩 및 크기 조정
    images = []
    for frame in ImageSequence.Iterator(Image.open(f"jpg_{i + 1}.jpg")):
        frame = frame.resize((100, 100), Image.LANCZOS)
        images.append(frame)
    image_list.append(ImageTk.PhotoImage(images[0]))  # 첫 번째 프레임을 PhotoImage로 변환

    # 이미지 표시
    label = tk.Label(root, image=image_list[i])
    label.image = image_list[i]
    window = canvas.create_window(text_x - 50, text_y + 250, anchor="nw", window=label)  # 텍스트의 아래로 조절

#7 마우스 클릭 이벤트에 콜백 함수 연결 및 Tkinter 메시지 루프 시작
# 마우스 클릭 이벤트에 콜백 함수 연결
canvas.bind("<Button-1>", on_mouse_click)

exit_flag = False

# 창을 확대해도 이미지와 텍스트가 함께 움직이도록 스크롤 설정
canvas.configure(scrollregion=canvas.bbox("all"))

# Tkinter 메시지 루프 시작
root.mainloop()
