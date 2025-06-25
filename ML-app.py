from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()
# Load model khi khởi động ứng dụng
model = joblib.load("model_ml.joblib")

@app.post("/predict")
def predict(features: list[float]):
    prediction = model.predict(np.array([features]))  # Dự đoán
    return {"prediction": prediction.tolist()}

if __name__ == "__main__": # Chạy ứng dụng FastAPI
    # Sử dụng uvicorn để chạy ứng dụng FastAPI
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
