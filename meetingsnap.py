import tkinter
import os
import io
import sys
import time
import _thread
import platform
import queue
from imagehash import average_hash
from PIL import ImageGrab, Image, ImageTk
from ttkbootstrap import Style
from tkinter import Label, Entry, filedialog, messagebox, ttk, E, W, N, S
from time import sleep
from urllib.request import urlopen

root = tkinter.Tk()
# root.minsize(width=400, height=200)
root.resizable(False, False)
root.title("截图程序状态：zzz")
root.config(bg="lightgrey")
savePath = ""
q = queue.Queue(1)

style = Style(theme="simplex")

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
                                                    outline='blue',
                                                    width=6,
                                                    dash=(10,10))
        self.canvas.bind('<B1-Motion>', onLeftButtonMove)

        def capImage(event):
            try:
                q.get(block=False)
            except:
                pass
            lastPic = None
            lastHash = 0
            currentHash = 0
            root.title("搬砖ing～累出屎～ 💩 ")
            while 1:
                left, right = sorted([self.X.get(), event.x])
                top, bottom = sorted([self.Y.get(), event.y])
                pic = ImageGrab.grab(bbox=[left+1, top+1, right, bottom])
                self.nameSuffix = time.strftime("_%H_%M_%S", time.localtime()) + ".jpg"
                filename = os.path.join(os.sep, savePath, self.namePrefix + self.nameSuffix)

                if lastPic != None:
                    lastHash = average_hash(lastPic)
                    currentHash = average_hash(pic)

                if lastPic == None or abs(lastHash-currentHash)>8:
                    pic.save(filename)
                    lastPic = pic
                sleep(1)
                try:
                    if q.get(block=False) == "False":
                        break
                except:
                    pass
            root.title("摆烂ing～闲出屁～ 💨 ")
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

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def stopCapture():
    try:
        q.put("False", block=False)
        root.title("摆烂ing～闲出屁～ 💨 ")
    except:
        pass

meetingNameLabel = Label(root, text="会议名称:")
meetingNameLabel.grid(row=0, column=0, padx=5, pady=5, sticky=W+E)

meetingNameEntry = Entry(root)
meetingNameEntry.grid(row=0, column=1, columnspan=2,  padx=5, pady=5, sticky=W+E)

buttonChooseDir = ttk.Button(root, style='info.TButton', text="选择目录", command=getDirectory)
buttonChooseDir.grid(row=1, padx=5, pady=5, sticky=W+E)

buttonCapture = ttk.Button(root, style='info.TButton', text='开始截图', command=buttonCaptureClick)
buttonCapture.grid(row=2,padx=5, pady=5, sticky=W+E)
buttonStop = ttk.Button(root, style='primary.TButton', text='停    止', command=stopCapture)
buttonStop.grid(row=2, column=1, padx=5, pady=5, sticky = W+E)

try:
    qcode_bytes = urlopen("https://meetingsnap.oss-cn-beijing.aliyuncs.com/ads/qcode.jpg", timeout=2).read()
    qcode_data = io.BytesIO(qcode_bytes)
    qcode = Image.open(qcode_data)
except:
    qcode = Image.open(get_resource_path("./qcode.jpg"))
qcodeImg = ImageTk.PhotoImage(qcode.resize((149, 142)))
qcodeLabel = Label(root, image=qcodeImg)
qcodeLabel.grid(row=3, column=2, sticky=W+E)
qcode.close()

try:
    howtouse_bytes = urlopen("https://meetingsnap.oss-cn-beijing.aliyuncs.com/ads/howtouse.jpg", timeout=2).read()
    howtouse_data = io.BytesIO(howtouse_bytes)
    howtouse = Image.open(howtouse_data)
except:
    howtouse = Image.open(get_resource_path("./howtouse.jpg"))
howtouseImg = ImageTk.PhotoImage(howtouse.resize((280, 150)))
howtouseLabel = Label(root, image=howtouseImg)
howtouseLabel.grid(row=3, column=0, columnspan=2, sticky=W+E+N+S)
howtouse.close()

adurl = "https://meetingsnap.oss-cn-beijing.aliyuncs.com/ads/note.jpg"
try:
    image_bytes = urlopen(adurl, timeout=2).read()
    data_stream = io.BytesIO(image_bytes)
    ad = Image.open(data_stream)
except:
    ad = Image.open(get_resource_path("./note.jpg"))
adImg = ImageTk.PhotoImage(ad.resize((430, 120)))
adLabel = Label(root, image=adImg)
adLabel.grid(row=4, column=0, columnspan=3, sticky=W+E)
ad.close()

root.mainloop()
