import tkinter
import os
import time
from PIL import ImageGrab, Image, ImageTk
from tkinter import Label, Entry, filedialog, messagebox
from time import sleep
from pathlib import Path
import _thread
import platform
import imagehash
import queue

root = tkinter.Tk()
# root.geometry('800x160+400+300')
root.resizable(False, False)
root.title("截图程序状态：zzz")
savePath = ""
q = queue.Queue(1)

def buttonCaptureClick():
    savePath = ""
    for widget in root.winfo_children():
        if isinstance(widget, Label):
            savePath = savePath + widget['text']

    if savePath.strip() == "会议名称:":
        messagebox.showwarning("给我反省！！！","上面的信息给我写明白！！！")
        return

    root.state('icon')

    sleep(0.1)

    filename = 'temp.png'
    im = ImageGrab.grab()
    im.save(filename)
    im.close()

    w = MyCapture(filename)
    buttonCapture.wait_window(w.top)

def getDirectory():
    savePath = filedialog.askdirectory(title = "选择存储目录")
    if platform.system().lower() == "windows":
        savePath = savePath.replace("/", "\\")
        
    pathLabel = Label(root, text=savePath)
    pathLabel.grid(row=1, column=1, columnspan=4)

def stopCapture():
    try:
        q.put("False", block=False)
        root.title("截图程序状态：摆烂ing～闲出屁～ 💨 ")
    except:
        pass

meetingNameLabel = Label(root, text="会议名称:")
meetingNameLabel.grid(row=0)

meetingNameEntry = Entry(root)
meetingNameEntry.grid(row=0, column=1, columnspan=3)

buttonChooseDir = tkinter.Button(root, text="选择目录", command=getDirectory)
buttonChooseDir.grid(row=1, ipadx=30)

buttonCapture = tkinter.Button(root, text='开始截图', command=buttonCaptureClick)
buttonCapture.grid(row=2,ipadx=30)
buttonStop = tkinter.Button(root, text='停    止', command=stopCapture)
buttonStop.grid(row=2, column=1,ipadx=30)

qcode = Image.open("./qcode.jpg")
qcodeImg = ImageTk.PhotoImage(qcode.resize((120, 130)))
qcodeLabel = Label(root, image=qcodeImg)
qcodeLabel.grid(row=3, column=1, ipadx=10)

class MyCapture:
    def __init__(self, png) -> None:
        # 记录鼠标位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)
        self.namePrefix = ""

        # 获取屏幕大小
        self.screenWidth = root.winfo_screenwidth()
        self.screenHeight = root.winfo_screenheight()

        self.top = tkinter.Toplevel(root,
                                    width=self.screenWidth,
                                    height=self.screenHeight)

        for widget in root.winfo_children():
            if isinstance(widget, Label):
                savePath = widget['text']
                if savePath == "会议名称:":
                    savePath = ""
            if isinstance(widget, Entry):
                self.namePrefix = widget.get().strip()
                if self.namePrefix == "":
                    self.namePrefix = time.strftime("%Y-%m-%d", time.localtime())

        # 创建顶级组件容器
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top,
                                     bg = 'white',
                                     width=self.screenWidth,
                                     height=self.screenHeight)

        # 显示全屏截图
        self.image = tkinter.PhotoImage(file=png)
        self.canvas.create_image(self.screenWidth//2,
                                 self.screenHeight//2,
                                 image=self.image)

        # 鼠标左键按下获取截图起始位置
        def onLeftButtonDown(event):
            self.X.set(event.x)
            self.Y.set(event.y)
            self.sel = True

        self.canvas.bind('<Button-1>', onLeftButtonDown)

        def onLeftButtonMove(event):
            if not self.sel:
                return

            global lastDraw
            try:
                self.canvas.delete(lastDraw) 
            except Exception as e:
                pass

            lastDraw = self.canvas.create_rectangle(self.X.get(),
                                                    self.Y.get(),
                                                    event.x,
                                                    event.y,
                                                    outline='black')
        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        def capImage(event):
            lastPic = None
            lastHash = 0
            currentHash = 0
            root.title("截图程序状态：搬砖ing～累出屎～ 💩 ")
            while 1:
                left, right = sorted([self.X.get(), event.x])
                top, bottom = sorted([self.Y.get(), event.y])
                pic = ImageGrab.grab(bbox=[left+1, top+1, right, bottom])
                self.nameSuffix = time.strftime("_%H_%M_%S", time.localtime()) + ".jpg"
                filename = os.path.join(os.sep, savePath, self.namePrefix + self.nameSuffix)

                if lastPic != None:
                    lastHash = imagehash.average_hash(lastPic)
                    currentHash = imagehash.average_hash(pic)

                if lastPic == None or abs(lastHash-currentHash)>10:
                    pic.save(filename)
                    lastPic = pic
                sleep(1)
                try:
                    if q.get(block=False) == "False":
                        break
                except:
                    pass
            root.title("截图程序状态：摆烂ing～闲出屁～ 💨 ")
            _thread.exit()

        def onLeftButtonUp(event):
            self.sel = False
            try:
                self.canvas.delete(lastDraw)
            except Exception as e:
                pass
            sleep(0.1)

            # global lastPic
            _thread.start_new_thread(capImage, (event,))
            self.top.destroy()

        self.canvas.bind('<ButtonRelease-1>', onLeftButtonUp)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

root.mainloop()
