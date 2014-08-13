'''    
Created on Apr 18, 2014
@author: Ben Petroski
'''
import os,sys,time,math,hashlib,urllib,cStringIO,fileinput,collections
from operator import itemgetter
from PIL import Image
from scipy.misc import imread
from scipy.linalg import norm
from scipy import sum, average

def main():
    start_time = time.time()
    count=0
    with open('Image_http.txt') as f: #_test, _test1
        url = f.readlines()
    
    #quadrantMaster(url)
    
    fail=0  
    fileCount=0
    matchCount=0     
    file = []
    fileNum = []
    sameFilename = []
    matchingPics = [[]]    
    for i in range(0,len(url)):
        try:
            fileCount+=1
            file.append(to_grayscale(imread(cStringIO.StringIO(urllib.urlopen(url[i]).read())).astype(float)))
            fileNum.append(i+1)
        except IOError as e:
            fail+=1         
    badCount=0
    compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
    for i in range(0,len(url)-fail):
        for j in range(i+1,len(url)-fail): #i+1 or 0           
            if j != i:
                try:
                    n_m, n_0 = compare_images(file[i], file[j])
                    #if n_m/file[i].size < 100: print "(%d,%d): %f" % (fileNum[i], fileNum[j], n_m/file[i].size) # Manhattan Norm
                    if n_m/file[i].size == 0.0: 
                        if not sameFilename:
                            sameFilename.append(fileNum[i])
                            sameFilename.append(fileNum[j])
                        if fileNum[i] not in sameFilename:
                            sameFilename.append(fileNum[i])
                            sameFilename.append(fileNum[j])
                        if fileNum[i] in sameFilename and fileNum[j] not in sameFilename:
                            sameFilename.append(fileNum[j])
                    if n_m/file[i].size < 45: #range from 40-55 = Manhattan Norm
                        #print "(%d,%d): %d" % (fileNum[i], fileNum[j]), n_m/file[i].size  
                        for sublist in matchingPics:
                            if not sublist:
                                sublist.append(fileNum[i])
                                sublist.append(fileNum[j])
                                matchCount+=1 
                                break
                            if fileNum[i] not in sublist:
                                if compare(sublist, matchingPics[len(matchingPics)-1]):
                                    matchingPics.append([])
                                    matchingPics[len(matchingPics)-1].append(fileNum[i])
                                    matchingPics[len(matchingPics)-1].append(fileNum[j])
                                    matchCount+=1 
                            if fileNum[i] in sublist and fileNum[j] not in sublist:
                                sublist.append(fileNum[j])  
                                matchCount+=1          
                            elif fileNum[i] in sublist:
                                break
                except IOError as e:
                    badCount+=1   
    print "Total Files: ", fileCount
    print '\n-------------------------------------------------------' 
    print "Manhattan Norm = 0, Potentially Same Filename (%d files):" % (len(sameFilename))
    print sameFilename
    print '\n-------------------------------------------------------' 
    print "Matching Lists (%d sublists/%d files):" % (len(matchingPics), matchCount)
    pos=0
    squareProfilePic = 48
    mosaicGrid = int(math.ceil(math.sqrt(matchCount))) + 1
    mosaicSize = mosaicGrid * squareProfilePic
    mosaic = Image.new('RGB',(mosaicSize,mosaicSize))
    whiteSquare = Image.new("RGB", (squareProfilePic, squareProfilePic), '#000000')
    for sublist in matchingPics:
        for i in sublist:
            try:
                file = cStringIO.StringIO(urllib.urlopen(url[i-1]).read())
                im = Image.open(file)
                mosaic.paste(im, ((pos%mosaicGrid)*squareProfilePic, (pos/mosaicGrid)*squareProfilePic))
                pos+=1
            except IOError as e:
                badCount+=1  
        mosaic.paste(whiteSquare, ((pos%mosaicGrid)*squareProfilePic, (pos/mosaicGrid)*squareProfilePic))
        pos+=1
        print sublist    
    print '\n-------------------------------------------------------'
    mosaicFilename = 'mosaic.bmp'
    print 'Mosaic Generated ("%s")' % (mosaicFilename)
    mosaic.save(mosaicFilename)
    print '\n-------------------------------------------------------'
    print time.time() - start_time, 'seconds'    
    
def quadrantMaster(url): #To calculate average color in grid fashion, not used in this program   
    quadrantList = []
    decList = []
    goodFiles = []
    badFiles = []
    for u in range(0, len(url)):
        file = cStringIO.StringIO(urllib.urlopen(url[u]).read())    
            
        try:
            jpg = Image.open(file)
            rgb_jpg = jpg.convert('RGB')
            goodFiles.append([u+1, url[u]])
            rL1Total=0;rM1Total=0;rR1Total=0;rL2Total=0;rM2Total=0;rR2Total=0;rL3Total=0;rM3Total=0;rR3Total=0;
            gL1Total=0;gM1Total=0;gR1Total=0;gL2Total=0;gM2Total=0;gR2Total=0;gL3Total=0;gM3Total=0;gR3Total=0;
            bL1Total=0;bM1Total=0;bR1Total=0;bL2Total=0;bM2Total=0;bR2Total=0;bL3Total=0;bM3Total=0;bR3Total=0;
            
            step=2
            pxlCnt = jpg.size[0]*jpg.size[1];
            for i in range(0, jpg.size[0], step):
                for j in range(0, jpg.size[1], step):
                    r, g, b = rgb_jpg.getpixel((i, j))
                    if i>=0 and i<jpg.size[0]/3 and j>=0 and j<jpg.size[1]/3:
                        rL1Total += r
                        gL1Total += g
                        bL1Total += b
                    elif i>=0 and i<jpg.size[0]/3 and j>=jpg.size[1]/3 and j<=2*jpg.size[1]/3:
                        rL2Total += r
                        gL2Total += g
                        bL2Total += b
                    elif i>=0 and i<jpg.size[0]/3 and j>2*jpg.size[1]/3 and j<=jpg.size[1]:
                        rL3Total += r
                        gL3Total += g
                        bL3Total += b
                    elif i>=jpg.size[0]/3 and i<=2*jpg.size[0]/3 and j>=0 and j<jpg.size[1]/3:
                        rM1Total += r
                        gM1Total += g
                        bM1Total += b
                    elif i>=jpg.size[0]/3 and i<=2*jpg.size[0]/3 and j>=jpg.size[1]/3 and j<=2*jpg.size[1]/3:
                        rM2Total += r
                        gM2Total += g
                        bM2Total += b
                    elif i>=jpg.size[0]/3 and i<=2*jpg.size[0]/3 and j>2*jpg.size[1]/3 and j<=jpg.size[1]:
                        rM3Total += r
                        gM3Total += g
                        bM3Total += b
                    elif i>2*jpg.size[0]/3 and i<=jpg.size[0] and j>=0 and j<jpg.size[1]/3:
                        rR1Total += r
                        gR1Total += g
                        bR1Total += b  
                    elif i>2*jpg.size[0]/3 and i<=jpg.size[0] and j>=jpg.size[1]/3 and j<=2*jpg.size[1]/3:
                        rR2Total += r
                        gR2Total += g
                        bR2Total += b
                    elif i>2*jpg.size[0]/3 and i<=jpg.size[0] and j>2*jpg.size[1]/3 and j<=jpg.size[1]:
                        rR3Total += r
                        gR3Total += g
                        bR3Total += b  
            uF = '{0: >3}'.format(u)        
            L1avg = '{0: >3}'.format(step**2*(rL1Total+gL1Total+bL1Total)/(jpg.size[0]*jpg.size[1]))
            L2avg = '{0: >3}'.format(step**2*(rL2Total+gL2Total+bL2Total)/(jpg.size[0]*jpg.size[1]))
            L3avg = '{0: >3}'.format(step**2*(rL3Total+gL3Total+bL3Total)/(jpg.size[0]*jpg.size[1]))
            M1avg = '{0: >3}'.format(step**2*(rM1Total+gM1Total+bM1Total)/(jpg.size[0]*jpg.size[1]))
            M2avg = '{0: >3}'.format(step**2*(rM2Total+gM2Total+bM2Total)/(jpg.size[0]*jpg.size[1]))
            M3avg = '{0: >3}'.format(step**2*(rM3Total+gM3Total+bM3Total)/(jpg.size[0]*jpg.size[1]))
            R1avg = '{0: >3}'.format(step**2*(rR1Total+gR1Total+bR1Total)/(jpg.size[0]*jpg.size[1]))
            R2avg = '{0: >3}'.format(step**2*(rR2Total+gR2Total+bR2Total)/(jpg.size[0]*jpg.size[1]))
            R3avg = '{0: >3}'.format(step**2*(rR3Total+gR3Total+bR3Total)/(jpg.size[0]*jpg.size[1]))        
            quadrantList.append([L1avg,L2avg,L3avg,M1avg,M2avg,M3avg,R1avg,R2avg,R3avg, uF])        
            redavg='{0: >3}'.format(step**2*(rL1Total+rM1Total+rR1Total+rL2Total+rM2Total+rR2Total+rL3Total+rM3Total+rR3Total)/pxlCnt)
            grnavg='{0: >3}'.format(step**2*(gL1Total+gM1Total+gR1Total+gL2Total+gM2Total+gR2Total+gL3Total+gM3Total+gR3Total)/pxlCnt)
            bluavg='{0: >3}'.format(step**2*(bL1Total+bM1Total+bR1Total+bL2Total+bM2Total+bR2Total+bL3Total+bM3Total+bR3Total)/pxlCnt)
            decList.append([redavg,grnavg,bluavg, uF])
        
    #         print quadrantList, '\n', decList, '\n', ' Left Averages:', L1avg, '\t', L2avg, '\t', L3avg, '\n', '  Mid Averages:', M1avg, '\t', M2avg, '\t', M3avg, '\n', 'Right Averages:', R1avg, '\t', R2avg, '\t', R3avg, '\n', 'Dec Color Averages:', redavg, grnavg, bluavg, '\n', time.time() - start_time, 'seconds\n'   
        except IOError as e:
            badFiles.append([u+1, url[u]])
    
    count=0        
    quadrantList.sort(key=itemgetter(0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    for i in range(0, len(quadrantList)):
        count+=1
        print 'Quad(%03d): [%s]' % (count, ', '.join(map(str, quadrantList[i])))
    print '\n---------------------------------------------------\n'
    count=0
    decList.sort(key=itemgetter(0, 1, 2, 3))
    for i in range(0, len(decList)):
        count+=1
        print 'Dec(%03d): [%s]' % (count, ', '.join(map(str, decList[i])))
        
    print '\nBadfiles(%d):' % (len(badFiles))
    for i in badFiles:
        print i
    print '\n---------------------------------------------------\n'  
    
def compare_images(img1, img2):
    img1 = normalize(img1)
    img2 = normalize(img2)
    try:
        diff = img1 - img2
        m_norm = sum(abs(diff))  # Manhattan norm
        z_norm = norm(diff.ravel(), 0)  # Zero norm
        return (m_norm, z_norm)
    except ValueError as e:
        diff = 100
        return (250000.0, 2000.0)
    
def to_grayscale(arr):
    "If arr is a color image (3D array), convert it to grayscale (2D array)."
    if len(arr.shape) == 3:
        return average(arr, -1)
    else:
        return arr
 
def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng
    
if __name__ == "__main__":
    main()