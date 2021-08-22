import tkinter as tk
from tkinter import ttk
from PIL import ImageTk,Image
from scipy.io import loadmat
from tkSliderWidget import Slider
import numpy as np
from scrollable_frame import DoubleScrolledFrame
from tkinter import messagebox, filedialog
import os
currentFrame = 0

class SampleApp(tk.Tk):

    globalContainer = 0

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        SampleApp.globalContainer = container
        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):
    data = np.zeros((120,3,3))
    coordinates = np.zeros((120,25,3))
    segments = []
    directory = ""
    files = []
    currentFile = ""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.root = tk.LabelFrame(self)
        self.root.grid(row = 0, column = 0, padx = 20, pady = 20)
        self.directoryBox = tk.LabelFrame(self.root)
        self.directoryBox.grid(row = 0, column = 0, padx = 20, pady = 20)
        self.directoryLocation = tk.Entry(self.directoryBox,text = StartPage.directory,width = 65)
        self.directoryLocation.grid(row = 0, column = 0, padx = 20, pady = 20)
        self.selectDirectoryButton = tk.Button(self.directoryBox, text = "Select directory", command = self.selectDirectory )
        self.selectDirectoryButton.grid(row = 0, column = 1, padx = 20, pady = 20)
        self.nextButton = tk.Button(self, text="Next",
                    command=lambda: controller.show_frame("PageOne"))
        self.nextButton.grid(row = 1, column = 0, padx = 20, pady = 20)

    def selectDirectory(self):
        StartPage.directory = filedialog.askdirectory(initialdir = "./", title = "Select a directory")
        self.directoryLocation.delete( 0,"end")
        self.directoryLocation.insert(0,str(StartPage.directory))
        StartPage.files = os.listdir(StartPage.directory)
        self.loadingVideo()
    def loadingVideo(self):
        for videoFile in StartPage.files:
            
            filePath = os.path.join(StartPage.directory,videoFile)
            labelPath = os.path.join(filePath,"label.txt")
            coordinatePath = os.path.join(filePath,"coordinates.mat")
            dataPath = os.path.join(filePath,'DepthFrames.mat')
            if not os.path.isfile(labelPath):  
                StartPage.currentFile = filePath
                coordinates = loadmat(coordinatePath)['coordinates'].squeeze(axis = 0)
                data = loadmat(dataPath)['DepthFrames'].squeeze(axis=0)
                StartPage.data = data 
                StartPage.coordinates = coordinates
                StartPage.segments = self.calculatingSegments()
                
                break
        
        return data, coordinates
    def returnData(self):
        return StartPage.data
    def calculatingSegments(self):
        rightHand = False
        leftHand = False
        coordinates = StartPage.coordinates
        for i in range(10,coordinates.shape[0]):

            if (coordinates[i][1,7]> 0.3 and coordinates[i-1][1,7] < 0.3 and coordinates[i-2][1,7] < 0.3 and coordinates[i-3][1,7] < 0.3 and 
            coordinates[i+1][1,7]> 0.3 and coordinates[i + 2][1,7]> 0.3 and coordinates[i + 3][1,7]> 0.3):
                rightHand = True
            if (coordinates[i][1,11]> 0.3 and coordinates[i-1][1,11] < 0.3 and coordinates[i-2][1,11] < 0.3 and coordinates[i-3][1,11] < 0.3 and 
            coordinates[i+1][1,11]> 0.3 and coordinates[i + 2][1,11]> 0.3 and coordinates[i + 3][1,11]> 0.3):
                leftHand = True
            if rightHand or leftHand:
                StartPage.segments.append(i)

            rightHand = False
            leftHand = False

        return StartPage.segments



class PageOne(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        global currentFrame
        self.parent = parent
        self.page1 = tk.LabelFrame(self)
        self.page1.grid(row = 0, column =0)
        self.controller = controller
        
        self.button9 = tk.Button(self.page1, text= "Refresh",command = self.refresh)
        self.button9.grid(row = 7, padx = 20, pady = 20)
        self.videoSpeed = 33

    def refresh(self):
        if self.page1:
            self.page1.destroy()
        self.page1 = tk.LabelFrame(self)
        self.page1.grid(row = 0, column =0) 
        self.root = tk.LabelFrame(self.page1,text = "Video")
        self.root.grid(row = 1, column = 1,padx = 20,pady = 20)
        self.frameNumber = tk.Label(self.root,text = str(currentFrame))
        self.frameNumber.grid(row = 0, column = 0)
        self.data = StartPage.data
        self.image = ImageTk.PhotoImage(image = Image.fromarray(self.data[0]))
        self.videoScreen = tk.Label(self.root,image = self.image,borderwidth = 10)
        self.videoScreen.grid(row = 1, column = 0,padx = 20, pady = 20,columnspan = 5)
        self.prevButton = tk.Button(self.root, text= "Previous",command = lambda: self.goBackward(currentFrame))
        self.prevButton.grid(row = 2, column = 0, padx = 5, pady = 20)
        self.nextButton = tk.Button(self.root, text= "Next",command = lambda: self.goForward(currentFrame))
        self.nextButton.grid(row = 2, column = 1, padx = 5, pady = 20)
        self.sliderFrame = tk.LabelFrame(self.page1, text = "Segmentations slider")
        self.sliderFrame.grid(row = 0, column = 1)
        self.scrollingFrame = DoubleScrolledFrame(self.sliderFrame, width = 600, height = 50)
        self.scrollingFrame.grid(row = 0 , column = 0 )
        self.boundaryBox = tk.Entry(self.sliderFrame,width = 20)
        self.boundaryBox.grid(row = 0 , column = 1, padx = 20, pady = 20)
        self.boundaryBoxButton = tk.Button(self.sliderFrame,text = "Add Boundary",command = lambda: self.addBoundary(self.boundaryBox.get()))
        self.boundaryBoxButton.grid(row = 0, column = 2)
        self.boundaryBoxDelete = tk.Entry(self.sliderFrame,width = 20)
        self.boundaryBoxDelete.grid(row = 1 , column = 1, padx = 20, pady = 20)
        self.boundaryBoxButtonDelete = tk.Button(self.sliderFrame,text = "Delete Boundary",command = lambda: self.DeleteBoundary(self.boundaryBoxDelete.get()))
        self.boundaryBoxButtonDelete.grid(row = 1, column = 2)
        self.slider = Slider(self.scrollingFrame, width = self.data.shape[0], height = 40, min_val = 0, max_val = self.data.shape[0], init_lis = StartPage.segments, show_value = True)
        self.slider.grid(row = 0, column = 0)       
        self.labels = np.zeros((self.data.shape[0]))
        self.labellingButtonsFrame = tk.LabelFrame(self.page1, text = "Labelling buttons")
        self.labellingButtonsFrame.grid(row = 0, column = 2,rowspan = 2)
        self.button1 = tk.Button(self.labellingButtonsFrame, text= "Collecting water",command = lambda: self.labelling(1,currentFrame))
        self.button1.grid(row = 0, padx = 20, pady = 20)
        self.button2 = tk.Button(self.labellingButtonsFrame, text= "Hand washing",command = lambda: self.labelling(2,currentFrame))
        self.button2.grid(row = 1, padx = 20, pady = 20)
        self.button3 = tk.Button(self.labellingButtonsFrame, text= "Mouth washing",command = lambda: self.labelling(3,currentFrame))
        self.button3.grid(row = 2, padx = 20, pady = 20)
        self.button4 = tk.Button(self.labellingButtonsFrame, text= "Face washing",command = lambda: self.labelling(4,currentFrame))
        self.button4.grid(row = 3, padx = 20, pady = 20)
        self.button5 = tk.Button(self.labellingButtonsFrame, text= "Arm washing",command = lambda: self.labelling(5,currentFrame))
        self.button5.grid(row = 4, padx = 20, pady = 20)
        self.button6 = tk.Button(self.labellingButtonsFrame, text= "Head washing",command = lambda: self.labelling(6,currentFrame))
        self.button6.grid(row = 5, padx = 20, pady = 20)
        self.button7 = tk.Button(self.labellingButtonsFrame, text= "Feet washing",command = lambda: self.labelling(7,currentFrame))
        self.button7.grid(row = 6, padx = 20, pady = 20)
        self.button8 = tk.Button(self.labellingButtonsFrame, text= "SAVE",command = self.saveLabel)
        self.button8.grid(row = 7, padx = 20, pady = 20)
        self.button9 = tk.Button(self.labellingButtonsFrame, text= "Refresh",command = self.refresh)
        self.button9.grid(row = 8, padx = 20, pady = 20)
        self.button10 = tk.Button(self.labellingButtonsFrame, text= "Next Video",command = self.nextVideo)
        self.button10.grid(row = 9, padx = 20, pady = 20)   
        self.labellingBox = tk.LabelFrame(self.page1,text = "LABELS")
        self.labellingBox.grid(row = 1,column = 0,rowspan = 10)     
        self.speedControlFrame = tk.LabelFrame(self.page1,text = "Control the speed of the video")
        self.speedControlFrame.grid(row = 2,column = 1,padx = 10,pady = 10)
        self.speed1Button = tk.Button(self.speedControlFrame,text = "0.5X", command = lambda: self.speedControl(0.5))
        self.speed1Button.grid(row = 0, column = 0, padx = 5, pady= 10)
        self.speed2Button = tk.Button(self.speedControlFrame,text = "0.75X", command = lambda: self.speedControl(0.75))
        self.speed2Button.grid(row = 0, column = 1, padx = 5, pady= 10)
        self.speed3Button = tk.Button(self.speedControlFrame,text = "1X", command = lambda: self.speedControl(1))
        self.speed3Button.grid(row = 0, column = 2, padx = 5, pady= 10)
        self.speed4Button = tk.Button(self.speedControlFrame,text = "1.5X", command = lambda: self.speedControl(1.5))
        self.speed4Button.grid(row = 0, column = 3, padx = 5, pady= 10)
        self.speed5Button = tk.Button(self.speedControlFrame,text = "2X", command = lambda: self.speedControl(2))
        self.speed5Button.grid(row = 0, column = 4, padx = 5, pady= 10)
        self.labelBox()
    def nextVideo(self):
         for videoFile in StartPage.files:
            
            filePath = os.path.join(StartPage.directory,videoFile)
            labelPath = os.path.join(filePath,"label.txt")
            coordinatePath = os.path.join(filePath,"coordinates.mat")
            dataPath = os.path.join(filePath,'DepthFrames.mat')
            if not os.path.isfile(labelPath): 
                StartPage.data = np.zeros((120,3,3))
                StartPage.coordinates = np.zeros((120,25,3))
                StartPage.segments = []
                StartPage.currentFile = filePath
                coordinates = loadmat(coordinatePath)['coordinates'].squeeze(axis = 0)
                data = loadmat(dataPath)['DepthFrames'].squeeze(axis=0)
                StartPage.data = data 
                StartPage.coordinates = coordinates
                StartPage.segments = self.calculatingSegments()
                print(StartPage.segments,"new segments")
                self.refresh()
                break
    
    def calculatingSegments(self):
        rightHand = False
        leftHand = False
        coordinates = StartPage.coordinates
        for i in range(10,coordinates.shape[0]):

            if (coordinates[i][1,7]> 0.3 and coordinates[i-1][1,7] < 0.3 and coordinates[i-2][1,7] < 0.3 and coordinates[i-3][1,7] < 0.3 and 
            coordinates[i+1][1,7]> 0.3 and coordinates[i + 2][1,7]> 0.3 and coordinates[i + 3][1,7]> 0.3):
                rightHand = True
            if (coordinates[i][1,11]> 0.3 and coordinates[i-1][1,11] < 0.3 and coordinates[i-2][1,11] < 0.3 and coordinates[i-3][1,11] < 0.3 and 
            coordinates[i+1][1,11]> 0.3 and coordinates[i + 2][1,11]> 0.3 and coordinates[i + 3][1,11]> 0.3):
                leftHand = True
            if rightHand or leftHand:
                StartPage.segments.append(i)

            rightHand = False
            leftHand = False

        return StartPage.segments
    def labelBox(self):
        self.labellingBox.destroy()
        self.labellingBox = tk.LabelFrame(self.page1,text = "LABELS")
        self.labellingBox.grid(row = 1,column = 0,rowspan = 10)
        sliderValues = [int(x) for x in self.slider.getValues()]
        sliderValues.insert(0,0)
        sliderValues.insert(len(self.data),len(self.data))
        for segment in range(len(sliderValues) - 1):
            tk.Label(self.labellingBox,text =\
                 f"Segment [{sliderValues[segment]} - {sliderValues[segment + 1]}] : Label = {self.labels[sliderValues[segment]]}"\
                     ).grid(row= segment,column = 0, padx = 20, pady = 5)

    def labelling(self,label,end):
        numbers = [int(x) for x in self.slider.getValues()]
        labelNames = {1:"collecting water", 2: "Hand washing", 3:"Mouth washing", 4:"Face washing", 5: "Arm washing", 6:"Head washing", 7:"Feet washing"}
        endPeriod = end
        if numbers.index(end + 1) != 0:
            start = numbers[numbers.index(end + 1) - 1]
        if numbers.index(end + 1) == 0:
            start = 0
        
        self.labels[start:endPeriod + 1] = label
        messagebox.showinfo("Notification", f"You labelled segment {start} - {end +1} as {labelNames[label] }")
        self.labelBox()
    
    def saveLabel(self):
        np.savetxt(os.path.join(StartPage.currentFile,'label.txt') ,self.labels)
        messagebox.showinfo("Notification", "You saved the label file")
    def playVideo(self,frame,end):
        try:
            image = ImageTk.PhotoImage(image = Image.fromarray(self.data[frame]))
        except IndexError:
            return
        self.videoScreen.configure(image = image)
        self.videoScreen.image = image
        self.frameNumber.configure(text = str(frame))
        if frame < end:
            global currentFrame
            currentFrame = frame
            root1 = self.root
            root1.after(self.videoSpeed, self.playVideo, frame+1,end)
    def addBoundary(self,boundary):
        StartPage.segments = self.slider.getValues()
        StartPage.segments.append(int(boundary))   
        self.refresh() 
    def DeleteBoundary(self,index):
        StartPage.segments = [int(x) for x in self.slider.getValues() ]
        if int(index) in StartPage.segments:
            StartPage.segments.remove(int(index))   
        self.refresh() 
    def speedControl(self,speed):
        self.videoSpeed = int(33 / speed)
    def goForward(self,currentNumber):
        numbers = [int(x) for x in self.slider.getValues()]
        if currentNumber == 0:
            self.playVideo(currentNumber,numbers[0])
        if currentNumber != 0:
            closestNumber = min(numbers, key=lambda x:abs(x-currentNumber))
            currentIndex = numbers.index(closestNumber )
            self.playVideo(closestNumber,numbers[currentIndex + 1])



    def goBackward(self,currentNumber):
        numbers = [int(x) for x in self.slider.getValues()]
        closestNumber = min(numbers, key=lambda x:abs(x-currentNumber))
        currentIndex = numbers.index(closestNumber)
        if currentIndex != 0:
            self.playVideo(numbers[currentIndex - 2],numbers[currentIndex - 1])

        if currentIndex ==0 or currentIndex ==1:
            self.playVideo(0,numbers[0])


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

    
   

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
