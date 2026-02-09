import os
import django
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import pickle
from tqdm import tqdm


# ---------------------------------------------------------
# DJANGO SETUP  (EDIT THIS TO MATCH YOUR PROJECT NAME)
# ---------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

# ---------------------------------------------------------
# IMPORT YOUR MODELS  (EDIT app → your app name)
# ---------------------------------------------------------
from app.models import Case_Report


class MissingChildTrainer:

    def __init__(self, model_path="missing_child_model.pkl", random_seed=42):
        self.model_path = model_path

        np.random.seed(random_seed)
        torch.manual_seed(random_seed)

        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[INFO] Using device: {self.device}")

        # Face detector
        self.mtcnn = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],
            factor=0.709,
            post_process=True,
            device=self.device
        )

        # Face embedding model
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)

        self.load_model()

    # ---------------------------------------------------------
    def load_model(self):
        """Load existing model or create new one"""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
            self.child_embeddings = data.get("embeddings", {})
            print(f"[INFO] Loaded model → {self.model_path}")

        else:
            print("[INFO] No model found. Creating new model...")
            self.child_embeddings = {}

    # ---------------------------------------------------------
    def extract_embedding(self, image_path):
        """Extract a 512-D embedding from image"""
        try:
            img = Image.open(image_path).convert("RGB")
            face = self.mtcnn(img)

            if face is None:
                print(f"[WARN] No face detected → {image_path}")
                return None

            face = face.unsqueeze(0).to(self.device)

            with torch.no_grad():
                emb = self.resnet(face).cpu().numpy()[0]

            return emb

        except Exception as e:
            print(f"[ERROR] extract_embedding failed: {e}")
            return None

    # ---------------------------------------------------------
    def add_person(self, person_id, person_name, folder_path):
        """Train a single missing child (when a case is submitted)"""

        images = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not images:
            raise Exception("No training images found")

        embeddings = []

        # repeat images (simulate more data)
        for img in images * 10:
            emb = self.extract_embedding(img)
            if emb is not None:
                embeddings.append(emb)

        if not embeddings:
            raise Exception("Could not extract face embedding")

        avg_emb = np.mean(embeddings, axis=0)

        key = f"{person_id}/{person_name}"
        self.child_embeddings[key] = avg_emb.tolist()

        print(f"[OK] Trained child → {key}")

    # ---------------------------------------------------------
    def train_all_children(self):
        """Train all missing children from database"""
        cases = Case_Report.objects.all()

        for case in tqdm(cases, desc="Training All Children"):

            if not case.image:
                continue

            image_path = os.path.join("media", str(case.image))
            embedding = self.extract_embedding(image_path)

            if embedding is None:
                continue

            key = f"{case.id}/{case.child_name}"
            self.child_embeddings[key] = embedding.tolist()

        self.save_model()

    # ---------------------------------------------------------
    def save_model(self):
        """Save all embeddings to file"""
        with open(self.model_path, "wb") as f:
            pickle.dump({"embeddings": self.child_embeddings}, f)

        print(f"[✓] Model saved → {self.model_path}")

    # ---------------------------------------------------------
    def summary(self):
        print("\n=== MODEL SUMMARY ===")
        for key in self.child_embeddings:
            print(f" → {key}")
        print("=====================\n")


# ---------------------------------------------------------
# RUN DIRECTLY (python train.py)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n===== Missing Child Trainer =====")
    trainer = MissingChildTrainer()
    trainer.train_all_children()
    trainer.summary()
