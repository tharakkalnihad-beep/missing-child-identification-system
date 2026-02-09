import os
import torch
import numpy as np
from PIL import Image, ImageDraw
from facenet_pytorch import MTCNN, InceptionResnetV1
import pickle


class MissingChildPredictor:

    def __init__(self, model_path="missing_child_model.pkl", threshold=0.75):
        self.model_path = model_path
        self.threshold = threshold

        # ------------------- DEVICE -------------------
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[INFO] Using device: {self.device}")

        # ------------------- MTCNN FACE DETECTOR -------------------
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            keep_all=False,        # only single face
            device=self.device
        )

        # ------------------- FACENET EMBEDDING MODEL -------------------
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)

        # ------------------- LOAD MODEL -------------------
        self.load_model()

    # --------------------------------------------------------
    def load_model(self):
        """Load trained missing child embeddings"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found → {self.model_path}")

        with open(self.model_path, "rb") as f:
            data = pickle.load(f)

        self.embeddings = data.get("embeddings", {})
        print(f"[OK] Loaded embeddings: {len(self.embeddings)} children")

    # --------------------------------------------------------
    def extract_embedding(self, face_tensor):
        """Convert cropped face to embedding"""
        with torch.no_grad():
            face_tensor = face_tensor.to(self.device)
            embedding = self.resnet(face_tensor).cpu().numpy()[0]
        return embedding

    # --------------------------------------------------------
    def predict(self, image_path):
        """Predict missing child from uploaded image"""

        if not os.path.exists(image_path):
            return {"status": "error", "message": "Image file does not exist"}

        # Load image
        img = Image.open(image_path).convert("RGB")

        # Detect face
        face = self.mtcnn(img)

        if face is None:
            return {"status": "no_face", "message": "No face detected"}

        # Convert to batch tensor
        face_tensor = face.unsqueeze(0)

        # Generate embedding for uploaded face
        embedding = self.extract_embedding(face_tensor)

        # ---------------- MATCH WITH SAVED CHILDREN ----------------
        best_distance = float("inf")
        best_child = "Unknown"
        best_id = None

        for key, saved_emb in self.embeddings.items():
            saved_emb = np.array(saved_emb)

            # Euclidean distance
            dist = np.linalg.norm(embedding - saved_emb)

            if dist < best_distance:
                best_distance = dist
                best_child = key
                best_id = key.split("/")[0]  # case_id

        # ---------------- THRESHOLD CHECK ----------------
        if best_distance > self.threshold:
            return {
                "status": "unknown",
                "name": "Unknown",

            }

        # Extract nice name: "21/Anu" → "Anu"
        child_name = best_child.split("/")[1]

        # Final output
        return {
            "status": "success",
            "case_id": best_id,
            "name": child_name,
            "distance": float(best_distance)
        }


# --------------------------------------------------------
# TEST MODE (DIRECT RUN)
# --------------------------------------------------------
if __name__ == "__main__":
    print("\n===== Missing Child Predictor =====")

    predictor = MissingChildPredictor(
        model_path="missing_child_model.pkl",
        threshold=0.75
    )

    img_path = input("Enter image path to test: ")

    result = predictor.predict(img_path)
    print("\nRESULT =", result)
