import os 
import numpy as np
import math
import cmath
import pdb
import cv2
import matplotlib.pyplot as plt
import pyqtgraph as pg
import pickle
import mapvbvd
from customDebug import set_trace
#from scipy.optimize import curve_fit
from PIL import Image
class data:
        def __init__(self, path):
            self.imagesets = 0
            self.nScans = 0
            self.images = 0
            self.loaded = []
            self.fullPath = path
            self.rootFolder = path
            self.imageFiles = []
            self.maxResolution = 512
            self.pixelSize = 1
            self.setLoaded = 0

            self.data = []
            self.edgeData = []
            self.thicknesses = []
            self.means = []
            self.roi= pg.ROI([200,200],[100,100]).saveState()

            self.timePoints = []
            self.samples = 0
            self.samplingRate = 0
            
            self.header = 0
            self.MID = 0
            self.norm = ''
            self.acc = 1
            self.accCsm = 1
            self.lam = 0
            self.nImages = 0
            self.spokesPerImage = 0
            self.findRecoParameters()
        def findRecoParameters(self):
            for element in os.path.basename(self.rootFolder).split('_'):
                if element.startswith('MID'):
                    self.MID = int(element[3:])
                if element.startswith('CGSENSE'):
                    self.norm = element[7:]
                if element.startswith('acc\d'):#acc then digit regexp (\d)
                    self.acc = int(element[3:])
                if element.startswith('accCsm'):
                    self.accCsm = int(element[6:])
                if element.startswith('lambda'):
                    self.lam = float(element[6:])
                if element.startswith('nImages'):
                    self.nImages = int(element[7:])
                if element.startswith('spokesPerImage'):
                    self.spokesPerImage = int(element[14:])
        def readSingle(self, scanNumber):
            self.data[scanNumber] = cv2.imread(os.path.join(self.rootFolder, 'images', self.imageFiles[scanNumber]), cv2.IMREAD_GRAYSCALE)
            #print(self.data[scanNumber].shape)
            self.edgeData[scanNumber] = np.zeros(self.data[scanNumber].shape)
            #set_trace()
            self.thicknesses[scanNumber] = np.nan
            self.means[scanNumber] = np.nan
            self.loaded[scanNumber] = 1
        def readSet(self):
            for scanNumber, image in enumerate(self.data):
                if not image.any():
                    self.readSingle(scanNumber)
            resFiles = [resFile for resFile in os.listdir(self.rootFolder) if resFile[0:4]=='res_' and resFile[-4:]=='.txt']
            rawDataFile = ''
            if resFiles:
                f = open(os.path.join(self.rootFolder, resFiles[0]), 'r')
                for line in f.readlines():
                    if line.startswith("Source File"):
                        rawDataFile = line.rstrip()[12:]
            print(rawDataFile)
            twixObject = mapvbvd.mapVBVD(rawDataFile)[-1]
            self.nScans = twixObject.image.NLin * twixObject.image.NRep
            self.pixelSize = twixObject.hdr.MeasYaps['sAdjData', 'sAdjVolume', 'dPhaseFOV']/ twixObject.hdr.MeasYaps['sKSpace','lBaseResolution']
            self.header = twixObject.hdr
            self.setLoaded = 1
        def initialize(self):
            saveString = os.path.join(self.rootFolder, 'roi.pickle')
            if os.path.exists(saveString):
                with open(saveString, 'rb') as roiFile:
                    print('loading roi from disk')
                    self.roi = pickle.load(roiFile)
            self.nImages = len(self.imageFiles)
            self.data = ([np.zeros((1,1))] * self.nImages)
            self.edgeData = ([np.zeros(1)] * self.nImages)
            self.thicknesses = ([np.nan] * self.nImages)
            self.means = ([np.nan] * self.nImages)
            self.loaded = ([0] * self.nImages)

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
