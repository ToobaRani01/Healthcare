import prompt_builder

# Mock api_connection to test logic in isolation
class MockApiConnection:
    def __init__(self):
        self.current_threads = {}
        self.gemini_chat_sessions = {}
        self.chat_histories = {}
        self.UPLOAD_FOLDER = 'uploads'

    def get_gemini_response_logic(self, user_text, image_filename, image_analysis_result=None):
        is_symptom = False # Simple mock of is_symptom_query
        
        if image_filename:
            is_symptom = True
            
        if user_text and not is_symptom and not image_filename:
            return "non-symptom message"
        else:
            if is_symptom:
                prompt_text = user_text if user_text else "Analyzing the provided medical image."
                analysis_text = "Formatted Analysis" if image_analysis_result else None
                prompt = prompt_builder.build_symptom_prompt(prompt_text, analysis_text)
                return prompt
        return "default"

def test_multimodal_logic():
    print("--- Testing Multimodal Logic ---")
    api = MockApiConnection()
    
    # Test 1: Image + Vague text
    result = api.get_gemini_response_logic("what is this?", "test.jpg", True)
    assert "Visual Analysis Findings: Formatted Analysis" in result
    assert "Patient's Description: what is this?" in result
    print("Test 1 (Image + Vague text): PASSED")
    
    # Test 2: Image only
    result = api.get_gemini_response_logic(None, "test.jpg", True)
    assert "Patient's Description: Analyzing the provided medical image." in result
    print("Test 2 (Image only): PASSED")


if __name__ == "__main__":
    try:
        test_multimodal_logic()
        print("\nAll multimodal tests: PASSED")
    except Exception as e:
        print(f"\nTests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
