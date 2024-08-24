import streamlit as st
import cv2
import pickle
import numpy as np
import os
from sklearn.neighbors import KNeighborsClassifier
import csv
import time
from datetime import datetime
from win32com.client import Dispatch
import pyautogui

# Function to perform text-to-speech and display a popup
def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)
    pyautogui.alert(text, "Information")

# Register Face Function
def register_face():
    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces_data = []

    i = 0
    name = st.text_input("Enter your aadhar number:")
    framesTotal = 51
    captureAfterFrame = 2

    if st.button('Start Registration'):
        while True:
            ret, frame = video.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facedetect.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                crop_img = frame[y:y + h, x:x + w]
                resized_img = cv2.resize(crop_img, (50, 50))
                if len(faces_data) <= framesTotal and i % captureAfterFrame == 0:
                    faces_data.append(resized_img)
                i = i + 1
                cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)

            cv2.imshow('frame', frame)
            cv2.waitKey(1)

            if len(faces_data) >= framesTotal:
                break

        video.release()
        cv2.destroyAllWindows()

        faces_data = np.asarray(faces_data)
        faces_data = faces_data.reshape((framesTotal, -1))
        if 'names.pkl' not in os.listdir('data/'):
            names = [name] * framesTotal
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)
        else:
            with open('data/names.pkl', 'rb') as f:
                names = pickle.load(f)
            names = names + [name] * framesTotal
            with open('data/names.pkl', 'wb') as f:
                pickle.dump(names, f)

        if 'faces_data.pkl' not in os.listdir('data/'):
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(faces_data, f)
        else:
            with open('data/faces_data.pkl', 'rb') as f:
                faces = pickle.load(f)
            faces = np.append(faces, faces_data, axis=0)
            with open('data/faces_data.pkl', 'wb') as f:
                pickle.dump(faces, f)
        st.success("Face registered successfully!")

# Voting Function
def vote():
    video = cv2.VideoCapture(0)
    facedetect = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    with open('data/names.pkl', 'rb') as f:
        LABELS = pickle.load(f)

    with open('data/faces_data.pkl', 'rb') as f:
        FACES = pickle.load(f)

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    screen_width, screen_height = pyautogui.size()
    imgBackground = cv2.imread("background.jpg")
    imgBackground = cv2.resize(imgBackground, (screen_width, screen_height))

    COL_NAMES = ['NAME', 'VOTE', 'DATE', 'TIME']

    def check_if_exists(name):
        try:
            with open("Votes.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and row[0] == name:
                        return True
        except FileNotFoundError:
            st.error("File not found or unable to open the CSV file.")
        return False

    if st.button('Start Voting'):
        while True:
            ret, frame = video.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facedetect.detectMultiScale(gray, 1.3, 5)

            output = None
            for (x, y, w, h) in faces:
                crop_img = frame[y:y + h, x:x + w]
                resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
                output = knn.predict(resized_img)
                ts = time.time()
                date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
                timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
                exist = os.path.isfile("Votes.csv")
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y - 40), (x + w, y), (0, 0, 255), -1)
                cv2.putText(frame, str(output[0]), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                attendance = [output[0], timestamp]

            video_x = 250
            video_y = (screen_height - frame.shape[0]) // 2
            imgBackground[video_y:video_y + frame.shape[0], video_x:video_x + frame.shape[1]] = frame

            cv2.imshow('frame', imgBackground)
            k = cv2.waitKey(1)

            if output is not None:
                voter_exist = check_if_exists(output[0])
                if voter_exist:
                    speak("YOU HAVE ALREADY VOTED")
                    break

                if k == ord('1'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "BJP", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

                if k == ord('2'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "CONGRESS", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

                if k == ord('3'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "JDS", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

                if k == ord('4'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "AAP", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

                if k == ord('5'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "COMMUNIST", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

                if k == ord('6'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "PRAJAKIYA", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

                if k == ord('7'):
                    speak("YOUR VOTE HAS BEEN RECORDED")
                    time.sleep(5)
                    with open("Votes.csv", "a") as csvfile:
                        writer = csv.writer(csvfile)
                        if not exist:
                            writer.writerow(COL_NAMES)
                        attendance = [output[0], "NOTA", date, timestamp]
                        writer.writerow(attendance)
                    speak("THANK YOU FOR PARTICIPATING IN THE ELECTIONS")
                    break

        video.release()
        cv2.destroyAllWindows()

# Streamlit App
st.title("Face Registration and Voting System")

option = st.selectbox("Choose an option", ["Register Face", "Vote"])

if option == "Register Face":
    register_face()
elif option == "Vote":
    vote()
