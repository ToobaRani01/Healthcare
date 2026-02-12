# image_analyzer.py
"""
Module for analyzing medical images using pre-trained ML models.
Supports chest X-ray pneumonia classification and skin disease analysis.
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

# Model paths
PNEUMONIA_MODEL_PATH = 'pneumonia_classification_model.h5'
SKIN_DISEASE_MODEL_PATH = 'skin_disease_final_model_2.h5'

# Global model variables
pneumonia_model = None
skin_disease_model = None

def load_pneumonia_model():
    """Load the pneumonia classification model."""
    global pneumonia_model
    if pneumonia_model is None:
        print("Loading pneumonia classification model...")
        print("Note: If loading fails, the model may need to be retrained with current TensorFlow version.")

        # Define custom objects for compatibility with older models
        custom_objects = {
            'DTypePolicy': 'float32',  # Handle newer dtype policy by using string fallback
        }

        try:
            # Try loading with safe_mode for newer TensorFlow versions
            pneumonia_model = tf.keras.models.load_model(PNEUMONIA_MODEL_PATH, compile=False, safe_mode=True)
            print("Pneumonia classification model loaded successfully.")
        except TypeError:
            # safe_mode not available, try normal loading
            try:
                pneumonia_model = tf.keras.models.load_model(PNEUMONIA_MODEL_PATH, compile=False)
                print("Pneumonia classification model loaded successfully.")
            except Exception as e:
                print(f"Error loading pneumonia model: {e}")
                try:
                    # Try with custom objects for compatibility
                    pneumonia_model = tf.keras.models.load_model(PNEUMONIA_MODEL_PATH, compile=False, custom_objects=custom_objects)
                    print("Pneumonia classification model loaded with custom objects.")
                except Exception as e2:
                    print(f"Error loading pneumonia model with custom objects: {e2}")
                    # Try to fix batch_shape compatibility issue
                    pneumonia_model = _load_model_with_batch_shape_fix(PNEUMONIA_MODEL_PATH, custom_objects)
        except Exception as e:
            print(f"Error loading pneumonia model: {e}")
            try:
                # Try with custom objects for compatibility
                pneumonia_model = tf.keras.models.load_model(PNEUMONIA_MODEL_PATH, compile=False, custom_objects=custom_objects)
                print("Pneumonia classification model loaded with custom objects.")
            except Exception as e2:
                print(f"Error loading pneumonia model with custom objects: {e2}")
                # Try to fix batch_shape compatibility issue
                pneumonia_model = _load_model_with_batch_shape_fix(PNEUMONIA_MODEL_PATH, custom_objects)
    return pneumonia_model

def _load_model_with_batch_shape_fix(model_path, custom_objects=None):
    """Load model after fixing batch_shape compatibility issues."""
    if custom_objects is None:
        custom_objects = {}

    try:
        import h5py
        import json
        import tempfile

        # Create a temporary copy of the model file
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Copy the original file
            import shutil
            shutil.copy2(model_path, temp_path)

            # Modify the temporary file to remove problematic parameters
            with h5py.File(temp_path, 'r+') as f:
                if 'model_config' in f.attrs:
                    config_str = f.attrs['model_config']
                    config = json.loads(config_str)

                    # Function to remove problematic parameters from nested config
                    def clean_config(obj):
                        if isinstance(obj, dict):
                            # Remove problematic parameters
                            obj.pop('batch_shape', None)
                            # Handle dtype_policy variations
                            if 'dtype_policy' in obj:
                                if obj['dtype_policy'] == 'DTypePolicy':
                                    obj['dtype_policy'] = None
                            for key, value in obj.items():
                                clean_config(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                clean_config(item)

                    clean_config(config)

                    # Save the cleaned config
                    f.attrs['model_config'] = json.dumps(config)

            # Try to load the fixed model
            model = tf.keras.models.load_model(temp_path, compile=False, custom_objects=custom_objects)
            print("Pneumonia classification model loaded after fixing compatibility issues.")

            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

            return model

        except Exception as e:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            print(f"Error fixing compatibility: {e}")
            return None

    except ImportError:
        print("h5py not available for model compatibility fix")
        return None
    except Exception as e:
        print(f"Error in compatibility fix: {e}")
        return None

def load_skin_disease_model():
    """Load the skin disease classification model."""
    global skin_disease_model
    if skin_disease_model is None:
        try:
            # Try loading with different approaches for compatibility
            skin_disease_model = tf.keras.models.load_model(SKIN_DISEASE_MODEL_PATH, compile=False)
            print("Skin disease classification model loaded successfully.")
        except Exception as e:
            print(f"Error loading skin disease model: {e}")
            try:
                # Alternative loading method for older models
                skin_disease_model = tf.keras.models.load_model(SKIN_DISEASE_MODEL_PATH, custom_objects={})
                print("Skin disease classification model loaded with custom objects.")
            except Exception as e2:
                print(f"Error loading skin disease model with custom objects: {e2}")
                skin_disease_model = None
    return skin_disease_model

def preprocess_image_for_pneumonia(image_path, target_size=(224, 224)):
    """
    Preprocess image for pneumonia classification.
    Converts to grayscale as the model expects single-channel input.

    Args:
        image_path (str): Path to the image file
        target_size (tuple): Target size for the model input

    Returns:
        numpy.ndarray: Preprocessed image array
    """
    try:
        img = Image.open(image_path)
        # Convert to grayscale (L mode) for pneumonia model
        if img.mode != 'L':
            img = img.convert('L')

        # Resize image
        img = img.resize(target_size)

        # Convert to array and normalize
        img_array = np.array(img) / 255.0

        # Add channel dimension for grayscale (1 channel)
        img_array = np.expand_dims(img_array, axis=-1)

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array
    except Exception as e:
        print(f"Error preprocessing image for pneumonia analysis: {e}")
        return None

def preprocess_image_for_skin_disease(image_path, target_size=(224, 224)):
    """
    Preprocess image for skin disease classification.

    Args:
        image_path (str): Path to the image file
        target_size (tuple): Target size for the model input

    Returns:
        numpy.ndarray: Preprocessed image array
    """
    try:
        img = Image.open(image_path)
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize image
        img = img.resize(target_size)

        # Convert to array and normalize
        img_array = np.array(img) / 255.0

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)

        return img_array
    except Exception as e:
        print(f"Error preprocessing image for skin disease analysis: {e}")
        return None

def analyze_chest_xray(image_path):
    """
    Analyze a chest X-ray image for pneumonia.

    Args:
        image_path (str): Path to the chest X-ray image

    Returns:
        dict: Analysis results with classification and confidence
    """
    model = load_pneumonia_model()
    if model is None:
        return {
            "analysis_type": "chest_xray",
            "classification": "unknown",
            "confidence": 0.0,
            "error": "Pneumonia model not available - model may need to be retrained with current TensorFlow version"
        }

    # Preprocess image
    processed_image = preprocess_image_for_pneumonia(image_path)
    if processed_image is None:
        return {
            "analysis_type": "chest_xray",
            "classification": "unknown",
            "confidence": 0.0,
            "error": "Image preprocessing failed"
        }

    try:
        # Make prediction
        predictions = model.predict(processed_image, verbose=0)
        confidence = float(predictions[0][0])

        # Assuming binary classification: 0 = Normal, 1 = Pneumonia
        classification = "pneumonia" if confidence > 0.5 else "normal"
        confidence_score = confidence if confidence > 0.5 else (1 - confidence)

        return {
            "analysis_type": "chest_xray",
            "classification": classification,
            "confidence": round(confidence_score * 100, 2),
            "raw_confidence": confidence,
            "description": f"Chest X-ray analysis indicates {classification} with {round(confidence_score * 100, 2)}% confidence."
        }
    except Exception as e:
        print(f"Error analyzing chest X-ray: {e}")
        return {
            "analysis_type": "chest_xray",
            "classification": "unknown",
            "confidence": 0.0,
            "error": str(e)
        }

def analyze_skin_disease(image_path):
    """
    Analyze a skin image for disease classification.

    Args:
        image_path (str): Path to the skin disease image

    Returns:
        dict: Analysis results with classification and confidence
    """
    model = load_skin_disease_model()
    if model is None:
        return {
            "analysis_type": "skin_disease",
            "classification": "unknown",
            "confidence": 0.0,
            "error": "Model not available"
        }

    # Preprocess image
    processed_image = preprocess_image_for_skin_disease(image_path)
    if processed_image is None:
        return {
            "analysis_type": "skin_disease",
            "classification": "unknown",
            "confidence": 0.0,
            "error": "Image preprocessing failed"
        }

    try:
        # Make prediction
        predictions = model.predict(processed_image, verbose=0)

        # Get the predicted class and confidence
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])

        # Map class indices to disease names (this may need adjustment based on your model's training)
        class_names = [
            "Actinic Keratosis", "Basal Cell Carcinoma", "Benign Keratosis",
            "Dermatofibroma", "Melanocytic Nevus", "Melanoma", "Squamous Cell Carcinoma",
            "Vascular Lesion", "Unknown"
        ]

        classification = class_names[predicted_class_idx] if predicted_class_idx < len(class_names) else "Unknown"

        return {
            "analysis_type": "skin_disease",
            "classification": classification,
            "confidence": round(confidence * 100, 2),
            "raw_confidence": confidence,
            "description": f"Skin analysis indicates {classification} with {round(confidence * 100, 2)}% confidence."
        }
    except Exception as e:
        print(f"Error analyzing skin disease: {e}")
        return {
            "analysis_type": "skin_disease",
            "classification": "unknown",
            "confidence": 0.0,
            "error": str(e)
        }

def detect_image_type(image_path):
    """
    Detect the type of medical image based on characteristics.

    Args:
        image_path (str): Path to the image

    Returns:
        str: Image type ('chest_xray', 'skin_disease', or 'unknown')
    """
    try:
        img = Image.open(image_path)
        width, height = img.size

        # Simple heuristic: chest X-rays are typically wider than tall
        # Skin disease images might be more square or varied
        if width > height * 1.2:
            return "chest_xray"
        else:
            return "skin_disease"

    except Exception as e:
        print(f"Error detecting image type: {e}")
        return "unknown"

def analyze_medical_image(image_path):
    """
    Main function to analyze a medical image.
    Automatically detects image type and applies appropriate analysis.

    Args:
        image_path (str): Path to the medical image

    Returns:
        dict: Analysis results
    """
    if not os.path.exists(image_path):
        return {
            "analysis_type": "unknown",
            "classification": "error",
            "confidence": 0.0,
            "error": "Image file not found"
        }

    # Detect image type
    image_type = detect_image_type(image_path)

    # Analyze based on detected type
    if image_type == "chest_xray":
        return analyze_chest_xray(image_path)
    elif image_type == "skin_disease":
        return analyze_skin_disease(image_path)
    else:
        # Try both analyses if detection is uncertain
        chest_result = analyze_chest_xray(image_path)
        skin_result = analyze_skin_disease(image_path)

        # Return the result with higher confidence
        if chest_result.get("confidence", 0) > skin_result.get("confidence", 0):
            return chest_result
        else:
            return skin_result

def format_analysis_for_prompt(analysis_result):
    """
    Format image analysis results for inclusion in AI prompts.

    Args:
        analysis_result (dict): Results from image analysis

    Returns:
        str: Formatted analysis text for prompts
    """
    if analysis_result.get("error"):
        return f"Image analysis failed: {analysis_result['error']}"

    analysis_type = analysis_result.get("analysis_type", "unknown")
    classification = analysis_result.get("classification", "unknown")
    confidence = analysis_result.get("confidence", 0.0)

    if analysis_type == "chest_xray":
        return f"Chest X-ray Analysis: {classification} (confidence: {confidence}%)"
    elif analysis_type == "skin_disease":
        return f"Skin Disease Analysis: {classification} (confidence: {confidence}%)"
    else:
        return f"Medical Image Analysis: {classification} (confidence: {confidence}%)"
