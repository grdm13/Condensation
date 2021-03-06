import cv2
import numpy as np
import math

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Read image
im_in = cv2.imread('/Users/georgedamoulakis/PycharmProjects/Droplets/splits/split1.jpg', cv2.IMREAD_GRAYSCALE);

def CountingCC():
# Threshold, Set values equal to or above 220 to 0, Set values below 220 to 255.
    th, im_th = cv2.threshold(im_in, 50, 220, cv2.THRESH_BINARY_INV);

    def CC (img):
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(img)
        label_hue = np.uint8(179*labels/np.max(labels))
        blank_ch = 255*np.ones_like(label_hue)
        labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
        labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
        labeled_img[label_hue==0] = 0
        return labeled_img, nlabels, labels, stats, centroids

#cleaning up the image get it ready to count
    blur = cv2.blur(im_th,(1,1))
    blur2 = cv2.blur(blur,(1,1))
    blur3 = cv2.blur(blur2,(1,1))
    kernel = np.ones((10,10),np.uint8)
    erosion2 = cv2.erode(blur3, kernel, iterations=1)
    dilation2 = cv2.dilate(erosion2,kernel,iterations=0)
    blur4 = cv2.blur(dilation2,(10,10))
    erosion = cv2.erode(blur4, kernel, iterations=1)
    dilation = cv2.dilate(erosion,kernel,iterations=0)

    #count droplets
    components, nlabels, labels, stats, centroids = CC(dilation2)
    print(f' There are ', (nlabels - 2 ), ' droplets')
#resize images, make them ready to show
    small1 = cv2.resize(im_in, (0, 0), fx=0.5, fy=0.5)
    small1 = cv2.cvtColor(small1, cv2.COLOR_GRAY2BGR)
    small2 = cv2.resize(im_th, (0, 0), fx=0.5, fy=0.5)
    small2 = cv2.cvtColor(small2, cv2.COLOR_GRAY2BGR)
    small3 = cv2.resize(blur, (0, 0), fx=0.5, fy=0.5)
    small3 = cv2.cvtColor(small3, cv2.COLOR_GRAY2BGR)
    result1 = np.hstack((small1, small2, small3))
    small4 = cv2.resize(blur2, (0, 0), fx=0.5, fy=0.5)
    small4 = cv2.cvtColor(small4, cv2.COLOR_GRAY2BGR)
    small5 = cv2.resize(blur3, (0, 0), fx=0.5, fy=0.5)
    small5 = cv2.cvtColor(small5, cv2.COLOR_GRAY2BGR)
    small6 = cv2.resize(erosion2, (0, 0), fx=0.5, fy=0.5)
    small6 = cv2.cvtColor(small6, cv2.COLOR_GRAY2BGR)
    result2 = np.hstack((small4, small5, small6))
    small7 = cv2.resize(dilation2, (0, 0), fx=0.5, fy=0.5)
    small7 = cv2.cvtColor(small7, cv2.COLOR_GRAY2BGR)
    small8 = cv2.resize(blur4, (0, 0), fx=0.5, fy=0.5)
    small8 = cv2.cvtColor(small8, cv2.COLOR_GRAY2BGR)
    small9 = cv2.resize(erosion, (0, 0), fx=0.5, fy=0.5)
    small9 = cv2.cvtColor(small9, cv2.COLOR_GRAY2BGR)
    result3 = np.hstack((small7, small8, small9))
    small10 = cv2.resize(dilation, (0, 0), fx=0.5, fy=0.5)
    small10 = cv2.cvtColor(small10, cv2.COLOR_GRAY2BGR)
    small11 = cv2.resize(blur4, (0, 0), fx=0.5, fy=0.5)
    small11= cv2.cvtColor(small11, cv2.COLOR_GRAY2BGR)
    small12 = cv2.resize(components, (0, 0), fx=0.5, fy=0.5)
    result4 = np.hstack((small10, small11, small12))
#show images
    cv2.imshow('image1/4, initial, thresh, blur', result1)
    cv2.imshow('image2/4, blur2, blur3, ero2', result2)
    cv2.imshow('image3/4, dil2, blur4, ero', result3)
    cv2.imshow('image4/4, dil, blur4, final', result4)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

# play with the stats and draw circles
    a = np.hsplit(stats, 5)
    horizontal = a[2]
    vertical = a[3]
    area = a[4]
    b = np.hsplit(centroids, 2)
    x_centr = b[0]
    y_centr = b[1]

    horizontalNEW = np.zeros(nlabels)
    verticalNEW = np.zeros(nlabels)
    TotalAreaNEW = np.zeros(nlabels)

    for i in range(nlabels):
        horizontalNEW[i] = horizontal[i] + 66
        verticalNEW[i] = vertical[i] + 66
        TotalAreaNEW[i] = (horizontalNEW[i] + verticalNEW[i]) * 3.14 * 0.25 * (horizontalNEW[i] + verticalNEW[i])


# new array with all the correct dimensions
# column 1 : x - centroid
# column 2 : y - centroid
# column 3: new horizontal
# column 4: new vertical
# column 5: new area

    NEW_dimensions = np.zeros((29, 5))

    for row in range(nlabels) :
        for column in range(5) :
            if column == 0:
                NEW_dimensions[row, column] = x_centr[row]
            elif column == 1:
                NEW_dimensions[row, column] = y_centr[row]
            elif column == 2:
                NEW_dimensions[row, column] = horizontalNEW[row]
            elif column == 3:
                NEW_dimensions[row, column] = verticalNEW[row]
            else:
                NEW_dimensions[row, column] = TotalAreaNEW[row]
        column = column +1
    row = row + 1
    #print(f' The correct dimensions are : (two first lines are background)' , NEW_dimensions)
    #imgplot = plt.imshow(components)
    #plt.show()

    image = components
    out = image.copy()
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for row in range(2, nlabels, 1):
        for column in range(5):
            # to find the centers of each
            cv2.rectangle(out, (x_centr[row] - 3, y_centr[row] - 3), (x_centr[row] + 3, y_centr[row] + 3), (0, 0, 0))
            #cv2.circle(out, (x_centr[row], y_centr[row]), int(((horizontalNEW[row] + verticalNEW[row]) * 0.25)), (0, 255, 0, 4))
            r = (math.sqrt(TotalAreaNEW[row] * 0.31830988618) * 0.5)
            cv2.circle(out, (x_centr[row], y_centr[row]), int(r), (255, 255, 0, 4))
        column = column + 1
    row = row + 1

    cv2.imshow("Final", out)
    cv2.waitKey(0)
    cv2.destroyAllWindows()




CountingCC()
