# 오픈CV로 카메라 -> 저장, 
# login함수 로그인 정보 db로 확인, 
# 성공했을때 리워드 update 요런느낌

import tkinter as tk
from tkinter import ttk
from ultralytics import YOLO
from tkinter import simpledialog, messagebox
import cv2
import matplotlib.pyplot as plt
import serial
import time

from sqlalchemy import create_engine
db_connection = create_engine('mysql://coffee:1234@175.106.96.251:3306/coffee')
print(db_connection)
arduino = serial.Serial('COM7', 9600, timeout=1)

login_name = "Login"
login_flag = False

model = YOLO('./best_1.pt')
lables = ['holder','liquid','straw']

login_id = ""

def infer(current_window):

    if login_id == "":
        messagebox.showerror("Connection", "Please Login")
    else:
        # 카메라 장치 열기
        cap = cv2.VideoCapture(0)  # 0은 기본 카메라
        desired_width = 640
        desired_height = 640
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)
        # 카메라 열렸는지 확인
        if not cap.isOpened():
            print("카메라를 열 수 없습니다.")
            exit()

        while True:
            # 카메라 프레임 읽기
            ret, frame = cap.read()

            if ret:
                break

        # 프레임이 제대로 읽혔는지 확인

        # 이미지 회전
        frame_rotated = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # OpenCV의 BGR 이미지를 RGB로 변환
        frame_rgb = cv2.cvtColor(frame_rotated, cv2.COLOR_BGR2RGB)

        # valid 폴더 안에 있는 모든 이미지들을 추론
        result = model.predict(source=frame_rgb, save=True, imgsz=640)
        
        trash=[]
        for i in result[0].boxes.cls:
            print(lables[int(i)])
            trash.append(lables[int(i)])

        current_window.destroy()  # 현재 윈도우를 닫는다
        if len(trash) >= 1:
            message = "홀더 또는 빨대 또는 액체를 제거하고 다시 진행해주세요."
        else:
            time.sleep(2)  # wait for the serial connection to initialize
            try:
                arduino.write(b'1')  # Send the byte '1' to Arduino
                print("Sent '1' to Arduino")
            except Exception as e:
                print("Failed to send data: " + str(e))
            finally:
                arduino.close()  # Close the serial connection

            message = "리워드가 쌓였습니다!"
            query = db_connection.execute("select * from user where user_id = '{}' ".format(login_id))
            result_db = query.fetchall()

            point = list(result_db)[0][4] + 100
            db_connection.execute("update user set point = {} where user_id = '{}' ".format(point, login_id))  

            # 데이터베이스에, 사용자의 정보를 이용해서 update set = + 100

        open_new_window(message)


def login():
    # 로그인 창 생성
    username = simpledialog.askstring("Login", "Username:")
    password = simpledialog.askstring("Login", "Password:", show='*')
 
    # select 문을 통해서 회원이 디비에 있는지 확인할거임.

    query = db_connection.execute("select * from user where user_id = '{}' and user_pwd like '{}'".format(username, password))
    result_db = query.fetchall()

    global login_id

    # 여기서는 예시로 사용자 이름이 admin이고, 비밀번호가 1234일 때 로그인 성공으로 처리
    if len(result_db) >= 1:

        login_id = username
        login_button.config(text=username+"님")  # 로그인 버튼을 사용자 이름으로 변경
        global login_name, login_flag
        login_name = username+"님"
        login_flag = True
    else:
        messagebox.showerror("Login failed", "Incorrect username or password")

def open_new_window(message):
    # 새 윈도우 생성
    new_window = tk.Tk()
    new_window.geometry("1200x600")
    new_window.resizable(False, False)
    new_window.title("수거하냥")
    new_window.configure(bg='white')

    # 새 캔버스 생성 및 설정
    canvas = tk.Canvas(new_window, width=900, height=500, background="white")
    canvas.create_text(450, 250, text=message, font=('bold', 22))
    canvas.pack(pady=20)

    if login_id == "":
        # 로그인 버튼 생성 및 위치 설정
        login_button = tk.Button(new_window, text="Login", command=lambda: login(new_window), bg='blue', fg='white', font=('bold', 12))
        login_button.place(x=1100, y=10)  # 우측 상단에 위치
    else:
        # 로그인 버튼 생성 및 위치 설정
        login_button = tk.Button(new_window, text=f"{login_name}", command=lambda: login(new_window), bg='blue', fg='white', font=('bold', 12))
        login_button.place(x=1100, y=10)  # 우측 상단에 위치

    return new_window

# 윈도우 생성
window = tk.Tk()
window.geometry("1200x600")  # Adjust the size as needed
window.resizable(False, False)
window.title("수거하냥")
window.configure(bg='white')

# 레이블 생성
label = tk.Label(window,bg='white')
label.pack(pady=20)  # Add some vertical padding

# Create an Entry widget (text input)
# 사각형 그리기# 캔버스 생성
canvas = tk.Canvas(window, width=900, height=400,background="white")
# 사각형 중앙에 텍스트 배치
canvas.create_text(450, 200, text="수거함 위에 '깨끗이 씻은컵'을 올려두고 start 버튼을 눌러주세요", font=('bold',22))
canvas.pack()

# Create a Button with a custom style
start_button = tk.Button(window, text="start", command=lambda: infer(window), bg='green', fg='white', height=20, width=30, font=( 'bold',22))
start_button.pack(pady=20)

# 로그인 버튼 생성 및 위치 설정
login_button = tk.Button(window, text=login_name, command=login, bg='blue', fg='white', font=('bold', 12))
login_button.place(x=1100, y=10)  # 우측 상단에 위치

# 윈도우 실행
window.mainloop()


