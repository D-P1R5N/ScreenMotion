import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import mss
import numpy as np

class Main(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Create Area of Interest")
        self.state = True
        self.attributes("-fullscreen",self.state)
        self.bind("<Escape>", self.toggle_fullscreen)


        self.frame = tk.Frame(self)
        self.frame.pack(side='top', expand=True, fill="both")

        self.canv = tk.Canvas(self.frame)
        self.canv.pack(side='top',expand=True, fill='both')
        self.image = self.capture_screen()
        self.canv.bind('<Button-1>', self.on_click)
        self.canv.bind('<ButtonRelease-1>', self.on_release)

    def toggle_fullscreen(self, event=None):
        if self.state:
            self.state = False
            self.attributes("-fullscreen",self.state)

        else:
            self.state = True
            self.attributes("-fullscreen",self.state)

        return "break"

    def on_click(self, event=None):
        x = self.winfo_pointerx()
        y = self.winfo_pointery()

        abs_x = x - self.winfo_rootx()
        abs_y = y - self.winfo_rooty()
        self.boundary_start = (abs_x, abs_y)
        print(self.boundary_start)

    def on_release(self, event=None):
        x = self.winfo_pointerx()
        y = self.winfo_pointery()

        abs_x = x - self.winfo_rootx()
        abs_y = y - self.winfo_rooty()
        self.boundary_end = (abs_x, abs_y)

        bool = messagebox.askyesno(
            'Confirm View',
            'Boundary:\nOrigin: {}\nEnd: {}'.format(self.boundary_start,self.boundary_end)
        )
        if bool:
            self._root().destroy()
        else:
            pass
        print(self.boundary_end)

    def capture_screen(self, event=None):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        with mss.mss() as scr:
            monitor = {"top": 0, "left": 0, "width": w, "height": h}
            i = np.array(scr.grab(monitor))
        #remove alpha channel
            i = i[:,:,:3]
        #reverse the color arrangement
            i = i[:,:,::-1]
            img = ImageTk.PhotoImage(image=Image.fromarray(i))
        self._root().canv.create_image(0,0,anchor='nw', image=img)
        return img

    def return_view(self, event=None):
        return (*self.boundary_start, *self.boundary_end)

root = Main()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
root.mainloop()
bounds = root.return_view()
y_ran = [bounds[1],bounds[3]]
y_ran.sort()
x_ran = [bounds[0],bounds[2]]
x_ran.sort()

edges = lambda x : cv2.Canny(x,20,30)
backSub = cv2.createBackgroundSubtractorMOG2(history = 50,varThreshold = 32, detectShadows = False)
with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": y_ran[0], "left": x_ran[0], "width": x_ran[1]-x_ran[0], "height": y_ran[1]-y_ran[0]}


    while "Screen capturing":

        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        img = np.array(sct.grab(monitor))


        mask = backSub.apply(img)
        x = edges(img)

        y = edges(mask)
        res = np.concatenate((x,y),axis=0)


        # Display the picture
        cv2.imshow("Captured Screen Region", res)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))


        #print("fps: {}".format(1 / (time.time() - last_time)))


        #print(np.sum(mask//np.max(mask)))

        # Press "q" to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
