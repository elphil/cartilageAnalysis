import os
import numpy as np
import math
import cmath
import pdb
import cv2
import matplotlib.pyplot as plt
import pyqtgraph as pg
import pickle
from customDebug import set_trace
#from scipy.optimize import curve_fit
from PIL import Image
class data:
        def __init__(self, path):
                #self.imagesFound = 0
                self.imagesets = 0
                self.nScans = 0
                self.images = 0
                self.loaded = []
                self.fullPath = path
                self.rootFolder = path
                self.imageFiles = []
                self.maxResolution = 512
                self.setLoaded = 0

                #self.data = np.array([])
                self.data = []
                self.edgeData = []
                self.thicknesses = []
                self.roi= pg.ROI([200,200],[100,100]).saveState()

                self.timePoints = []
                self.samples = 0
                self.samplingRate = 0
                #self.fitParameters = np.array([])
                #self.summedFitParameters = np.array([])
                #self.phase = np.array([]) #-2*cmath.pi
                #self.summedPhase = 0
                #self.function = 0
                #self.numberOfParameters = np.array((3,3))
        def readSingle(self, scanNumber):
            self.data[scanNumber] = cv2.imread(os.path.join(self.rootFolder, 'images', self.imageFiles[scanNumber]))
            self.edgeData[scanNumber] = np.zeros(self.data[scanNumber].shape)
            self.thicknesses[scanNumber] = 0
            self.loaded[scanNumber] = 1
        def readSet(self):
            for scanNumber, image in enumerate(self.data):
                if not image.any():
                    self.readSingle(scanNumber)
                    self.edgeData[scanNumber] = np.zeros(self.data[scanNumber].shape)
                    self.thicknesses[scanNumber] = 0
                    self.loaded[scanNumber] = 1
            self.setLoaded = 1
        def initialize(self):
            saveString = os.path.join(self.rootFolder, 'roi.pickle')
            if os.path.exists(saveString):
                with open(saveString, 'rb') as roiFile:
                    print('loading roi from disk')
                    self.roi = pickle.load(roiFile)
            self.data = ([np.zeros((1,1,3))] * len(self.imageFiles))
            self.edgeData = ([np.zeros(1)] * len(self.imageFiles))
            self.thicknesses = ([np.nan] * len(self.imageFiles))
            self.loaded = ([0] * len(self.imageFiles))

            #for scanNumber in np.arange(len(self.data)):
            #    self.data[scanNumber] = cv2.imread(os.path.join(self.rootFolder, 'images', self.imageFiles[scanNumber]))
            #    self.edgeData[scanNumber] = np.zeros(self.data[scanNumber].shape)
            #    self.thicknesses[scanNumber] = 0
                #self.data = np.array([self.nImagesets])

                ##Read rois from file if exists


                #create subimages - possibly better to not store!!!!
                #for currentset in [1:nImageSets]:
                #    if self.rois[currentSet]:
                #        self.subData[currentSet] = self.data[currentSet][:][[subImageRoi[1]:subImageRoi[1]+subImageRoi[3],subImageRoi[0]:subImageRoi[0]+subImageRoi[2]]]
                #    else:
                #        self.subData[currentSet] = self.data[currentSet]

                #else:
                #        filename, fileExtension = os.path.splitext(self.fullPath)
                #        if  ".png" in fileExtension:
                #                dataType = 1
                #        else:
                #                print('No files in png format found, please override to a different format or select folder containing png files')
                #if dataType == 1:
                #        tempData = matFile.read(self.fullPath)
                #        self.timePoints = tempData[0,:]
                #        self.data = tempData[1:tempData[:,0].size]
                #        self.samples, self.samplingRate, self.nScans = matFile.readParameters(filename+'parameter.mat')
                #elif dataType == 2:
                #        self.data = datFile(self.fullPath)
                #else:
                #        print("Please choose valid override parameter:\n 1: .mat file\n 2: .dat file")
                #self.timepoints = np.linspace(0,False, self.samples)
                #self.phase = np.zeros(self.data[:,0].size)
                #self.fitParameters = np.zeros((self.nScans, self.numberOfParameters[self.function]))
                #self.summedFitParameters = np.zeros((1,self.numberOfParameters[self.function]))
#        def fit(self, startFrequency, stopFrequency, scanNumber, function = 0, summed = 0) :
#                startIndex = 0
#                while self.frequencies[startIndex] < startFrequency:
#                        startIndex = startIndex + 1
#                stopIndex = startIndex
#                while self.frequencies[stopIndex] < stopFrequency:
#                        stopIndex = stopIndex + 1
#                if function == 0:
#                        #def func(x, width, height, center):
#                        #       return height / (np.pi * (x - center)**2/width + (width))
#                        def func(x, *parameters):
#                                #parameters[0] is width
#                                #parameters[1] is frequency
#                                #parameters[0] is width
#                                return parameters[0] / (np.pi * ((x - parameters[1])**2/parameters[2] + (parameters[2])))
#                elif function == 1:
#                        def func(x, a, b, c):
#                                return a * np.exp(-b * x) + c
#                else:
#                        print ('Please choose valid function: \n 0: lorentian\n 1: exponential')
#                parameterBounds = ([-np.inf, startFrequency, -np.inf], [np.inf, stopFrequency, np.inf])
#                if summed == 0:
#                        return func, curve_fit(func,
#                                self.frequencies[startIndex:stopIndex], np.real(cmath.exp(1j*self.phase[scanNumber]) * self.fftData[scanNumber, -self.frequencies.size+startIndex:-self.frequencies.size+stopIndex]), self.fitParameters[scanNumber], maxfev = 2000, bounds=parameterBounds)
#                elif summed == 1:
#                        #pdb.set_trace()
#                        return  func, curve_fit(func, self.frequencies[startIndex:stopIndex], np.real(cmath.exp(1j*self.summedPhase) * self.summedFftData[-self.frequencies.size+startIndex:-self.frequencies.size+stopIndex]), self.summedFitParameters, maxfev = 2000, bounds=parameterBounds)
        def readParameters(self):
                parameterFilePath = os.path.splitext(self.fullPath)[0] + 'FitParameters.dat'
                if os.path.exists(parameterFilePath) and os.path.getsize(parameterFilePath)>0:
                        with open(parameterFilePath) as fullFile:
                                lineNumber = 0
                                readList  = list((float(number) for number in fullFile.readline().strip().split()))
                                self.summedFitParameters = readList[0:len(readList) - 1]
                                self.summedPhase = readList[len(readList) - 1]
                                for line in fullFile:
                                        readList  = list((float(number) for number in line.strip().split()))
                                        self.fitParameters[lineNumber] = readList[0:len(readList) - 1]
                                        self.phase[lineNumber] = readList[len(readList) -1]
                                        lineNumber += 1 
                                print("Read parameters from file.")
                                print(self.phase)

        def saveParameters(self):
                noExtensionPath = os.path.splitext(self.fullPath)
                parameterFile = open(str(noExtensionPath[0]) + 'FitParameters.dat', 'w+')
                if np.any(self.summedFitParameters):
                        parameterFile.write(str(self.summedFitParameters).lstrip('[').rstrip(']') + '\t')
                        parameterFile.write(str(self.summedPhase))
                        parameterFile.write(str('\n'))
                else:
                        for column in range(0, self.fitParameters.shape[1]):
                                #parameterFile.write('\t'.join("") + '\n')
                                parameterFile.write("0\t")
                        parameterFile.write(str(self.summedPhase))
                        parameterFile.write(str('\n'))
                if self.fitParameters.any:
                        for row in range(0,self.fitParameters.shape[0]):
                                for column in range (0,self.fitParameters.shape[1]):
                                        parameterFile.write(str(self.fitParameters[row][column]) + "\t")
                                parameterFile.write(str(self.phase[row]))
                                parameterFile.write(str('\n'))
                else:
                        for row in range(0,self.fitParameters.shape[0]):
                                for column in range (0,self.fitParameters.shape[1]):
                                        parameterFile.write(str(self.fitParameters[row][column]) + "\t")
                                parameterFile.write(str(self.phase[row]))
                                parameterFile.write(str('\n'))
