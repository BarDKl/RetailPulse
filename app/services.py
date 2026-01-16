import pathlib as pth
import pickle
import numpy as np

class ModelService:
    def __init__(self):
        self.base_dir = pth.Path(__file__).parent.absolute()
        self.model_path = pth.Path.joinpath(self.base_dir, 'final_models' , 'pickles' , 'rfm_pipeline.pkl')
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            if pth.Path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print('Model loaded succesfuly')
            else:
                print(f"ERROR: no file at {self.model_path}")
        except Exception as e:
            print(f"ERROR: {e}")

    def predict(self, recency, frequency, monetary):
        if not self.model:
            return 'no model loaded'
        input_data = np.array([[recency, frequency, monetary]])
        prediction = self.model.predict(input_data)[0]

        segment_map = {
            0: 'Casual',
            1: 'Loyal',
            2: 'VIP'
        }
        return segment_map.get(int(prediction), 'Unknown')
run_model = ModelService()
