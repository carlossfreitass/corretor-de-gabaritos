import cv2

def convert_to_gray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def threshold_image(gray):
    _, thresh = cv2.threshold(
        gray,
        150,
        255,
        cv2.THRESH_BINARY_INV
    )
    return thresh

def threshold_otsu(gray):
    _, binaria = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binaria