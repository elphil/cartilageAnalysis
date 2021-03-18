#!/usr/bin/python
import sys
import tkinter
import dataStruct
import pyqtgraph
import os
import numpy as np
import cv2
import pdb
from pyqtgraph.Qt import QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem, QSlider, QLabel, QFileDialog, QListWidget, QListWidgetItem, QAbstractItemView
import pyqtgraph as pg
import pyqtgraph.exporters
import pickle
import customImageView
from customDebug import set_trace
dataText = '/raid/home/extern/rovedo/radial_recon/PH_1eco_5eco/MID573_CGSENSEl2_acc1_accCsm1_lambda0.3_nImages2200_spokesPerImage400'
class mainWindow():
        def __init__(self):
                self.overrideType = 0
                self.datasets = []
                self.filetype = 'png'
                self.scanNumber = 4 
                self.selectedDataset = 0
                self.nDatasets = 0
                self.lowerLimit = 300
                self.upperLimit = 400
                self.roiChanged = 0
                self.runtimeFolder = dataText
#########Main window
                self.app = QtGui.QApplication([])
                self.window = pg.GraphicsWindow(title="Thickness calculations")
                greyValue = 200
                self.window.setBackground((greyValue,greyValue,greyValue))
############Plot regions and layout
                self.fullPlot = pg.ImageView()
                self.fullPlot.ui.roiBtn.hide()
                self.fullPlot.ui.menuBtn.hide()

                self.roiPlot = customImageView.customImageView(self)
                self.roiPlot.ui.roiBtn.hide()
                self.roiPlot.ui.menuBtn.hide()

                self.edgePlot = pg.ImageView()
                self.edgePlot.ui.roiBtn.hide()
                self.edgePlot.ui.menuBtn.hide()
                self.edgePlot.ui.histogram.hide()

                self.resultPlot = pg.PlotWidget()
                self.resultPlot.getPlotItem().setLabel('left', 'thickness / mm')
                self.resultPlot.getPlotItem().setLabel('bottom', 'time / s')
#########Roi generation and functions for full plot
                self.roi = pg.ROI([200,200],[100,100])
                self.roi.addScaleHandle([1,1], [0,0])
                self.roi.addScaleHandle([1,0], [0,1])
                self.roi.addScaleHandle([0,1], [1,0])
                self.roi.addScaleHandle([0,0], [1,1])
                self.roiClipboard = pg.ROI([200,200],[100,100])
                #self.fullPlot.fullRoi = self.fullPlot.getRoiPlot()
                self.fullPlot.fullRoi = self.roi
                def updateRoi():
                    if self.nDatasets:
                        self.roiChanged = 1
                        #self.calculateAllMeans()
                        self.plotWindow(0)
                def updateRoiEnd():
                    if self.nDatasets:
                        for index, currentImage in enumerate(self.datasets[self.selectedDataset].data):
                            if self.datasets[self.selectedDataset].loaded[index] and self.roiChanged:
                                self.findCurrentEdges(index)
                        self.datasets[self.selectedDataset].roi = self.fullPlot.fullRoi.saveState()
                        self.roiChanged = 0
                        self.plotWindow(0)
                self.roi.sigRegionChanged.connect(updateRoi)
                self.roi.sigRegionChangeFinished.connect(updateRoiEnd)
                self.fullPlot.addItem(self.roi)
#############Buttons layout
                self.buttonLayout = QGridLayout()
             #Data Handling
                self.leftButtonBox = QGroupBox('Data Handling')
                self.leftButtonLayout = QVBoxLayout()

                self.browseButton = QPushButton('Browse directories...')
                self.browseButton.clicked.connect(self.browseCallback)
                self.leftButtonLayout.addWidget(self.browseButton)
                self.searchDataButton = QPushButton('Search Data')
                self.searchDataButton.clicked.connect(self.searchDataCallback)
                self.leftButtonLayout.addWidget(self.searchDataButton)
                self.loadAllDataButton = QPushButton('Load All Data')
                self.loadAllDataButton.clicked.connect(self.loadAllDataCallback)#AllDataCallback)
                self.leftButtonLayout.addWidget(self.loadAllDataButton)
                self.leftButtonBox.setLayout(self.leftButtonLayout)
                self.upButton = QPushButton('up')
                self.upButton.clicked.connect(self.raiseScanCallback)
                self.downButton = QPushButton('down')
                self.downButton.clicked.connect(self.lowerScanCallback)
                self.leftButtonLayout.addWidget(self.upButton)
                self.leftButtonLayout.addWidget(self.downButton)
            #RoiManipulationBox
                self.roiButtonBox = QGroupBox('Roi Manipulation')
                self.roiButtonBoxLayout = QGridLayout()
                self.roiButtonBox.setLayout(self.roiButtonBoxLayout)

                self.copyButton = QPushButton('Copy Roi')
                self.copyButton.clicked.connect(self.copyRoiCallback)
                self.roiButtonBoxLayout.addWidget(self.copyButton, 0, 0,)

                self.pasteButton = QPushButton('Paste Roi')
                self.pasteButton.clicked.connect(self.pasteRoiCallback)
                self.roiButtonBoxLayout.addWidget(self.pasteButton, 1, 0)
                self.pasteToAllButton = QPushButton('Paste Roi to All')
                self.pasteToAllButton.clicked.connect(self.pasteRoiToAll)
                self.roiButtonBoxLayout.addWidget(self.pasteToAllButton, 2, 0)

                self.saveButton = QPushButton('Save Roi')
                self.saveButton.clicked.connect(self.saveRoiCallback)
                self.roiButtonBoxLayout.addWidget(self.saveButton, 3, 0)
                self.saveAllButton = QPushButton('Save all Rois')
                self.saveAllButton.clicked.connect(self.saveAllRoisCallback)
                self.roiButtonBoxLayout.addWidget(self.saveAllButton, 4, 0)
                self.leftButtonLayout.addWidget(self.roiButtonBox)
            #Calculations
                self.rightButtonBox = QGroupBox('Calculations')
                self.rightButtonLayout = QGridLayout()
                self.rightButtonBox.setLayout(self.rightButtonLayout)

                self.calculateThicknessButton = QPushButton('Calculate Thickness')
                self.calculateThicknessButton.clicked.connect(self.calculateThickness)
                self.rightButtonLayout.addWidget(self.calculateThicknessButton, 3,0, 1, 2)

                self.calculateAllThicknessesButton = QPushButton('Calculate all Thicknesses')
                self.calculateAllThicknessesButton.clicked.connect(self.calculateAllThicknesses)
                self.rightButtonLayout.addWidget(self.calculateAllThicknessesButton, 4, 0, 1, 2)

                self.saveThicknessesButton = QPushButton('Save Thicknesses')
                self.saveThicknessesButton.clicked.connect(self.saveThicknessesCallback)
                self.rightButtonLayout.addWidget(self.saveThicknessesButton, 5, 0, 1, 2)


                self.saveToTextBox = QLineEdit()
                self.saveToTextBox.setText('../60')
                self.rightButtonLayout.addWidget(self.saveToTextBox, 6, 0, 1, 2)

                self.savePlotsButton = QPushButton('Save Plots')
                self.savePlotsButton.clicked.connect(self.savePlotsCallback)
                self.rightButtonLayout.addWidget(self.savePlotsButton, 7, 0, 1, 2)
#############Sliders for edge detection limits
                self.lowerLimitSlider = QSlider()
                self.lowerLimitLabel = QLabel()
                self.upperLimitSlider = QSlider()
                self.upperLimitLabel = QLabel()

                self.lowerLimitSlider.setOrientation(1)
                self.lowerLimitSlider.setMaximum(20*255)
                self.lowerLimitSlider.setValue(self.lowerLimit)
                self.lowerLimitSlider.valueChanged.connect(self.setEdgeLimits)

                self.upperLimitSlider.setOrientation(1)
                self.upperLimitSlider.setMaximum(20*255)
                self.upperLimitSlider.setValue(self.upperLimit)
                self.upperLimitSlider.valueChanged.connect(self.setEdgeLimits)

                self.rightButtonLayout.addWidget(self.lowerLimitSlider, 8, 0)
                self.rightButtonLayout.addWidget(self.lowerLimitLabel, 8, 1)
                self.rightButtonLayout.addWidget(self.upperLimitSlider, 9, 0)
                self.rightButtonLayout.addWidget(self.upperLimitLabel, 9, 1)
                
                self.upperLimitLabel.setNum(self.upperLimitSlider.value())
                self.lowerLimitLabel.setNum(self.lowerLimitSlider.value())

                self.buttonLayout.addWidget(self.leftButtonBox, 1, 0)
                self.buttonLayout.addWidget(self.rightButtonBox, 1,1)
##########Slider for scan selection
                self.scanSliderBox = QGroupBox('Scan Number')
                self.scanSlider = QSlider()
                self.scanSliderLabel = QLineEdit()
                self.scanSliderLabel.textEdited.connect(self.textEditedCallback)
                self.scanSliderLabel.setMaximumWidth(30)
                self.scanSliderLabel.setText(str(self.scanNumber))
                self.scanSlider.setOrientation(1)
                self.scanSlider.setMaximum(1)
                self.scanSlider.setValue(0)
                self.scanSlider.valueChanged.connect(self.scanSliderCallback)
                self.scanSliderLayout = QGridLayout()
                self.scanSliderLayout.addWidget(self.scanSlider, 0,0)
                self.scanSliderLayout.addWidget(self.scanSliderLabel, 0,1)
                self.scanSlider.setFixedHeight(50)
                self.scanSliderBox.setMaximumHeight(100)
                self.scanSliderBox.setLayout(self.scanSliderLayout)

                self.buttonLayout.addWidget(self.scanSliderBox,0,0,1,2)
                #self.buttonLayout.addLayout(self.scanSliderLayout,0,0,1,2)

###########Path to data
                self.dataTextBox = QLineEdit()
                self.dataTextBox.setText(dataText)
                self.scanNumberTextBox = QLineEdit()
                self.scanNumberTextBox.setText(str(self.scanNumber))

                self.tableWidget = QTableWidget(0,8)
                self.tableWidget.setHorizontalHeaderLabels(['MID', 'norm','acc', 'accCSM', 'lambda', 'nImages', 'spokesPerImage', 'datasetNumber'])
                #self.tableWidget.setColumnHidden(7, True)
                #self.tableWidget.setColumnWidth(0, 500)
                self.tableWidget.itemSelectionChanged.connect(self.setDatasetCallback)
                self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.datasetListWidget = QListWidget()
                #self.tableWidget.resizeRowsToContents()

                #self.datasetList = QListWidget()
           #####Main layout
                self.layout = QGridLayout() #main layout for window
                self.layout.setColumnMinimumWidth(0, 800)
                self.layout.addWidget(self.fullPlot, 0, 0, 2, 1)
                self.layout.addWidget(self.edgePlot, 1, 1)
                self.layout.addWidget(self.roiPlot, 0, 1)
                self.layout.addWidget(self.resultPlot, 2, 0, 2 ,2)
                self.layout.setRowMinimumHeight(3, 400)
                self.layout.addWidget(self.dataTextBox, 2, 2, 1, 1)
                self.layout.addLayout(self.buttonLayout, 3,2)

                self.layout.addWidget(self.tableWidget, 0, 2, 2, 1)
                #self.layout.addWidget(self.datasetList, 0, 2, 2, 1)
                self.window.setLayout(self.layout)
                self.window.show()
                sys.exit(self.app.exec_())
        def browseCallback(self):
                newDataFile = ''
                if self.runtimeFolder:
                    newDataFile =  QFileDialog.getExistingDirectory(None, 'Please select a data directory', self.runtimeFolder )
                else:
                    newDataFile =  QFileDialog.getExistingDirectory(None, 'Please select a data directory', '/raid/home/extern/rovedo/radial_recon/' )
                if newDataFile:
                    #print(newDataFile)
                    self.runtimeFolder = newDataFile#os.path.dirname(newDataFile)
                    #print(self.runtimeFolder)
                else:
                    self.runtimeFolder = ''
                    return 0
                self.saveString = self.runtimeFolder
                self.dataTextBox.setText(self.runtimeFolder)
                self.searchDataCallback()
        def searchDataCallback(self):
                self.selectedDataset = 0
                self.runtimeFolder = self.dataTextBox.text().strip()
                self.findDataDirs()
                self.initializeData()
                self.scanSlider.setMaximum(len(self.datasets[self.selectedDataset].data)-1)
                #for row in np.arange(self.tableWidget.rowCount()-1, -1, -1):
                #    self.tableWidget.removeRow(row)
                self.populateDatasetList()
                self.setScanCallback()
        def populateDatasetList(self):
            self.nDatasets = 0
            self.tableWidget.setRowCount(len(self.datasets))
            for setNumber,dataset in enumerate(self.datasets):
                self.nDatasets +=1
                items = []
                #self.tableWidget.insertRow(setNumber)
                items.append(QTableWidgetItem(('   ' + str(dataset.MID))[-5:]))
                items.append(QTableWidgetItem(('    ' + str(dataset.norm))[-2:]))
                items.append(QTableWidgetItem(('    ' + str(dataset.acc))[-1:]))
                items.append(QTableWidgetItem(('    ' + str(dataset.accCsm))[-1:]))
                items.append(QTableWidgetItem(('    ' + str(dataset.lam))[-1:]))
                items.append(QTableWidgetItem(('    ' + str(dataset.nImages))[-4:]))
                items.append(QTableWidgetItem(('    ' + str(dataset.spokesPerImage))[-4:]))
                items.append(QTableWidgetItem(str(setNumber)))
                for column, item in enumerate(items):
                    #self.tableWidget.insertRow(setNumber)
                    self.tableWidget.setItem(setNumber, column, item)
                #self.datasetListWidget.clicked
            #self.tableWidget.setSizeIncrement
            self.tableWidget.setSortingEnabled(True)
            #self.tableWidget.setColumnHidden(7, True)
        def findDataDirs(self):
            if self.overrideType != 0:
                    self.filetype = 'png' #read from text field later
            oldSets = self.datasets
            self.datasets = []
            print(self.datasets)
            for root, dirs, files in os.walk(self.runtimeFolder):
                if "images" in dirs:
                    self.datasets.append(dataStruct.data(root))
            print(self.datasets)
            self.nImagesets = len(self.datasets)
            if self.nImagesets == 0:
                self.datasets = oldSets
            #for currentSet in np.arange(self.nImagesets):
            for currentSet in self.datasets:
                    currentSet.imageFiles = [files for files in os.listdir(os.path.join(currentSet.rootFolder, "images" )) if files.endswith('.'+ self.filetype)]
        def initializeData(self):
                for currentSet in self.datasets:
                    currentSet.initialize()
                self.fullPlot.fullRoi.setState(self.datasets[self.selectedDataset].roi)
        def loadSetCallback(self):
                print('read: ', self.selectedDataset)
                self.datasets[self.selectedDataset].readSet()
        def loadAllDataCallback(self):
                self.runtimeFolder = self.dataTextBox.text().strip()
                self.searchDataCallback()
                self.initializeData()
                for dataset in self.datasets:
                    print(dataset)
                    dataset.readSet()
                self.calculateAllMeans()
                self.plotWindow(1)
        def setDatasetCallback(self):
            if(self.tableWidget.selectedItems()):
                #set_trace()
                #print(self.tableWidget.selectedItems()[6].text)
                self.selectedDataset = int(self.tableWidget.selectedItems()[7].text())
                self.fullPlot.fullRoi.setState(self.datasets[self.selectedDataset].roi)
                self.scanSlider.setMaximum(len(self.datasets[self.selectedDataset].data)-1)
                if self.scanNumber >= len(self.datasets[self.selectedDataset].data):
                    self.scanNumber = len(self.datasets[self.selectedDataset].data)
                    self.scanSlider.setValue(len(self.datasets[self.selectedDataset].data)-1)
                else:
                    self.scanSlider.setValue(self.scanNumber)
                self.setScanCallback()
        def scanSliderCallback(self):
            self.scanNumber = self.scanSlider.value()
            self.scanSliderLabel.setText(str(self.scanSlider.value()))
            self.setScanCallback()
        def textEditedCallback(self):
            newScanNumber = -1
            if self.scanSliderLabel.text() == '':
                return
            try:
                newScanNumber = int(self.scanSliderLabel.text())
                self.scanSliderLabel.setText('')
            except:
                print("Scan Number error: enter valid string to convert to int")
                return
            if newScanNumber < 0:
                newScanNumber = 0
            if newScanNumber > len(self.datasets[self.selectedDataset].data):
                newScanNumber = len(self.datasets[self.selectedDataset].data)-1
            self.scanNumber = newScanNumber
            self.setScanCallback()
        def setSlider(self):
            self.scanSlider.blockSignals(True)
            self.scanSlider.setValue(self.scanNumber)
            self.scanSliderLabel.setText(str(self.scanSlider.value()))
            self.scanSlider.blockSignals(False)
        def raiseScanCallback(self):
                if self.scanNumber < len(self.datasets[self.selectedDataset].data)-1:
                    self.scanNumber +=1
                    self.setScanCallback()
        def lowerScanCallback(self):
                if self.scanNumber > 0:
                    self.scanNumber -=1
                    self.setScanCallback()
        def setScanCallback(self):
            newNumber = self.scanNumber
            if not self.datasets[self.selectedDataset].data[self.scanNumber].any():
                self.datasets[self.selectedDataset].readSingle(self.scanNumber)
            if not self.datasets[self.selectedDataset].thicknesses[self.scanNumber]:
                self.calculateThickness()
            if not self.datasets[self.selectedDataset].means[self.scanNumber]:
                self.calculateMean()
            #if self.datasets[self.selectedDataset].roiChanged[self.scanNumber]:
            #    self.findCurrentEdges()
            #self.findCurrentEdges()
            if newNumber < len(self.datasets[self.selectedDataset].data)-1 and newNumber >= 0:
                self.scanNumber = newNumber
            self.plotWindow(1)
            self.setSlider()
        def savePlotsCallback(self):
            resolution = 400
            saveTo = self.saveToTextBox.text()
            fullPlotExporter = pg.exporters.ImageExporter(self.fullPlot.getImageItem())
            fullPlotExporter.parameters().param('width').setValue(resolution, blockSignal=fullPlotExporter.widthChanged)
            fullPlotExporter.parameters().param('height').setValue(resolution, blockSignal=fullPlotExporter.heightChanged)
            fullPlotExporter.export(os.path.join(self.datasets[self.selectedDataset].rootFolder,saveTo + 'full.png'))
            resolution = 400
            resultPlotExporter = pg.exporters.ImageExporter(self.resultPlot.getPlotItem())
            resultPlotExporter.parameters().param('width').setValue(resolution*2, blockSignal=resultPlotExporter.widthChanged)
            resultPlotExporter.parameters().param('height').setValue(resolution, blockSignal=resultPlotExporter.heightChanged)
            resultPlotExporter.export(os.path.join(self.datasets[self.selectedDataset].rootFolder,saveTo + 'result.png'))
        def plotWindow(self, plotMain, autoZoom = False):
                #print(self.selectedDataset, self.scanNumber)
                try:
                    if(plotMain):
                        self.fullPlot.setImage(self.datasets[self.selectedDataset].data[self.scanNumber], autoRange=autoZoom)
                        #print(self.datasets[self.selectedDataset].data[self.scanNumber])
                except:
                    print('could not plot main image, probably empty')
                try:
                    if self.fullPlot.fullRoi.size()[0]:
                        self.roiPlot.setImage(self.datasets[self.selectedDataset].data[self.scanNumber][int(self.fullPlot.fullRoi.pos()[0]):int(self.fullPlot.fullRoi.pos()[0])+int(self.fullPlot.fullRoi.size()[0]), int(self.fullPlot.fullRoi.pos()[1]):int(self.fullPlot.fullRoi.pos()[1])+int(self.fullPlot.fullRoi.size()[1])])
                    else:
                        self.roiPlot.setImage(self.datasets[self.selectedDataset].data[self.scanNumber])
                except:
                    print('could not plot Roi image, probably empty')
                try:
                    if self.datasets[self.selectedDataset].edgeData[self.scanNumber].any():
                        self.edgePlot.setImage(self.datasets[self.selectedDataset].edgeData[self.scanNumber])
                    elif self.fullPlot.fullRoi.size()[0]+self.fullPlot.fullRoi.size()[1]:
                        print('else, probalbly no edges detected')
                        self.findCurrentEdges()
                        self.edgePlot.setImage(self.datasets[self.selectedDataset].edgeData[self.scanNumber])
                except:
                    print('could not plot Roi image, probably empty')
                self.updateResultPlot()
        def defineRoi(self):
            subImageRoi = cv2.selectROI('ROI selection', self.datasets[self.selectedDataset].data[self.scanNumber])
            self.datasets[self.selectedDataset].roi = subImageRoi
            self.findCurrentEdges()
            cv2.destroyWindow('ROI selection')
            self.plotWindow(1)
        def setEdgeLimits(self):
            self.lowerLimit = self.lowerLimitSlider.value()
            self.lowerLimitLabel.setText(str(self.lowerLimit))
            self.upperLimit = self.upperLimitSlider.value()
            self.upperLimitLabel.setText(str(self.upperLimit))
            self.findCurrentEdges()
            self.plotWindow(0)
        def findCurrentEdges(self, scanNumber = -1):
            if scanNumber == -1:
                scanNumber = self.scanNumber
            if self.fullPlot.fullRoi.size()[0] and self.fullPlot.fullRoi.size()[1]:
                labelImage = self.datasets[self.selectedDataset].data[scanNumber][int(self.fullPlot.fullRoi.pos()[0]):int(self.fullPlot.fullRoi.pos()[0])+int(self.fullPlot.fullRoi.size()[0]),int(self.fullPlot.fullRoi.pos()[1]):int(self.fullPlot.fullRoi.pos()[1])+int(self.fullPlot.fullRoi.size()[1])]
                #print( 'size label image: ' + str(np.shape(labelImage)) + ' before:' + str(labelImage[1, 1]) + ' \n max label image: ' + str(np.max(labelImage)) + ' element*255/max: ' + str(labelImage[1,1] * 255 / np.max(labelImage)))

                #labelImage = labelImage[1]
                labelImage = np.uint8(labelImage *  255. / np.max(labelImage))
                #labelImage = cv2.resize (labelImage, None, fx=2, fy=4) #interpolation in image plane
                #try:
                edges = cv2.Canny(labelImage, self.lowerLimit, self.upperLimit, None, 5, L2gradient=True)
                edges, labelImage = cv2.connectedComponents(edges)
                self.datasets[self.selectedDataset].edgeData[scanNumber] = labelImage
                    #if self.datasets[self.selectedDataset].edgeData[self.scanNumber].any():#edges[scanNumber].any():
                        #self.plotWindow(0)
                #except:
                #    print('Error finding current edges')
            else:
                print('Roi misdefinded or no roi found')
        def findAllEdges(self):
            #self.loadSetCallback()
            print('finding all edges')
            for scanNumber in np.arange(len(self.datasets[self.selectedDataset].data)):
                self.scanNumber = scanNumber
                self.findCurrentEdges()
        def calculateThickness(self):
            self.findCurrentEdges()
            if np.any(self.datasets[self.selectedDataset].edgeData[self.scanNumber] == 3):
                return np.nan # No thickness if more than 2 edges detectedi, i.e. connected edges labeled 3 appear in dataset
            if not np.any(self.datasets[self.selectedDataset].edgeData[self.scanNumber] > 1):
                return np.nan # No thickness if less than 2 edges detected
            if self.datasets[self.selectedDataset].edgeData[self.scanNumber].any():
                readVectorY = np.arange(self.datasets[self.selectedDataset].edgeData[self.scanNumber].shape[0])
                readVectorX = np.arange(self.datasets[self.selectedDataset].edgeData[self.scanNumber].shape[1])
                edge1 = np.where(self.datasets[self.selectedDataset].edgeData[self.scanNumber]==1, 1, 0)
                edge2 = np.where(self.datasets[self.selectedDataset].edgeData[self.scanNumber]==2, 1, 0)
                n1 = np.sum(edge1)
                n2 = np.sum(edge2)
                if np.abs(n1 - n2) > 10:
                    return(np.nan)
                x1 = np.sum(np.dot(edge1, readVectorX))/n1
                y1 = np.sum(np.dot(np.transpose(edge1), readVectorY))/n1
                x2 = np.sum(np.dot(edge2, readVectorX))/n2
                y2 = np.sum(np.dot(np.transpose(edge2), readVectorY))/n2
                print( np.abs( x2 - x1 ))
                #print( np.abs( y2 - y1 ))
                self.plotWindow(0)
                return(np.abs( x2 - x1 )) #thickness as the distance of the centers of mass
            else:
                return(np.nan)
        def calculateMean(self):
            tempData = self.datasets[self.selectedDataset].data[self.scanNumber][int(self.fullPlot.fullRoi.pos()[0]):int(self.fullPlot.fullRoi.pos()[0])+int(self.fullPlot.fullRoi.size()[0]), int(self.fullPlot.fullRoi.pos()[1]):int(self.fullPlot.fullRoi.pos()[1])+int(self.fullPlot.fullRoi.size()[1])]
            self.datasets[self.selectedDataset].means[self.scanNumber] = np.mean(tempData)/10

        def calculateAllThicknesses(self):
            currentViewNumber = self.scanNumber
            if not self.datasets[self.selectedDataset].setLoaded:
                self.datasets[self.selectedDataset].readSet()
            self.findAllEdges()
            for index, image in enumerate(self.datasets[self.selectedDataset].data):
                self.scanNumber = index
                if image.any():
                    self.datasets[self.selectedDataset].thicknesses[self.scanNumber] = self.calculateThickness()
                else:
                    print('image not found, loading and calc...')
                    self.datasets[self.selectedDataset].readSingle(self.scanNumber)
                    self.findCurrentEdges()
                    self.datasets[self.selectedDataset].thicknesses[self.scanNumber] = self.calculateThickness()
                    #print("thickness" + str(self.scanNumber) + ": " + str(thickness))
            self.updateResultPlot()
            self.scanNumber = currentViewNumber
        def calculateAllMeans(self):
            returnToNumber = self.scanNumber
            for index, image in enumerate(self.datasets[self.selectedDataset].data):
                self.scanNumber = index
                self.calculateMean()
            #print('Calculated all means, current mean is: ', self.datasets[self.selectedDataset].means)
            self.scanNumber = returnToNumber
        def saveThicknessesCallback(self):
            outputFile = os.path.join(self.datasets[0].rootFolder, '../thicknesses.dat')
            outputFileHandle = 0
            if os.path.exists(outputFile):
                os.remove(outputFile)
            outputFileHandle = open(os.path.join(self.datasets[0].rootFolder, '../thicknesses.dat'), 'w')
            print(os.path.join(self.datasets[0].rootFolder, '../thicknesses.dat'))
            for dataset in self.datasets:
                outputFileHandle.write(' '.join(['{:.05f}'.format(thickness) for thickness in dataset.thicknesses]))
                outputFileHandle.write(' ')
                outputFileHandle.write('_'.join([str(dataset.MID), dataset.norm, str(dataset.acc), str(dataset.accCsm), str(dataset.lam), str(dataset.nImages), str(dataset.spokesPerImage)]))
                outputFileHandle.write('\n')
        def updateResultPlot(self):
            plotNumbers = []
            plotNumbersMeans = []
            plotThicknesses =[]
            plotMeans = []
            timestep = 1
            if self.datasets[self.selectedDataset].header:
                TR = self.datasets[self.selectedDataset].header.MeasYaps['alTR', '0']
                timestep = self.datasets[self.selectedDataset].nScans * TR / self.datasets[self.selectedDataset].nImages/1000/1000 # in sec
            for scanNumber, thickness in enumerate(self.datasets[self.selectedDataset].thicknesses):
                if not np.isnan(self.datasets[self.selectedDataset].thicknesses[scanNumber]):
                    #set_trace()
                    plotNumbers.append(scanNumber * timestep ) # in ms
                    plotThicknesses.append(thickness * self.datasets[self.selectedDataset].pixelSize) #REMOVED FOR MEAN PLOT - REINSERT AFTER
                plotNumbersMeans.append(scanNumber * timestep )
                plotMeans.append(self.datasets[self.selectedDataset].means[scanNumber])
                    #self.datasets[self.selectedDataset].thicknesses
            self.resultPlot.clear()
            self.resultPlot.plot(plotNumbers, plotThicknesses)
            #self.resultPlot.plot(plotNumbersMeans, plotMeans)
        def copyRoiCallback(self):
            self.roiClipboard = self.fullPlot.fullRoi.saveState()
        def pasteRoiCallback(self):
            self.fullPlot.fullRoi.setState(self.roiClipboard)
        def pasteRoiToAll(self):
            for dataset in  self.datasets:
                dataset.roi = self.roiClipboard
        def saveRoiCallback(self):
            saveString = os.path.join(self.datasets[self.selectedDataset].rootFolder, 'roi.pickle')
            with open(saveString, 'wb') as roiFile:
                pickle.dump(self.datasets[self.selectedDataset].roi, roiFile)
            print( 'ROI saved as: ' + saveString)
        def saveAllRoisCallback(self):
            for dataset in self.datasets:
                saveString = os.path.join(dataset.rootFolder, 'roi.pickle')
                with open(saveString, 'wb') as roiFile:
                    pickle.dump(self.datasets[self.selectedDataset].roi, roiFile)
                print( 'ROI saved as: ' + saveString)
        def deleteRoiCallback(self):
            self.fullPlot.fullRoi.setState(self.roiClipboard)
            roiString = os.path.join(self.datasets[self.selectedDataset].rootFolder, 'roi.pickle')
            with open(saveString, 'wb') as roiFile:
                pickle.dump(self.datasets[self.selectedDataset].roi, roiFile)
            print( 'ROI saved as: ' + saveString)
        def closeCallback(self):
                self.top.destroy()
