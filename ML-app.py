from fastapi import FastAPI, HTTPException
import joblib
import numpy as np
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from functools import wraps
from typing import List
import logging
import time

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resource chung cho cả tracing và metrics
resource = Resource.create({SERVICE_NAME: "ml-prediction-service"})

# 1. Thiết lập Tracing với Jaeger
set_tracer_provider(
    TracerProvider(resource=resource)
)

# Tạo Jaeger Exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

# Thêm processor để gửi span đến Jaeger
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Lấy tracer
tracer = get_tracer_provider().get_tracer("ml-prediction", "0.1.2")

# 2. Thiết lập Metrics với Prometheus
prometheus_reader = PrometheusMetricReader()
set_meter_provider(
    MeterProvider(
        resource=resource,
        metric_readers=[prometheus_reader]
    )
)

# Lấy meter
meter = get_meter_provider().get_meter("ml-prediction", "0.1.2")

# Tạo các metrics
model_request_counter = meter.create_counter(
    name="model_request_counter",
    description="Total number of requests sent to model",
    unit="1"
)

prediction_duration_histogram = meter.create_histogram(
    name="ml_prediction_duration_seconds",
    description="Time spent on predictions",
    unit="s"
)

error_counter = meter.create_counter(
    name="ml_errors_total",
    description="Total number of errors",
    unit="1"
)

app = FastAPI(title="ML Prediction Service", version="0.1.0")

# Biến global để cache model
cached_model = None

# 2. Tạo decorator để tự động trace cho các function
def trace_span(span_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator

# 3. Load model với tracing
@trace_span("model-loader")
def load_model():
    global cached_model
    if cached_model is not None:
        return cached_model
    
    try:
        logger.info("Loading model...")
        
        cached_model = joblib.load("model_ml.joblib")
        logger.info("Model loaded successfully")
        
        return cached_model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        
        # Increment error counters
        error_counter.add(1, {"operation": "model_load", "error_type": type(e).__name__})
        
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

# 4. Hàm dự đoán với tracing và metrics
@trace_span("predictor")
def make_prediction(model, features):
    start_time = time.time()
    
    try:
        logger.info(f"Making prediction with features: {features}")
        
        # Kiểm tra input
        if not features:
            raise ValueError("Features cannot be empty")
        
        # Chuyển đổi features thành numpy array
        features_array = np.array([features])
        
        # Thực hiện dự đoán
        prediction = model.predict(features_array)
        
        logger.info(f"Prediction result: {prediction}")
        
        # Chuyển đổi kết quả thành list
        result = prediction.tolist()
        
        # Record successful prediction metrics
        duration = time.time() - start_time
        prediction_duration_histogram.record(duration, {"status": "success"})
        
        return result
        
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        
        # Record error metrics
        duration = time.time() - start_time
        prediction_duration_histogram.record(duration, {"status": "error"})
        error_counter.add(1, {"operation": "prediction", "error_type": type(e).__name__})
        
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# 5. API endpoint với tracing và metrics
@app.post("/predict")
def predict(features: List[float]):
    endpoint_start_time = time.time()
    
    # Đếm số lượng request được gửi đến model
    model_request_counter.add(1, {"endpoint": "/predict"})
    
    try:
        with tracer.start_as_current_span("prediction-endpoint") as span:
            logger.info(f"Received prediction request with features: {features}")
            
            # Thêm thông tin vào span
            span.set_attribute("input.features", str(features))
            span.set_attribute("input.length", len(features))
            
            # Load model
            model = load_model()
            
            # Thực hiện dự đoán
            prediction = make_prediction(model, features)
            
            # Thêm thông tin prediction vào span
            span.set_attribute("prediction.result", str(prediction))
            span.set_attribute("prediction.success", True)
            
            # Record endpoint metrics
            endpoint_duration = time.time() - endpoint_start_time
            prediction_duration_histogram.record(endpoint_duration, {"endpoint": "/predict", "status": "success"})
            
            logger.info(f"Returning prediction: {prediction}")
            return {"prediction": prediction, "status": "success"}
            
    except HTTPException as he:
        # Record HTTP error metrics
        endpoint_duration = time.time() - endpoint_start_time
        prediction_duration_histogram.record(endpoint_duration, {"endpoint": "/predict", "status": "http_error"})
        error_counter.add(1, {"operation": "endpoint", "error_type": "HTTPException"})
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in prediction endpoint: {e}")
        
        # Record unexpected error metrics
        endpoint_duration = time.time() - endpoint_start_time
        prediction_duration_histogram.record(endpoint_duration, {"endpoint": "/predict", "status": "error"})
        error_counter.add(1, {"operation": "endpoint", "error_type": type(e).__name__})
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint để expose Prometheus metrics
@app.get("/metrics")
def get_metrics():
    """Endpoint để Prometheus scrape metrics"""
    from prometheus_client import generate_latest
    return generate_latest()

# Health check endpoints
@app.get("/")
def root():
    return {"message": "ML Prediction Service is running"}

@app.get("/health")
def health():
    try:
        # Kiểm tra xem model có load được không
        model_loaded = cached_model is not None
        if not model_loaded:
            try:
                load_model()
                model_loaded = True
            except:
                model_loaded = False
        
        return {
            "status": "healthy",
            "model_loaded": model_loaded,
            "service": "ml-prediction-service",
            "metrics_endpoint": "/metrics"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Load model khi startup
@app.on_event("startup")
def startup_event():
    logger.info("Starting ML Prediction Service...")
    try:
        load_model()
        logger.info("Model loaded successfully during startup")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {e}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ML Prediction Service...")
    uvicorn.run(app, host="0.0.0.0", port=5000)