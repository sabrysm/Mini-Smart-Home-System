import os
import face_recognition
import cv2
import numpy as np
from cvzone.FaceDetectionModule import FaceDetector
import customtkinter as tk  # Tkinter for creating the GUI
from tkinter import messagebox, END  # Tkinter modules for dialogs
from tkinter import *
from PIL import Image, ImageTk  # PIL for image processing in Tkinter
import time
import serial


class GUIApp:
    def __init__(self, root):
        # Set up the main window and components
        self.root = root
        self.cap = None  #the camera variable
        self.EN = True  #flag of the language
        self.door_open = False  #flag of the door
        self.inData = False  #flag represent if the user is known or not
        self.users = self.read_users_names()  #list store all users name in database
        self.face_encodings2 = self.read_the_users()  #list store all face encoding in the database
        self.face_encodings = []  #list store face encoding in the camera
        self.boolean = False  #flag represent if the frame should be the main frame or not
        self.cap_encoding = []  #another list store face encoding in the camera(when using capture function only)
        self.inputPassword = "" #store the password entered by the user
        ########################################################
        #main frame
        self.main_frame = tk.CTkFrame(root)
        tk.set_appearance_mode("Light")

        #to add the video capture in the main frame
        self.image_label = tk.CTkLabel(self.main_frame, text="")  # Label to display camera images
        self.image_label.pack(pady=20)

        #to add mind cloud photo
        mind = Image.open('mind.png')
        mind = mind.resize((300, 200))
        mind = ImageTk.PhotoImage(mind)
        label = tk.CTkLabel(self.main_frame, image=mind, text="")
        label.pack(pady=70, side="bottom")

        # Button to manually change the password
        self.btn_change_password = tk.CTkButton(self.main_frame, text="Change Password",
                                                command=lambda: self.show_frame(self.verify_frame),
                                                hover_color="blue")
        self.btn_change_password.place(x=80, y=425)

        # Button to manually open the door
        self.open_button = tk.CTkButton(self.main_frame, text="Open Door", command=self.open_door,
                                        hover_color="green")
        self.open_button.place(x=500, y=425)

        # Button to manually close the door
        self.close_button = tk.CTkButton(self.main_frame, text="Close Door", command=self.close_door,
                                         hover_color="red")
        self.close_button.place(x=500, y=500)

        # Button to manually delete the user
        self.delete_button = tk.CTkButton(self.main_frame, text="Delete User",
                                          command=lambda: self.show_frame(self.delete_user_frame),
                                          hover_color='#FF6961')
        self.delete_button.place(x=80, y=500)

        # Button to manually add the user
        self.add_button = tk.CTkButton(self.main_frame, text="Add", command=self.capture, hover_color="lightblue")
        self.add_button.place(x=300, y=360)

        # label to show if there is unkown person
        self.labelunkown = tk.CTkLabel(self.main_frame, text="",
                                       font=tk.CTkFont(family="Arial", size=20, weight="bold"))
        self.labelunkown.place(x=260, y=570)

        #Button to manually change the theme of the gui
        self.mode_button = tk.CTkSwitch(self.main_frame, text="Light", command=self.change_mode)
        self.mode_button.place(x=10, y=10)

        #Button to manually change the language
        self.language_button = tk.CTkSwitch(self.main_frame, text="En", command=self.change_language)
        self.language_button.place(x=10, y=30)

        # circle to show if the door is opened or closed
        bg_color = self.main_frame.cget("fg_color")[0]
        self.canvas = tk.CTkCanvas(self.main_frame, width=30, height=30, bg=bg_color, highlightthickness=0)
        self.canvas.create_oval(0, 0, 30, 30, fill="red")
        self.canvas.place(x=1100, y=30)

        ########################################################
        #verify frame
        self.verify_frame = tk.CTkFrame(root)

        self.labelv = tk.CTkLabel(self.verify_frame, text="Please enter the old password to verify",
                                  bg_color="lightgreen", text_color="black")
        self.labelv.place(x=270, y=200)

        self.entv = tk.CTkEntry(self.verify_frame, width=200, height=30,
                                placeholder_text="enter old password to verify")
        self.entv.place(x=280, y=250)

        self.verify_btn = tk.CTkButton(self.verify_frame, text="Verify", command=self.verify_password,
                                       hover_color="lightgreen")
        self.verify_btn.place(x=310, y=310)

        self.home_btn = tk.CTkButton(self.verify_frame, text="Home",
                                     command=lambda: self.show_frame(self.main_frame),
                                     hover_color="blue")
        self.home_btn.place(x=310, y=350)
        ########################################################
        #update password frame
        self.update_password_frame = tk.CTkFrame(root)

        self.labelu = tk.CTkLabel(self.update_password_frame, text="Please enter new password",
                                  bg_color="lightblue",
                                  text_color="black")
        self.labelu.place(x=270, y=200)

        self.entu = tk.CTkEntry(self.update_password_frame, width=200, height=30,
                                placeholder_text="enter new password")
        self.entu.place(x=280, y=250)

        self.change_btn = tk.CTkButton(self.update_password_frame, text="Change", command=self.update_password,
                                       hover_color="lightblue")
        self.change_btn.place(x=310, y=310)

        self.home1_btn = tk.CTkButton(self.update_password_frame, text="Home",
                                      command=lambda: self.show_frame(self.main_frame), hover_color="blue")
        self.home1_btn.place(x=310, y=350)
        ########################################################
        #delete user frame
        self.delete_user_frame = tk.CTkFrame(root)

        self.labeld = tk.CTkLabel(self.delete_user_frame, text="List of the users", bg_color="light green",
                                  text_color="black")
        self.labeld.pack(pady=20)

        self.users_list = Listbox(self.delete_user_frame, width=20, height=15, font=('Arial', 15, 'bold'))
        self.users_list.pack(pady=30)

        self.delete_btn = tk.CTkButton(self.delete_user_frame, text="Delete", command=self.delete_user,
                                       hover_color="red")
        self.delete_btn.pack(pady=10)

        self.home2_btn = tk.CTkButton(self.delete_user_frame, text="Home",
                                      command=lambda: self.show_frame(self.main_frame), hover_color="blue")
        self.home2_btn.pack(pady=10)
        ########################################################
        #add user frame
        self.add_user_frame = tk.CTkFrame(root)

        #to add the video capture in the add user frame
        self.image_labela = tk.CTkLabel(self.add_user_frame, text="")  # Label to display camera images
        self.image_labela.pack(pady=20)

        self.labela = tk.CTkLabel(self.add_user_frame, text="Please enter the name", bg_color="light green",
                                  text_color="blue")
        self.labela.place(x=50, y=400)

        self.enta = tk.CTkEntry(self.add_user_frame, width=200, height=30, placeholder_text="enter name")
        self.enta.place(x=50, y=450)

        self.add_btn = tk.CTkButton(self.add_user_frame, text="Add", command=self.add_user, hover_color="lightblue")
        self.add_btn.place(x=300, y=450)

        self.home3_btn = tk.CTkButton(self.add_user_frame, text="Home",
                                      command=lambda: self.show_frame(self.main_frame),
                                      hover_color="blue")
        self.home3_btn.place(x=50, y=500)
        ########################################################
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.show_frame(self.main_frame)

    #intialize the serial communicate object between the arduino and the python program
    SerialInst=serial.Serial('COM3',9600,timeout=2)
    time.sleep(2)

    #close the camera if I closed the gui
    def on_closing(self):
        # Release the video capture if it's active
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        self.root.quit()  # Exit the Tkinter mainloop
        self.root.destroy()  # Close the window

    #change the theme between dark and light theme
    def change_mode(self):
        if self.mode_button.get():
            bg_color = self.main_frame.cget("fg_color")[1]
            self.canvas.configure(bg=bg_color)
            tk.set_appearance_mode("Dark")
            if self.EN:
                self.mode_button.configure(text="Dark")  #write dark if it is dark theme and the language english
            else:
                self.mode_button.configure(text="مظلم")  #write مظلم if it is dark theme and the language arabic
        else:
            bg_color = self.main_frame.cget("fg_color")[0]
            self.canvas.configure(bg=bg_color)
            tk.set_appearance_mode("Light")
            if self.EN:
                self.mode_button.configure(text="Light")  #write light if it is light theme and the language english
            else:
                self.mode_button.configure(text="مضيئ")     #write مضيئ if it is light theme and the language arabic

    #change the language between arabic and english (edit most of the labels to the language it should be)
    def change_language(self):
        self.EN = not self.language_button.get()
        if self.language_button.get():
            self.btn_change_password.configure(text="المرور كلمة تغيير")
            self.open_button.configure(text="الباب فتح")
            self.close_button.configure(text="الباب غلق")
            self.delete_button.configure(text="المستخدم مسح")
            self.add_button.configure(text="اضافة")
            if self.mode_button.get():
                self.mode_button.configure(text="مظلم")
            else:
                self.mode_button.configure(text="مضيئ")
            self.language_button.configure(text="ع")
            self.labelv.configure(text="القديمة المرور كلمة ادخال بالرجاء")
            self.entv.configure(placeholder_text=" القديمة المرور كلمة ادخل")
            self.verify_btn.configure(text="التأكيد")
            self.home_btn.configure(text="المنزل")
            self.labelu.configure(text="الجديدة المرور كلمة ادخال بالرجاء")
            self.entu.configure(placeholder_text="الجديدة المرور كلمة ادخل")
            self.change_btn.configure(text="تغيير")
            self.home1_btn.configure(text="المنزل")
            self.labeld.configure(text="المستخدمين قائمة")
            self.delete_btn.configure(text="مسح")
            self.home2_btn.configure(text="المنزل")
            self.labela.configure(text="الاسم ادخال برجاء")
            self.enta.configure(placeholder_text="الاسم ادخل")
            self.add_btn.configure(text="اضف")
            self.home3_btn.configure(text="المنزل")
        else:
            self.btn_change_password.configure(text="Change Password")
            self.open_button.configure(text="Open Door")
            self.close_button.configure(text="Close Door")
            self.delete_button.configure(text="Delete User")
            self.add_button.configure(text="Add")
            if self.mode_button.get():
                self.mode_button.configure(text="Dark")
            else:
                self.mode_button.configure(text="Light")
            self.language_button.configure(text="En")
            self.labelv.configure(text="Please enter the old password to verify")
            self.entv.configure(placeholder_text="enter old password to verify")
            self.verify_btn.configure(text="Verify")
            self.home_btn.configure(text="Home")
            self.labelu.configure(text="Please enter new password")
            self.entu.configure(placeholder_text="enter new password")
            self.change_btn.configure(text="Change")
            self.home1_btn.configure(text="Home")
            self.labeld.configure(text="List of the users")
            self.delete_btn.configure(text="Delete")
            self.home2_btn.configure(text="Home")
            self.labela.configure(text="Please enter the name")
            self.enta.configure(placeholder_text="enter name")
            self.add_btn.configure(text="Add")
            self.home3_btn.configure(text="Home")

    #show the frame you want
    def show_frame(self, frame):
        #hide all the frames
        self.main_frame.pack_forget()
        self.update_password_frame.pack_forget()
        self.verify_frame.pack_forget()
        self.add_user_frame.pack_forget()
        self.delete_user_frame.pack_forget()

        if frame == self.delete_user_frame:
            self.users_list.selection_clear(0, END)
            self.users_list.delete(0, END)
            for user in self.users:
                if user == "":
                    continue
                self.users_list.insert(END, user)

        #show the selected frame
        frame.pack(fill="both", expand=True)

    #check the password to open the door if right
    def check_password(self,entered_password):
        with open("Password.txt", 'r') as f:
            password = f.read()
        if entered_password == password:
            self.open_door()
        else:
            self.close_door()
        f.close()

    #check if the user know the old password to update a new password
    def verify_password(self):

        #to get the entered password
        verify = self.entv.get()
        #to delete the password written if it is incorrect inorder to try to enter it again
        self.entv.delete(0, END)

        if self.EN:
            self.labelv.configure(text="Please enter the old password to verify", bg_color="lightgreen")
        else:
            self.labelv.configure(text="السابقة المرور كلمة ادخال برجاء", bg_color="lightgreen")

        #if there is no password set before set a password named admin for the homeowners to change to be usable
        if not os.path.exists("Password.txt"):
            with open('Password.txt', 'w') as fs:
                fs.write("admin")
                fs.close()

        #read the password to check it with the new password
        with open("Password.txt", 'r') as f:
            password = f.read()
        if verify == password:
            self.show_frame(self.update_password_frame)
        else:
            if self.EN:
                self.labelv.configure(text="Sorry, incorrect password!", bg_color="red")
            else:
                self.labelv.configure(text="خاطئة! مرور كلمة عذرا", bg_color="red")
        f.close()

    #the homeowners after verifying the old password they can put a new password
    def update_password(self):
        password = self.entu.get()
        self.entu.delete(0, END)  # Clear the entry field

        if len(password) != 4:
            messagebox.showerror("Error", "Password must be 4 digits!")
            return

        with open("Password.txt", 'w') as f:
            f.write(password)
            f.close()

        self.show_frame(self.main_frame)

    # Method to open the door
    def open_door(self):
        self.SerialInst.write('1'.encode()) # Send command to Arduino to open the door
        if self.EN and not self.door_open:
            self.door_open = True
            messagebox.showinfo("Door Control", "The door has been opened.")  # Show confirmation message
            self.canvas.create_oval(0, 0, 30, 30, fill="green")
        elif not self.EN and not self.door_open:
            self.door_open = True
            messagebox.showinfo("Door Control", "تم فتح الباب")
            self.canvas.create_oval(0, 0, 30, 30, fill="green")

    # Method to close the door
    def close_door(self):
        self.SerialInst.write('0'.encode())  # Send command to Arduino to close the door
        if self.EN and self.door_open:
            messagebox.showinfo("Door Control", "The door has been closed.")  # Show confirmation message
            self.canvas.create_oval(0, 0, 30, 30, fill="red")
            self.door_open = False
        elif not self.EN and self.door_open:
            self.door_open = False
            messagebox.showinfo("Door Control", "تم غلق الباب ")
            self.canvas.create_oval(0, 0, 30, 30, fill="red")

    #read the faces from the database
    def read_the_users(self):
        #if there is no file with this name open a one and close it
        if not os.path.exists('save.txt'):
            open('save.txt', 'w').close()
        # open the file to read it
        with open('save.txt', 'r') as file:
            #get content a string that's in the file
            content = file.read()
            #write the characters that you don't need in a list
            unNeadedChars = ['[', ']', '(', ')', ' ']
            #delete all this characters
            for char in unNeadedChars:
                content = content.replace(char, '')
            #split the string to lists every object was a numpy array before
            faces = content.split("array")
            last = []
            for face in faces:
                #split every object to a list
                char_face = face.split(',')
                final_face = []
                # return all numbers to float form
                for charr in char_face:
                    if charr != '\n' and charr != '':
                        float_number = float(charr)
                        final_face.append(float_number)
                #convert the list of numbers to a numpy array
                final_face_array = np.array(final_face)
                #make a list of the numpy arrays and return it
                last.append(final_face_array)
            return last

    #read all the users names
    def read_users_names(self):
        # if there is no file with this name open a one and close it
        if not os.path.exists('users.txt'):
            open('users.txt', 'w').close()
        # open the file to read it
        with open('users.txt', 'r') as file:
            #read all the file content and split it into list
            content = file.read()
            #delete all unwanted chars
            content = content.replace('[', '')
            content = content.replace(']', '')
            content = content.replace('\'', '')
            usersNames = content.split(',')
            return usersNames

    # compare the image with the database
    def compare_two_images(self, img):
        thisUser = "unknown"    #at first the user is unknown until prove the opposite
        #load the image
        image1 = img
        # Get the face encodings
        face_locations1 = face_recognition.face_locations(image1)
        face_encodings1 = face_recognition.face_encodings(image1, face_locations1)
        self.face_encodings = face_encodings1
        #load the database
        # Ensure we have at least one face in both of them
        if len(face_encodings1) == 0:
            return [False, thisUser]
        elif len(self.face_encodings2) == 0:
            return [False, thisUser]
        else:
            #compare the face with every face in the database
            idx = 1
            for face in self.face_encodings2:
                if len(face) == 0:
                    continue
                matches = face_recognition.compare_faces(face_encodings1, face)
                if any(matches):
                    return [True, self.users[idx]]
                idx = idx + 1
            return [False, thisUser]

    #add the user to the database
    def add_user(self):
        name = self.enta.get()
        self.enta.delete(0, END)

        if self.EN:
            self.labela.configure(text="Please enter the name", bg_color="light green", text_color="blue")
        else:
            self.labela.configure(text="الاسم ادخال برجاء", bg_color="light green", text_color="blue")

        #write username in the database and the variable will be a flag if this is a new name or not
        f = self.write_user_name(name)

        #if it is a new name add the face in the database and the boolean flag will represent that
        #the app should go to the main frame
        if f:
            self.write_new_users(self.cap_encoding)
            self.boolean = True
            self.detect_faces()
        #else you should take another name or return to home page without saving the user
        else:
            if self.EN:
                self.labela.configure(text="This name is already used", bg_color="red")
            else:
                self.labela.configure(text="حاليا مستخدم الاسم", bg_color="red")

    #capture a pic to the user to check if there is a face unknown or not
    def capture(self):
        cap = cv2.VideoCapture(0)
        s, img = cap.read()
        inData, _ = self.compare_two_images(img)
        #get the face encoding in another variable to prevent changing it in the detecting face function
        self.cap_encoding = self.face_encodings
        cap.release()
        if len(self.cap_encoding) and not inData:
            self.show_frame(self.add_user_frame)
        elif not len(self.cap_encoding):
            if self.EN:
                messagebox.showerror("Error", "There is no face detected!")
            else:
                messagebox.showerror("Error", "لم يتم تحديد اي وجه!")
        elif inData:
            if self.EN:
                messagebox.showerror("Error", "This face is already added before!")
            else:
                messagebox.showerror("Error", "هذا الوجه تم اضافته من قبل!")
        self.detect_faces()

    #detect if there is a face
    def detect_faces(self):
        #if boolean you should go to the main frame
        if self.boolean:
            self.show_frame(self.main_frame)
            self.boolean = False
        self.inData = False  #flag that there is a face in Database
        userName = "UnKnown"
        #open a video of your camera
        self.cap = cv2.VideoCapture(0)
        #detect the face in the video
        detector = FaceDetector()
        #booleon detect if there is a face in video or no
        bol = False
        startTime = time.time()
        timeInterval = 5
        #open the app loop
        while True:
            #check the time of the app
            currentTime = time.time()
            #take a two image one to detect if there is a face or no and the other to edit on it
            success, img = self.cap.read()
            s, image = self.cap.read()
            #flib the images to be easier to watch
            image = cv2.flip(image, 1)
            img = cv2.flip(img, 1)
            # Print the bounding boxes and their scores(score=the percentages that is a face)
            img, bBoxes = detector.findFaces(img)
            cv2.waitKey(1)
            for bbox in bBoxes:
                x, y, w, h = bbox['bbox']
                startPoint = (x, y)
                endPoint = (x + w, y + h)
                thickness = 2

                try:
                    # Face Detected
                    if self.inData:
                        self.labelunkown.configure(text="")
                        self.open_door()  # Open the door
                        cv2.putText(image, str(userName), (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2,
                                    cv2.LINE_AA)
                        image = cv2.rectangle(image, startPoint, endPoint, (0, 255, 0), thickness)
                    else:
                        if self.EN:
                            self.labelunkown.configure(text="Unkown person detected!", text_color="red")
                        else:
                            self.labelunkown.configure(text="!تم اكتشاف شخص مجهول", text_color="red")

                        if self.SerialInst.in_waiting > 0:
                            receivedText=self.SerialInst.readline().decode('utf-8').rstrip()
                            if receivedText == "Key pressed: #":
                                self.check_password(receivedText)
                            if isinstance(receivedText, str) and len(receivedText) == 4:
                                print(f"{receivedText=}")
                                self.inputPassword = receivedText
                                self.check_password(receivedText)
                            else:
                                print(receivedText)

                        cv2.putText(image, str(userName), (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2,
                                    cv2.LINE_AA)
                        image = cv2.rectangle(image, startPoint, endPoint, (0, 0, 255), thickness)
                except Exception as e:
                    print(e)
                score = bbox['score']

                #it is less than 70% there is a face
                if bol and score[0] < 0.7:
                    bol = False #get that the face get away of the camera
                    self.inData = False
                    userName = "unKnown"
                #check if there is a face detected in first time by 90% percentage or passed 5 sec
                if (score[0] > 0.9 and not bol) or (currentTime - startTime >= timeInterval):
                    #boolen of presence of a face is true now
                    bol = True
                    #compare the image with the database
                    self.inData, userName = self.compare_two_images(img)
                    startTime = time.time()

            # Display the image in the GUI
            try:
                img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)

                self.image_label.configure(image=img_tk)
                self.image_label.image = img_tk
                self.image_labela.configure(image=img_tk)
                self.image_labela.image = img_tk
                # Call the Tkinter update() method to refresh the GUI
                self.root.update()
            except Exception as e:
                print(e)

    #write the image in the database after encoding it
    def write_new_users(self, encoding):
        self.face_encodings2.append(encoding[0])
        with open('save.txt', 'a') as file:
            # Write the encoding like a string
            file.write(f"{encoding}")

    # write the users name in database
    def write_user_name(self, name):
        #booleon that this is new name
        newName = True
        usersNames = self.users
        print(f"{usersNames=}")
        #chect that the name not in the database
        for user in usersNames:
            #if the name not new request to enter new name
            if user == name:
                newName = False
        #if the name is new name write it in the file
        if newName:
            self.users.append(name)
            with open('users.txt', 'a') as file:
                file.write(f",{name}")
        return newName

    #delete the user from the database
    def delete_user(self):
        select = self.users_list.curselection()
        if not select:
            if self.EN:
                messagebox.showerror("Error", "No name selected!")
            else:
                messagebox.showerror("Error", "لم يتم تحديد اسم!")
            return

        #to get the name selected from the list
        name = self.users_list.get(select)
        #get the name index and delete it and its face
        idx = self.users.index(name)
        print(f"Name: {name}, Index: {idx}")
        if idx == -1:
            if self.EN:
                messagebox.showerror("Error", "Can't delete this user!")
            else:
                messagebox.showerror("Error", "لا يمكن حذف هذا المستخدم!")
            return
        print(f"{self.users=}\n{self.face_encodings2=}")
        self.face_encodings2.pop(idx)
        self.users.pop(idx)
        if len(self.users) != 1:
            with open('users.txt', 'w') as file:
                file.write(f"{self.users}")
                file.close()
        else:
            open('users.txt', 'w').close()
        if len(self.face_encodings2) != 1:
            with open('save.txt', 'w') as file:
                file.write(f"{self.face_encodings2[1:]}")
                file.close()
        else:
            open('save.txt', 'w').close()

        #remove the name selected from the list
        self.users_list.delete(0, END)
        for user in self.users:
            if user == "":
                continue
            self.users_list.insert(END, user)
        self.users_list.selection_clear(0, END)


# Initialize the GUI application
root = tk.CTk()
root.title("Smart Home - Face Recognition")
root.geometry("720x600")
app = GUIApp(root)  # Create an instance of the GUIApp class
app.detect_faces()
root.mainloop()  # Start the main loop to run the application
