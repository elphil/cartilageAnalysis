import numpy as np
import subprocess
import os
import sys
import pdb
import matplotlib.pyplot as plt
import guiQt
from matplotlib import cm
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d import Axes3D
import cv2
window = guiQt.mainWindow()

#image = cv2.imread('JK_radial_incLoopCoil/MID308_CGSENSEl2/images/orig-img-010.png')
#subImageRoi = cv2.selectROI(image)
#subImage = image[subImageRoi[1]:subImageRoi[1]+subImageRoi[3],subImageRoi[0]:subImageRoi[0]+subImageRoi[2]]
#image = subImage
#labelImage = image
#edges = cv2.Canny(image, 100, 200)
#nEdges, labelImage = cv2.connectedComponents(edges)
#print(nEdges, 'edges found')
#plt.imshow(labelImage)
#plt.imshow(subImage)
#plt.show()

'''
def extractData(content):
    lines = content.split('\n')
    nPoints = len(lines) -2 #first line is column title, last is ended with \n
    nFrames = len(lines[0].split('\t'))-1 #first column is line number
    sliceProfiles = np.zeros((nFrames-1, nPoints))
    for line in range(1,nPoints+1):
        lineList = lines[line].split('\t')[1:nFrames]
        sliceProfiles[:,line-1] = np.array(lineList)
    return sliceProfiles, nFrames, nPoints

def plotData(sliceProfiles, nFrames, nPoints, savepath):
    fig = plt.figure('2d Profiles')
    axis = fig.gca(projection='3d')
    x = np.arange(0,nFrames-1)
    y = np.arange(0,nPoints)
    [xs, ys] = np.meshgrid(y,x)
    #plot all slice profiles as a 3d stack
    #for frame in range(nFrames-2,1,-1):
    #    axis.plot(xs[frame,:], ys[frame,:], sliceProfiles[frame,:], color = [(2*frame%(nFrames-1))/(nFrames-1), 0.5,frame/(nFrames-1)], linewidth = ys[-1, -1]/ys.shape[1]*4)
    #plt.show()
    distances= np.zeros(nFrames-1)
    lowerBounds= np.zeros(nFrames-1)
    upperBounds= np.zeros(nFrames-1)
    print('nFrames: ', nFrames)
    for frame in range(1,nFrames-1):
        frameMax = np.max(sliceProfiles[frame,:])
        frameMin = np.min(sliceProfiles[frame,:])
        frameMaxIndex = np.argmax(sliceProfiles[frame,:])
        #print('index maximum: ', frameMaxIndex)
        lowerBoundIndex = frameMaxIndex;
        upperBoundIndex = frameMaxIndex;
        threshold = (frameMax - frameMin)*0.5
        while (sliceProfiles[frame,lowerBoundIndex] >= threshold and lowerBoundIndex > 0):
            lowerBoundIndex-=1
        while (sliceProfiles[frame,upperBoundIndex] >= threshold and upperBoundIndex < frameMaxIndex):
            upperBoundIndex+=1
        print('pixel distance: ', upperBoundIndex-lowerBoundIndex, '; lower: ', lowerBoundIndex, '; upper: ', upperBoundIndex)#adapt slopes if resolution is available!!!!!! currently, deltaX is always 1
        lowerSlope = (sliceProfiles[frame,lowerBoundIndex + 1] - sliceProfiles[frame,lowerBoundIndex])/(1)
        upperSlope = (sliceProfiles[frame,upperBoundIndex] - sliceProfiles[frame,upperBoundIndex - 1])/(1)
        lowerBounds[frame] = lowerBoundIndex + (threshold - sliceProfiles[frame,lowerBoundIndex])/lowerSlope
        upperBounds[frame] = upperBoundIndex + (threshold - sliceProfiles[frame,upperBoundIndex])/upperSlope
        distances[frame] = upperBounds[frame] - lowerBounds[frame]
    fig2 = plt.figure('distances')
    plt.plot(x, lowerBounds, upperBounds, color = 'r')
    plt.plot(x, distances, color='g' )
    #plt.plot(x,np.average((lowerBounds[1:nFrames-1]+upperBounds[1:nFrames-1])/2)+(upperBounds-lowerBounds)/2, color = 'g' )
    #plt.plot(x,np.average((lowerBounds[1:nFrames-1]+upperBounds[1:nFrames-1])/2)-(upperBounds-lowerBounds)/2, color = 'g')
    #plt.plot(x,np.ones(nFrames-1) * np.average((lowerBounds[1:nFrames-1]+upperBounds[1:nFrames-1])/2), color =  'b' )
    plt.ylim((0,26))
    print("File saved as " + os.path.join(os.path.abspath(savepath),"distances.png"))
    plt.savefig(os.path.join(os.path.abspath(savepath),"distances.png"))
    np.savetxt(os.path.join(os.path.abspath(savepath),"distances.txt"), distances)
    plt.close()
    #plt.show()
#f = open("./MID72_CGSENSEl2_4_4/stackProfiles.txt", 'r')
#f = open("./MID72_CGSENSEl2_8_8/stackProfiles.txt", 'r')
####################
####################main
####################
walkDir = "./"
nLines = 1
if len(sys.argv)-1:
    walkDir = sys.argv[1]
for root, folders, files in os.walk(walkDir):
    if ("images" in folders):
        print("root: ", root)
        imagePath = os.path.join(os.path.abspath(root), "images/orig-img-01.jpg")
        roiString = ''
        roiFound = 0
        for currFile in os.listdir(os.path.abspath(root)):
            if(currFile.endswith(".roi") and roiFound == 0):
                roiString = currFile
                print('using ROI ', roiString)
                roiFound = 1
                break
        if roiFound == 0:
            roiString = "183 234 25 6"
        masub = subprocess.call(["/usr/local/ImageJ/ImageJ", "-macro", "/home/philipp/.imagej/macros/getProfileAuto.ijm",  imagePath + " " + str(nLines) + " " + os.path.join(root, roiString)])
        #pdb.set_trace()
        for currentFile in os.listdir(os.path.abspath(root)):
            if "stackProfileLine" in currentFile:
                print("evaluating ", os.path.join(os.path.abspath(root), currentFile))
                content = readFile(os.path.join(os.path.abspath(root), currentFile))
                [sliceProfiles, nFrames, nPoints] = extractData(content)
                plotData(sliceProfiles, nFrames, nPoints, os.path.abspath(root) )
            #print("/usr/local/ImageJ/ImageJ", "-macro", "/home/philipp/.imagej/macros/getProfileAuto.ijm",  imagePath +                 " " + str(nLines) + " " + os.path.abspath(roiString))
            #sub = subprocess.call(["/usr/local/Fiji.app/ImageJ-linux64", "-macro", "/home/philipp/.imagej/macros/getProfile.txt",  imagePath])
'''
'''
for root, folders, files in os.walk(walkDir):
    if os.path.isfile(os.path.join(os.path.abspath(root), "stackProfileLine*.txt")):
        print(os.path.join(os.path.abspath(root), "stackProfiles.txt"))
        content = readFile(os.path.join(os.path.abspath(root), "stackProfiles.txt"))
        #plotData(sliceProfiles, nFrames, nPoints, os.path.join(os.path.abspath(root), folder))
'''
