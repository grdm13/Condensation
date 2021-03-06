import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import time
import os

################### I N F O ###################
# works perfect
# new logic to find droplets
#####################################################


################### start the clock ###################
start_time = time.time()

################### function read names from file ###################
def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles

################### give the folders with the pictures ###################
#initial
dirName = '/Users/georgedamoulakis/PycharmProjects/Condensation/1_Script/9_Complete_Procedure_for_MatrixA/Initial';
listOfFiles = getListOfFiles(dirName)
#after Gamma
dirName2 = '/Users/georgedamoulakis/PycharmProjects/Condensation/1_Script/9_Complete_Procedure_for_MatrixA/afterGamma';
listOfFiles2 = getListOfFiles(dirName2)

for i in range(len(listOfFiles)):
    im_initial = cv2.imread(listOfFiles[i], cv2.IMREAD_GRAYSCALE);
    im_in = cv2.imread(listOfFiles2[i], cv2.IMREAD_GRAYSCALE);

    def create_Matrix(im_initial, im_in):
        h, w = im_initial.shape[:2]
        white = np.zeros([h + 300, w + 300, 3], dtype=np.uint8)
        white.fill(255)
        # or img[:] = 255
        cv2.imshow('3 Channel Window', white)
        for i in range(1, h, 1):
            for j in range(1, w, 1):
                white[i + 150, j + 150] = im_initial[i, j]
        im_in1 = white

        h, w = im_in.shape[:2]
        white = np.zeros([h + 300, w + 300, 3], dtype=np.uint8)
        white.fill(255)
        cv2.imshow('3 Channel Window', white)
        for i in range(1, h, 1):
            for j in range(1, w, 1):
                white[i + 150, j + 150] = im_in[i, j]

        # Read image
        im_in = white
        im_in = cv2.cvtColor(im_in, cv2.COLOR_BGR2GRAY)

        def CountingCC(im_in):
            ################### thresh ##################
            th, im_th = cv2.threshold(im_in, 50, 150, cv2.THRESH_BINARY_INV);

            ################### define CC function ##################
            def CC(img):
                nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(img)
                label_hue = np.uint8(179 * labels / np.max(labels))
                blank_ch = 255 * np.ones_like(label_hue)
                labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
                labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
                labeled_img[label_hue == 0] = 0
                return labeled_img, nlabels, labels, stats, centroids

            # fixing the image
            # this is the second part of the image process
            kernel = np.ones((3, 3), np.uint8)
            erosion = cv2.erode(im_th, kernel, iterations=3)
            dilation = cv2.dilate(erosion, kernel, iterations=1)
            components, nlabels, labels, stats, centroids = CC(dilation)

            # creating the matrices
            a = np.hsplit(stats, 5)
            horizontal = a[2]
            vertical = a[3]
            area = a[4]
            b = np.hsplit(centroids, 2)
            x_centr = b[0]
            y_centr = b[1]
            NEW_dimensions = np.zeros((nlabels, 6))

            # Logic check if something is DROPLET or NOT
            d = 0
            droplet_counter = 0
            Not_Droplet = np.empty(nlabels, dtype=object)
            for i in range(nlabels):
                d = ((horizontal[i] + vertical[i]) / 2)
                p = d * 3.14  # the perimeter
                circularity = 4 * (3.14) * ((area[i]) / (p ** 2))
                #print(circularity)
                if circularity < 0.90:
                    Not_Droplet[i] = "NOT a droplet"
                else:
                    Not_Droplet[i] = "ok"
                    droplet_counter = droplet_counter + 1

            # building the new final dimensions matrix
            for row in range(nlabels):
                for column in range(8):
                    if column == 0:
                        NEW_dimensions[row, column] = (row + 1)
                    elif column == 1:
                        NEW_dimensions[row, column] = x_centr[row]
                    elif column == 2:
                        NEW_dimensions[row, column] = y_centr[row]
                    elif column == 3:
                        if horizontal[row] < 100:
                            NEW_dimensions[row, column] = horizontal[row] + 20
                        else:
                            NEW_dimensions[row, column] = horizontal[row] + 40
                    elif column == 4:
                        if vertical[row] < 100:
                            NEW_dimensions[row, column] = vertical[row] + 20
                        else:
                            NEW_dimensions[row, column] = vertical[row] + 40
                    elif column == 5:
                        NEW_dimensions[row, column] = ((NEW_dimensions[row][3]) + (
                            NEW_dimensions[row][4])) * 3.14 * 0.25 * (
                                                              (NEW_dimensions[row][3]) + (NEW_dimensions[row][4]))
                column = column + 1
            row = row + 1
            plt.show()

            # here we have to build the surface area difference
            TotalArea_Frame = 956771  # i am not sure about this number for this image - but we dont care about it now
            TotalArea_Droplets = 0
            TotalArea_Background = 0
            d3 = 0
            droplet_counter_2 = 0
            # Not_Droplet = np.empty(nlabels, dtype=object)
            for i in range(nlabels):
                d3 = ((horizontal[i] + vertical[i]) / 2)
                d4 = 0.785 * d3 * d3
                if abs(area[i] - (d4)) > 2000 or horizontal[i] < 10 or vertical[i] < 10:
                    pass
                else:
                    droplet_counter_2 = droplet_counter_2 + 1
                    TotalArea_Droplets = int(TotalArea_Droplets + (NEW_dimensions[i][5]))

            # here we draw the circles, the boxes and the numbers
            XCENTER = []
            r = []
            YCENTER = []
            image = components
            i = 0
            out = image.copy()
            for row in range(1, nlabels, 1):
                for column in range(5):
                    if Not_Droplet[row] == "ok":
                        XCENTER.append((int(x_centr[row])))
                        YCENTER.append((int(y_centr[row])))
                        X = XCENTER[i]
                        Y = YCENTER[i]
                        cv2.rectangle(out, (int(X) - 3, int(Y) - 3), (int(X) + 3, int(Y) + 3), (0, 0, 0))
                        r.append((math.sqrt(NEW_dimensions[row][5] * 0.31830988618) * 0.5))
                        P = r[i]
                        cv2.circle(out, (int(X), int(Y)), int(P), (255, 255, 0, 4))
                        cv2.putText(out, ('%d' % (row + 1)), (int(X), int(Y)), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                    (255, 255, 255),
                                    2)
                        i = i + 1
            cv2.putText(out, ('%d droplets' % droplet_counter), (5, 30), cv2.FONT_ITALIC, 1.2, (220, 220, 220), 2)

            # show the images
            #cv2.imshow("Initial", im_in)
            #cv2.imshow("Final", out)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
            return r, XCENTER, YCENTER, out, droplet_counter

        r, x_centr, y_centr, output, droplet_counter = CountingCC(im_in)
        U = int(len(r) / 5)
        R = np.zeros(U)
        X = np.zeros(U)
        Y = np.zeros(U)
        C = np.zeros(U)
        B = np.zeros(U)
        New_Cx = np.zeros(U)
        New_Cy = np.zeros(U)
        Radii = np.zeros(U)
        for i in range(0, U):
            R[i] = r[(i * 5) + 1]
            X[i] = x_centr[(i * 5) + 1]
            Y[i] = y_centr[(i * 5) + 1]
            C[i] = droplet_counter
            B[i] = 0

        for t in range(0, U):
            # the actual CircleNO is i+1
            CircleNO = t
            if int(R[CircleNO]) < 10:
                RR = int(R[CircleNO]) + 10
            elif int(R[CircleNO]) < 70 & int(R[CircleNO]) > 10:
                RR = int(R[CircleNO]) + 20
            else:
                RR = int(R[CircleNO]) + 30
            x = int(X[CircleNO])
            y = int(Y[CircleNO])

            crop_img = im_in1[y - RR:y + RR, x - RR:x + RR]
            # cv2.imwrite("circleNO {0}.png".format(i),crop_img)

            # Hough Circle Detection

            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            Blured = cv2.GaussianBlur(crop_img, (1, 1), 0)

            cimg = cv2.cvtColor(crop_img, cv2.COLOR_GRAY2BGR)

            circles = cv2.HoughCircles(Blured, cv2.HOUGH_GRADIENT, 1, 800,
                                       param1=40, param2=10, minRadius=1, maxRadius=600)
            circles = np.uint16(np.around(circles))

            for i in circles[0, :]:
                Radii[t] = i[2]
                New_Cx[t] = x - RR + i[0]
                New_Cy[t] = y - RR + i[1]

        for i in range(0, len(Radii)):
            # draw the outer circle
            NCY = New_Cy[i]
            NCX = New_Cx[i]
            RDI = Radii[i]
            cv2.circle(im_in1, (int(NCX), int(NCY)), int(RDI), (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(im_in1, (int(NCX), int(NCY)), 2, (0, 0, 255), 2)

            ################### calculate background area  ###################
            TotalArea_Frame = int(im_in.shape[0] * im_in.shape[1])
            TotalArea_Droplets = 0
            for i in range(0, U):
                TotalArea_Droplets = (3.14 * Radii[i] * Radii[i]) + TotalArea_Droplets
            TotalArea_Background = TotalArea_Frame - TotalArea_Droplets
            for i in range(0, U):
                B[i] = TotalArea_Background

        ################### image show ###################
        # cv2.imshow("output", output)
        # im_in1 = cv2.resize(im_in1, (0, 0), fx=0.8, fy=0.8)
        # Original = cv2.resize(Original, (0, 0), fx=0.8, fy=0.8)
        # cv2.imshow("FinalCircles", im_in1)
        # cv2.imshow("Original", Original)
        # cv2.imshow("output", output)
        # cv2.imwrite("FinalCircles16050.png", im_in1)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # show the images
        # cv2.imshow("Initial", im_in)
        # cv2.imshow("Final", out)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Stacking and Saving
        #X = np.column_stack((New_Cx, New_Cy, Radii))
        #np.savetxt("CentroidsAndRadii.csv", X, delimiter=",")

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        Matrix = np.zeros((Radii.shape[0], 5), dtype=int)
        for row in range(0, len(Radii)):
            Matrix[row][0] = New_Cx[row]
            Matrix[row][1] = New_Cy[row]
            Matrix[row][2] = Radii[row]
            Matrix[row][3] = C[row]
            Matrix[row][4] = B[row]

        # print(Matrix)
        return Matrix, len(r)


    #np.savetxt(f'matrix from {i} frame', (create_Matrix(im_initial, im_in)[0]), newline=" ")

    my_df_1 = pd.DataFrame((create_Matrix(im_initial, im_in)[0]))
    my_df_1.columns =  ['0', '1', '2', '3', '4']
    my_df_1.to_csv(f'matrix from {i} frame.csv', index=False)  # save as csv



print("--- %s seconds ---" % (time.time() - start_time))