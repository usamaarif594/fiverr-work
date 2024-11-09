import cv2
import torch
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn
from PIL import Image
import time
from facenet_pytorch import MTCNN

# Set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Define MobileNet model
model = models.mobilenet_v2(weights='DEFAULT')
num_ftrs = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_ftrs, 2)  # 2 classes: man and woman
model = model.to(device)

# Load the trained model weights
model_weights_path = 'gender_classifier_mobilenet.pth'
model.load_state_dict(torch.load(model_weights_path, map_location=device))
model.eval()

# Define data transformations
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Class names
class_names = ['Male', 'Female']

# Initialize MTCNN for face detection
mtcnn = MTCNN(keep_all=True, device=device)

def process_frame(frame):
    # Convert the frame to a PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Apply the transformations
    transformed_image = data_transforms(pil_image).unsqueeze(0).to(device)
    
    start_time = time.time()  # Record start time

    # Make prediction
    with torch.no_grad():
        output = model(transformed_image)
        _, pred = torch.max(output, 1)

    end_time = time.time()  # Record end time
    inference_time = (end_time - start_time) * 1000  # Convert to milliseconds

    print(f"Inference Time: {inference_time:.2f} ms")  # Print inference time

    return class_names[pred.item()]

def detect_faces_and_predict(frame):
    # Detect faces with MTCNN
    boxes, _ = mtcnn.detect(frame)

    if boxes is not None:
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face_region = frame[y1:y2, x1:x2]

            # Ensure the face region is not empty
            if face_region.size != 0:
                # Process the face region
                prediction = process_frame(face_region)

                # Draw a rectangle around the face
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Display the prediction on the frame
                cv2.putText(frame, f'Prediction: {prediction}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)

    return frame

def process_video_stream():
    # Start video capture from the webcam
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret:
            print("Failed to capture video frame. Stopping the webcam.")
            break

        # Process the frame
        frame = detect_faces_and_predict(frame)

        # Display the frame
        cv2.imshow('Gender Detection', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video_stream()
