import cv2
import numpy as np
import imutils
import easyocr
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize EasyOCR reader globally
reader = easyocr.Reader(['en'], gpu=False)

def process_license_plate(image_path):
    try:
        logging.info(f"Processing image: {image_path}")
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            logging.error(f"Failed to load image: {image_path}")
            return {'error': 'Failed to load image', 'text': None, 'processed_image': None, 'original': None, 'grayscale': None, 'edge': None, 'contoured': None, 'cropped': None}

        # Save original image
        original_path = f'Uploads/original_{os.path.basename(image_path)}'
        cv2.imwrite(original_path, img)
        logging.info(f"Saved original image: {original_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        grayscale_path = f'Uploads/grayscale_{os.path.basename(image_path)}'
        cv2.imwrite(grayscale_path, gray)
        logging.info(f"Saved grayscale image: {grayscale_path}")

        # Apply bilateral filter and edge detection
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(bfilter, 30, 200)
        edge_path = f'Uploads/edge_{os.path.basename(image_path)}'
        cv2.imwrite(edge_path, edged)
        logging.info(f"Saved edge image: {edge_path}")

        # Find contours
        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(keypoints)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        # Find quadrilateral contour (license plate)
        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        if location is None:
            logging.warning(f"No license plate detected in {image_path}")
            return {'error': 'No license plate detected', 'text': None, 'processed_image': None, 'original': original_path, 'grayscale': grayscale_path, 'edge': edge_path, 'contoured': None, 'cropped': None}

        # Draw contours on original image
        contoured_img = img.copy()
        cv2.drawContours(contoured_img, [location], -1, (0, 255, 0), 3)
        contoured_path = f'Uploads/contoured_{os.path.basename(image_path)}'
        cv2.imwrite(contoured_path, contoured_img)
        logging.info(f"Saved contoured image: {contoured_path}")

        # Extract license plate
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_image = gray[x1:x2+1, y1:y2+1]

        # Save cropped image
        cropped_path = f'Uploads/cropped_{os.path.basename(image_path)}'
        cv2.imwrite(cropped_path, cropped_image)
        logging.info(f"Saved cropped image: {cropped_path}")

        # Apply additional preprocessing for OCR
        cropped_image = cv2.GaussianBlur(cropped_image, (3, 3), 0)
        _, cropped_image = cv2.threshold(cropped_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Perform OCR
        result = reader.readtext(cropped_image)
        if not result:
            logging.warning(f"No text detected in {image_path}")
            return {'error': 'No text detected', 'text': None, 'processed_image': None, 'original': original_path, 'grayscale': grayscale_path, 'edge': edge_path, 'contoured': contoured_path, 'cropped': cropped_path}

        # Extract text and annotate image
        text = result[0][-2].upper()
        font = cv2.FONT_HERSHEY_SIMPLEX
        res = cv2.putText(img, text=text, org=(location[0][0][0], location[1][0][1]+60),
                          fontFace=font, fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
        res = cv2.rectangle(img, tuple(location[0][0]), tuple(location[2][0]), (0, 255, 0), 3)

        # Save processed image
        output_path = f'Uploads/processed_{os.path.basename(image_path)}'
        cv2.imwrite(output_path, res)
        logging.info(f"Saved processed image: {output_path}")

        return {
            'text': text,
            'processed_image': output_path,
            'original': original_path,
            'grayscale': grayscale_path,
            'edge': edge_path,
            'contoured': contoured_path,
            'cropped': cropped_path,
            'error': None
        }
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return {
            'error': str(e),
            'text': None,
            'processed_image': None,
            'original': None,
            'grayscale': None,
            'edge': None,
            'contoured': None,
            'cropped': None
        }