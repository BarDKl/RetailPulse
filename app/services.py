import pathlib as pth
import pickle
import numpy as np

class ModelService:
    def __init__(self):
        self.base_dir = pth.Path(__file__).parent.absolute()
        self.rfm_path = pth.Path.joinpath(self.base_dir, 'final_models', 'pickles', 'rfm_model.pkl')
        self.rfm_model = None
        self.clv_path = pth.Path.joinpath(self.base_dir, 'final_models', 'pickles', 'clv_model.pkl')
        self.clv.model = None
        self.load_models()

    def load_models(self):
        try:
            if pth.Path.exists(self.rfm_path):
                with open(self.rfm_path, 'rb') as f:
                    self.rfm_model = pickle.load(f)
                print('RFM Model loaded succesfuly')
            else:
                print(f"ERROR: RFM model not found at {self.rfm_path}")
        except Exception as e:
            print(f"ERROR loading RFM model: {e}")
        try:
            if pth.Path.exists(self.clv_path):
                with open(self.clv_path, "rb") as f:
                    self.clv_model = pickle.load(f)
                print("CLV Model loaded successfully")
            else:
                print(f"Warning: CLV model not found at {self.clv_path}")
        except Exception as e:
            print(f"Error loading CLV model: {e}")

    def predict_rfm(self, recency, frequency, monetary):
        if not self.rfm_model:
            return 'no model loaded'
        input_data = np.array([[recency, frequency, monetary]])
        prediction = self.rfm_model.predict(input_data)[0]

        segment_map = {
            0: 'Casual',
            1: 'Loyal',
            2: 'VIP'
        }
        return segment_map.get(int(prediction), 'Unknown')
    def predict_clv(self, recency, frequency, monetary):
        if not self.clv_model:
            return 'no model loaded'
        input_data = np.array([[recency, frequency, monetary]])
        prediction = self.clv_model.predict(input_data)[0]
        return round(prediction,2)

run_model = ModelService()
