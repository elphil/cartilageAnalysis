import os
import cmath
import tkinter
import dataStruct
import pyqtgraph
from tkinter import filedialog
import matplotlib
from matplotlib import font_manager as fm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pdb
from pyqtgraph.Qt import QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout, QGroupBox, QLineEdit, QTableWidget, QTableWidgetItem
import pyqtgraph as pg

#dataText = '/media/group/hyper/archive/Measured_Data/2016_06_21/20160621_081835.mat'
dataText = '/raid/home/extern/rovedo/radial_recon/JK_radial_incLoopCoil/'
matplotlib.use("TkAgg")
matplotlib.rcParams.update({'font.size' : 10, 'figure.autolayout': True})
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Helvetica']#, 'DejaVu Sans']
#matplotlib.pyplot.tight_layout()
class mainWindow():
        def __init__(self):

                self.scanNumber = 4 
                self.selectedDataset = 1
                self.datasets = 0
                self.lowerLimit = 100
                self.upperLimit = 200
                self.roiChanged = 0

                #main figures
                DPI = 100
                heightMM = 160.0
                widthMM = 280.0

                self.app = QtGui.QApplication([])
                #self.window = QWidget()
                self.window = pg.GraphicsWindow(title="Thickness calculations")
                greyValue = 200
                self.window.setBackground((greyValue,greyValue,greyValue))
                self.fullPlot = pg.ImageView()
                self.fullPlot.fullRoi = self.fullPlot.getRoiPlot()
                self.roi = pg.ROI([200,200],[100,100])
                self.roi.addScaleHandle([1,1], [0,0])
                self.roi.addScaleHandle([1,0], [0,1])
                self.roi.addScaleHandle([0,1], [1,0])
                self.roi.addScaleHandle([0,0], [1,1])
                def updateRoi():
                    if self.datasets:
                        self.roiChanged = 1
                        self.guiData.rois[self.selectedDataset] = [self.roi.pos()[1] , self.roi.pos()[0], self.roi.size()[1], self.roi.size()[0]]
                        self.plotWindow(0)
                    #print('roi changed')
                def updateEdges():
                    if self.datasets:
                        self.findCurrentEdges()
                        self.plotWindow(0)
                self.roi.sigRegionChanged.connect(updateRoi)
                self.roi.sigRegionChangeFinished.connect(updateEdges)
                self.fullPlot.addItem(self.roi)
                self.fullPlot.fullRoi = self.roi

                self.roiPlot = pg.ImageView()
                self.edgePlot = pg.ImageView()
                self.resultPlot = pg.PlotWidget()
                #self.Roi = pg.LineSegmentROI([10,20], [110,100], pen='r')
                #self.fullPlot.addItem(self.Roi)

                self.layout = QVBoxLayout()
                self.layout.setDirection(2)
                self.layout.addWidget(self.fullPlot)  # plot goes on right side, spanning 3 rows
                self.layout.addWidget(self.roiPlot)  # plot goes on right side, spanning 3 rows
                self.layout.addWidget(self.edgePlot)  # plot goes on right side, spanning 3 rows
                self.layout.addWidget(self.resultPlot)
                #self.layout.addPlot()
                #self.layout.addWidget(self.resultPlot)
#Buttons layout
                self.buttonGroupBox = QGroupBox('buttons')
                self.buttonLayout = QVBoxLayout()
                self.buttonLayout.setDirection(0)
                self.buttonGroupBox.setLayout(self.buttonLayout)

                self.leftButtonBox = QGroupBox()
                self.leftButtonLayout = QVBoxLayout()
                self.leftButtonLayout.setDirection(2)

                self.searchDataButton = QPushButton('Search Data')
                self.searchDataButton.clicked.connect(self.searchDataCallback)
                self.leftButtonLayout.addWidget(self.searchDataButton)
                self.loadAllDataButton = QPushButton('Load All Data')
                self.loadAllDataButton.clicked.connect(self.loadAllDataCallback)
                self.leftButtonLayout.addWidget(self.loadAllDataButton)
                self.leftButtonBox.setLayout(self.leftButtonLayout)

                self.rightButtonBox = QGroupBox()
                self.rightButtonLayout = QVBoxLayout()
                self.rightButtonLayout.setDirection(2)
                self.upButton = QPushButton('up')
                self.upButton.clicked.connect(self.raiseScanCallback)
                self.downButton = QPushButton('down')
                self.downButton.clicked.connect(self.lowerScanCallback)
                self.rightButtonLayout.addWidget(self.upButton)
                self.rightButtonLayout.addWidget(self.downButton)
                self.rightButtonBox.setLayout(self.rightButtonLayout)

                self.calculateThicknessButton = QPushButton('Calculate Thickness')
                self.calculateThicknessButton.clicked.connect(self.calculateThickness)
                self.rightButtonLayout.addWidget(self.calculateThicknessButton)
                self.calculateAllThicknessesButton = QPushButton('Calculate all Thicknessses')
                self.calculateAllThicknessesButton.clicked.connect(self.calculateAllThicknesses)
                self.rightButtonLayout.addWidget(self.calculateAllThicknessesButton)
                #self.upButton = QPushButton('up')
                #Jself.upButton.clicked.connect(self.raiseScanCallback)

                self.dataTextBox = QLineEdit()
                self.dataTextBox.setText(dataText)
                
                self.scanNumberTextBox = QLineEdit()
                self.scanNumberTextBox.setText(str(self.scanNumber))
                self.datasetList = QTableWidget()
                self.datasetList.setColumnCount(3)
                self.datasetList.setHorizontalHeaderLabels(['Dataset', 'Loaded',''])
                self.datasetList.setColumnWidth(0, 500)
                self.datasetList.itemSelectionChanged.connect(self.setDatasetCallback)
                self.datasetList.resizeRowsToContents()

                
                self.layout.addWidget(self.buttonGroupBox)
                self.buttonLayout.addWidget(self.leftButtonBox)
                self.buttonLayout.addWidget(self.rightButtonBox)
                self.layout.addWidget(self.dataTextBox)
                self.layout.addWidget(self.datasetList)
                #self.layout.addWidget(self.leftButtonBox)
                
                #QPushButton
                #layout.addWidget(plot, 0, 1, 1, 1)  # plot goes on right side, spanning 3 rows
                self.window.setLayout(self.layout)
                self.window.show()
                #w.show()

                ## Start the Qt event loop


                #self.datasetList = tkinter.Listbox(self.top)
                #self.datasetList.grid(row=8, column=4, sticky = tkinter.W + tkinter.E)#, selectmode=EXTENDED)
                #def onSelection(event):
                #    eventWidget = event.widget
                #    self.selectedDataset = int(eventWidget.curselection()[0])
                #    print(self.selectedDataset)
                #    #self.plotWindow()
                #self.datasetList.bind('<<ListboxSelect>>', print('selected'))
                #self.datasetList.bind('<<ListboxSelect>>', onSelection)

                ###close main Window
                ##invoke main window
                self.app.exec_()
                #self.top.mainloop()
        def browseCallback(self):
                newDataFile = ''
                if self.runtimeFolder:
                    newDataFile =  filedialog.askopenfilename(initialdir = self.runtimeFolder, title = 'Please select a file')
                else:
                    newDataFile =  filedialog.askopenfilename(initialdir = '/raid/home/extern/rovedo/radial_recon/', title = 'Please select a data directory')
                self.runtimeFolder = os.path.dirname(newDataFile)
                self.saveString = self.runtimeFolder
                self.dataTextBox.delete("1.0", tkinter.END)
                self.dataTextBox.insert(tkinter.END, newDataFile)
                self.saveStringTextBox.delete("1.0", tkinter.END)
                self.saveStringTextBox.insert(tkinter.END, self.saveString)
        def loadSetCallback(self):
                self.dataString = self.dataTextBox.text().strip()
                print('dataset: ', self.selectedDataset)
                self.guiData = dataStruct.data(self.dataString)
                self.guiData.findDataDirs()
                self.guiData.initializeData()
                self.guiData.readSet(self.selectedDataset)
                self.datasetList.clear()
                for dataset in self.guiData.rootFolders:
                    print(dataset)
                    self.datasetList.insertRow(self.datasetList.rowCount() )
                    #[os.path.basename(os.path.normpath(dataset))]
                self.plotWindow(1)
        def loadAllDataCallback(self):
                self.dataString = self.dataTextBox.text().strip()
                self.guiData = dataStruct.data(self.dataString)
                self.guiData.readAll()
                self.datasetList.clear()
                for dataset in self.guiData.rootFolders:
                    print(dataset)
                    #self.datasetList.insert(tkinter.END, os.path.basename(os.path.normpath(dataset)))
                    self.datasetList.insertRow(self.datasetList.rowCount())
                self.plotWindow(1)
                #pdb.set_trace()
        def searchDataCallback(self):
                self.dataString = self.dataTextBox.text().strip()
                self.guiData = dataStruct.data(self.dataString)
                self.guiData.findDataDirs()
                self.guiData.initializeData()
                #self.datasetList.clear()
                for row in np.arange(self.datasetList.rowCount()-1, -1, -1):
                    print('row:', row)
                    self.datasetList.removeRow(row)
                for dataset in self.guiData.rootFolders:
                    self.datasets +=1
                    row = self.datasetList.rowCount()
                    self.datasetList.insertRow(row)
                    self.datasetList.setItem(row,0, QTableWidgetItem(os.path.basename(os.path.normpath(dataset))))
                self.guiData.rois[self.selectedDataset]=[100,50,200,200]
                self.plotWindow(1)
        def fftGuiData(self):
                self.guiData.fft(omitSamples = int(self.omitSamplesTextBox.get("1.0",tkinter.END).strip()), sumScans = self.sumDataVar.get(), zeroFill = int(self.zeroFillStringVar.get()))
                if self.sumDataVar.get():
                        self.plotWindow(1)
                else:
                        self.plotWindow(1)
        def raiseScanCallback(self):
                if self.scanNumber < len(self.guiData.data[self.selectedDataset])-1:
                        self.scanNumber +=1
                        #self.scanNumberString.set(self.scanNumber)
                self.setScanCallback()
        def lowerScanCallback(self):
                if self.scanNumber > 0:
                        self.scanNumber -=1
                        #self.scanNumberString.set(self.scanNumber)
                self.setScanCallback()
        def setDatasetCallback(self):
            if(self.datasetList.selectedItems()):
                self.selectedDataset = self.datasetList.selectedItems()[0].row()
                self.plotWindow(1)
        def setScanCallback(self):
            #newNumber = int(self.scanNumberTextBox.text().strip())
            newNumber = self.scanNumber
            if newNumber < len(self.guiData.data[self.selectedDataset])-1 and newNumber >= 0:
                self.scanNumber = newNumber
            self.plotWindow(1)
        def fitFunction(self, data, *parameters):
                #return np.zeros(data.shape[0]) #real fit function is returned by self.guiData.fit
                return parameters[0] / (np.pi * (data - parameters[1])**2/parameters[2] + (parameters[2]))
        def setPhase(self, scanNumber):
                if self.sumDataVar.get():
                        self.guiData.summedPhase = float(self.phaseStringVar.get())
                        self.plotWindow(1)
                else:
                        self.guiData.phase[scanNumber] = float(self.phaseStringVar.get())
                        self.plotWindow(1)
        def fitGuiData(self):
                frequency = float(self.frequencyParameter.get()) if self.frequencyParameter.get() else (int(self.maxFrequencyEntry.get())+int(self.minFrequencyEntry.get()))/2
                width = float(self.widthParameter.get()) if self.widthParameter.get() else (int(self.maxFrequencyEntry.get())-int(self.minFrequencyEntry.get()))/100
                #height = self.heightParameter.get() if self.heightParameter.get() else np.max(self.guiData.fftData[self.scanNumber])
                if self.heightParameter.get():
                        height = float(self.heightParameter.get())
                elif self.guiData.summedFftData.any():
                        height = np.real(np.max(self.guiData.summedFftData[self.guiData.getIndex(int(self.minFrequencyEntry.get())):self.guiData.getIndex(int(self.maxFrequencyEntry.get()))]))
                elif self.guiData.fftData.any():
                        height = np.real(np.max(self.guiData.fftData[self.scanNumber, self.guiData.getIndex(int(self.minFrequencyEntry.get())):self.guiData.getIndex(int(self.maxFrequencyEntry.get()))]))
                else:
                        height = 1;
                if self.sumDataVar.get():
                        self.guiData.summedFitParameters = [height, frequency, width]
                else:
                        self.guiData.fitParameters[self.scanNumber] = [height, frequency, width]
                self.fitFunction, tempParameters = self.guiData.fit(int(self.minFrequencyEntry.get()), int(self.maxFrequencyEntry.get()), self.scanNumber, self.guiData.function, self.sumDataVar.get())
                if self.sumDataVar.get():
                        self.guiData.summedFitParameters = tempParameters[0]
                else:
                        self.guiData.fitParameters[self.scanNumber] = tempParameters[0]
                self.frequencyParameter.delete(0,tkinter.END)
                self.widthParameter.delete(0,tkinter.END)
                self.heightParameter.delete(0,tkinter.END)
                self.frequencyParameter.insert(0, tempParameters[0][1])
                self.widthParameter.insert(0,tempParameters[0][2])
                self.heightParameter.insert(0, tempParameters[0][0])

                self.plotWindow(1)
                self.guiData.saveParameters()
        def plotExternal(self):
            if plt.fignum_exists(0):
                plt.clf()
            plt.figure(0, figsize=[6,3])
            plt.xlabel('f / MHz')
            plt.ylabel('signal / a.u.')
            if self.guiData:
                    lowerIndex = self.guiData.getIndex(int(self.minFrequencyEntry.get()))
                    upperIndex = self.guiData.getIndex(int(self.maxFrequencyEntry.get()))
                    if self.sumDataVar.get():
                        self.guiData.fft(omitSamples = 1000, sumScans = self.sumDataVar.get(), zeroFill = int(self.zeroFillStringVar.get()))
                        plt.plot(self.guiData.frequencies[lowerIndex:upperIndex]/1e6, 100 * np.real(cmath.exp(1j*self.guiData.summedPhase)*  self.guiData.summedFftData[-self.guiData.frequencies.size+lowerIndex:-self.guiData.frequencies.size+upperIndex]), label='1000 samples x 100')
                        self.guiData.fft(omitSamples = 500, sumScans = self.sumDataVar.get(), zeroFill = int(self.zeroFillStringVar.get()))
                        plt.plot(self.guiData.frequencies[lowerIndex:upperIndex]/1e6, np.real(cmath.exp(1j*self.guiData.summedPhase)*  self.guiData.summedFftData[-self.guiData.frequencies.size+lowerIndex:-self.guiData.frequencies.size+upperIndex]), label = '500 samples')
            plt.legend()
            #plt.savefig('/home/philipp/Documents/thesis/figures/experiments/lowFieldSpectrometer/niNetworkAnalysis.pdf')
            plt.show()
        def plotWindow(self, plotMain):
                #try:
                if not self.guiData.data[self.selectedDataset][self.scanNumber].any():
                    self.guiData.readSingle(self.selectedDataset, self.scanNumber)
                    print('plot: reading single')
                #self.fullPlot.clear()
                if(plotMain):
                    self.fullPlot.setImage(self.guiData.data[self.selectedDataset][self.scanNumber][:,:,1])
                #self.fullPlot.plot(self.guiData.data[self.selectedDataset][self.scanNumber])
                if self.guiData.rois[self.selectedDataset][2]+self.guiData.rois[self.selectedDataset][3]:
                    self.roiPlot.setImage(self.guiData.data[self.selectedDataset][self.scanNumber][self.guiData.rois[self.selectedDataset][1]:self.guiData.rois[self.selectedDataset][1]+self.guiData.rois[self.selectedDataset][3],self.guiData.rois[self.selectedDataset][0]:self.guiData.rois[self.selectedDataset][0]+self.guiData.rois[self.selectedDataset][2],:][:,:,0])
                else:
                    self.roiPlot.setImage(self.guiData.data[self.selectedDataset][self.scanNumber][:,:,0])
                if self.guiData.edgeData[self.selectedDataset][self.scanNumber].any():
                    self.edgePlot.setImage(self.guiData.edgeData[self.selectedDataset][self.scanNumber])
                    #self.subplotEdges.setImage(self.guiData.data[self.selectedDataset][self.scanNumber])
                elif self.guiData.rois[self.selectedDataset][2]+self.guiData.rois[self.selectedDataset][3]:
                    self.findCurrentEdges()
                    self.edgePlot.setImage(self.guiData.edgeData[self.selectedDataset][self.scanNumber])
                #self.plotCanvas.draw()
                #image = pyqtgraph.imageview(self.guiData.edgeData[self.selectedDataset][self.scanNumber])
                #image.show()
                #self.findCurrentEdges()for testing only
                        #plt.imshow(self.guiData.data[self.selectedDataset][scanNumber])
                        #plt.show()
                #except AttributeError:
                #        print("Please load a dataset")
                #except IndexError:
                #        print("Please check parameters")
                #except ValueError:
                #        print("wrong parameters entered")
                #self.minFrequencyEntry.focus_set()
        def defineRoi(self):
            subImageRoi = cv2.selectROI('ROI selection', self.guiData.data[self.selectedDataset][self.scanNumber])
            self.guiData.rois[self.selectedDataset] = subImageRoi
            self.findCurrentEdges()
            cv2.destroyWindow('ROI selection')
            self.plotWindow(1)
        def findCurrentEdges(self):
            if self.guiData.rois[self.selectedDataset][2]+self.guiData.rois[self.selectedDataset][3]:
                print('roi found')
                labelImage = self.guiData.data[self.selectedDataset][self.scanNumber][self.guiData.rois[self.selectedDataset][1]:self.guiData.rois[self.selectedDataset][1]+self.guiData.rois[self.selectedDataset][3],self.guiData.rois[self.selectedDataset][0]:self.guiData.rois[self.selectedDataset][0]+self.guiData.rois[self.selectedDataset][2],:]
                edges = cv2.Canny(self.guiData.data[self.selectedDataset][self.scanNumber][self.guiData.rois[self.selectedDataset][1]:self.guiData.rois[self.selectedDataset][1]+self.guiData.rois[self.selectedDataset][3],self.guiData.rois[self.selectedDataset][0]:self.guiData.rois[self.selectedDataset][0]+self.guiData.rois[self.selectedDataset][2],:], self.lowerLimit, self.upperLimit)
                edges, labelImage = cv2.connectedComponents(edges)
                self.guiData.edgeData[self.selectedDataset][self.scanNumber] = labelImage
                #self.subplotEdges.imshow(self.guiData.edgeData[self.selectedDataset][self.scanNumber])
                #self.plotCanvas.draw()
            else:
                print('Roi misdefinded or no roi found')
        def calculateThickness(self):
            if self.guiData.edgeData[self.selectedDataset][self.scanNumber].any():
                readVectorY = np.arange(self.guiData.edgeData[self.selectedDataset][self.scanNumber].shape[0])
                readVectorX = np.arange(self.guiData.edgeData[self.selectedDataset][self.scanNumber].shape[1])
                edge1 = np.where(self.guiData.edgeData[self.selectedDataset][self.scanNumber]==1, 1, 0)
                edge2 = np.where(self.guiData.edgeData[self.selectedDataset][self.scanNumber]==2, 1, 0)
                n1 = np.sum(edge1)
                n2 = np.sum(edge2)
                x1 = np.sum(np.dot(edge1, readVectorX)/n1)
                y1 = np.sum(np.dot(np.transpose(edge1), readVectorY))/n1
                x2 = np.sum(np.dot(edge2, readVectorX)/n2)
                y2 = np.sum(np.dot(np.transpose(edge2), readVectorY))/n2
                #pdb.set_trace()
                print(np.abs(x2 - x1))
                return(np.abs(x2 - x1))
            else:
                return(np.nan)
        def findAllEdges(self):
            for scanNumber in np.arange(4,len(self.guiData.data[self.selectedDataset])):
                self.scanNumber = scanNumber
                self.findCurrentEdges()
            #self.plotCanvas.draw()
        def calculateAllThicknesses(self):
            if self.roiChanged:
                self.findAllEdges()
            self.scanNumber = 0
            for image in self.guiData.data[self.selectedDataset]:
                if image.any():
                    print('image found, calc...')
                    self.guiData.thicknesses[self.selectedDataset][self.scanNumber] = self.calculateThickness()
                else:
                    print('image not found, laoding and calc...')
                    self.guiData.readSingle(self.selectedDataset, self.scanNumber)
                    self.findCurrentEdges()
                    self.guiData.thicknesses[self.selectedDataset][self.scanNumber] = self.calculateThickness()
                self.scanNumber +=1
            self.scanNumber = 4
            print('thicknesses calculated')
            print(self.guiData.thicknesses[self.selectedDataset] )
            #self.resultPlot.plot(np.arange(len(self.guiData.thicknesses[self.selectedDataset])), self.guiData.thicknesses[self.selectedDataset])
            self.resultPlot.clear()
            self.resultPlot.plot(self.guiData.thicknesses[self.selectedDataset][4:-1])
            #pdb.set_trace()
        def saveCallback(self):
            self.saveString = self.saveStringTextBox.get("1.0", tkinter.END).rstrip()
            print( 'saveString' + self.saveString)
            print(self.saveString + '/' +  os.path.splitext(os.path.basename(self.dataString))[0] + '.pdf')
            self.figure.savefig(self.saveString + '/' +  os.path.splitext(os.path.basename(self.dataString))[0] + '.pdf')
        def closeCallback(self):
                self.top.destroy()
