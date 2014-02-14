import cv2

img = cv2.imread('C:\Users\Mattias\Desktop\Naamloos.png')
gray = cv2.imread('C:\Users\Mattias\Desktop\Naamloos.png', 0)
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
contours, _ = cv2.findContours(thresh, 1, 2)

for contour in contours:
    if cv2.arcLength(contour, True) > 100:
        simp = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
        if len(simp) == 4:
            print 'square'
            cv2.drawContours(img, [contour], 0, (0, 0, 255), -1)
        elif len(simp) == 3:
            print 'triangle'


cv2.imshow('img', img)

cv2.waitKey(0)