# test_image_analysis.py
"""
Test script for image analysis functionality
"""

import os
from image_analyzer import analyze_medical_image, analyze_chest_xray, analyze_skin_disease, detect_image_type

def test_image_analysis():
    """Test the image analysis functions with sample images."""

    # Get list of uploaded images
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        print("Uploads directory not found!")
        return

    image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

    if not image_files:
        print("No image files found in uploads directory!")
        return

    print(f"Found {len(image_files)} image files. Testing image analysis...")

    for image_file in image_files[:3]:  # Test first 3 images
        image_path = os.path.join(uploads_dir, image_file)
        print(f"\n--- Testing {image_file} ---")

        # Detect image type
        image_type = detect_image_type(image_path)
        print(f"Detected image type: {image_type}")

        # Analyze with general function
        result = analyze_medical_image(image_path)
        print(f"Analysis result: {result}")

        # Test specific functions
        if image_type == "chest_xray":
            chest_result = analyze_chest_xray(image_path)
            print(f"Chest X-ray specific result: {chest_result}")
        elif image_type == "skin_disease":
            skin_result = analyze_skin_disease(image_path)
            print(f"Skin disease specific result: {skin_result}")

if __name__ == "__main__":
    test_image_analysis()
