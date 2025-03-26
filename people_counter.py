
import cv2
import numpy as np
from ultralytics import YOLO
#import io


model = YOLO("best.pt")



CONF_THRESHOLD = 0.3
IOU_THRESHOLD = 0.4
IMG_SIZE = 640


def enhance_contrast(image):

    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


def count_people(image):
    #image = enhance_contrast(image)
    if image is None:
        raise ValueError("Error: Image is None. Decoding may have failed.")

    if not isinstance(image, np.ndarray):
        raise TypeError(f"Error: Expected numpy array, but got {type(image)}")

    print(f"Image shape: {image.shape if isinstance(image, np.ndarray) else 'N/A'}")
    print(f"Image dtype: {image.dtype if isinstance(image, np.ndarray) else 'N/A'}")

    # Ensure it's a 3-channel image
    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("Error: Image does not have 3 color channels (RGB).")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = model(image, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, imgsz=IMG_SIZE)

    person_boxes = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())

            if cls == 0 and conf > CONF_THRESHOLD:
                person_boxes.append((x1, y1, x2, y2, conf))


    #REMOVE DUBLICATES? I DONT UNDERSTAND

    return len(person_boxes)

def detect_people(img):
    imgToNumpy=np.array(img)
   
    
    num_people = count_people(imgToNumpy)

    return num_people

def process_image(image):



    # Apply contrast enhancement
    #enhanced_image = enhance_contrast(image)

    # Run YOLO detection on the enhanced image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
   
    results = model(image, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, imgsz=IMG_SIZE)

    # Extract person detections
    person_boxes = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())

            if cls == 0 and conf > CONF_THRESHOLD:  # Class 0 is 'person'
                person_boxes.append((x1, y1, x2, y2, conf))

    # Apply OpenCV NMS to remove duplicates
    if person_boxes:
        boxes = np.array([b[:4] for b in person_boxes])  # Extract only coordinates
        confidences = np.array([b[4] for b in person_boxes])  # Extract confidence scores

        indices = cv2.dnn.NMSBoxes(boxes.tolist(), confidences.tolist(), CONF_THRESHOLD, IOU_THRESHOLD)

        # Ensure indices is iterable and valid
        if indices is not None and len(indices) > 0:
            if indices.ndim == 2:
                indices = indices.flatten()
            final_boxes = [person_boxes[i] for i in indices]
        else:
            final_boxes = []
    else:
        final_boxes = []

    # Draw bounding boxes and labels
    num_people = len(final_boxes)
    for idx, (x1, y1, x2, y2, conf) in enumerate(final_boxes):
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f"Person {idx + 1} ({conf:.2f})", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    print(f"Processed image: Detected {num_people} persons")
    return image
      # Return the processed image

def view(files):
    #print("Received request at /view")

    
    try:
        imgToNumpy=np.array(img)
        
        

        if image is None:
            print("Error: Image decoding failed")
            return "Image decoding failed", 400

        # Process Image
        output_image = process_image(imgToNumpy)

        # Convert processed image to bytes
        #_, img_encoded = cv2.imencode('.jpg', output_image)
        #img_bytes = io.BytesIO(img_encoded.tobytes())

        print("Image successfully processed and sent")
        return output_image

    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}", 500