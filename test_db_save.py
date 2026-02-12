
from user_db_operations import save_structured_response
from response_parser import parse_structured_response

# Test response from the AI
test_response = '''**Understanding:**
The patient is experiencing symptoms of a common respiratory infection.

**Disease Diagnosis:**
Common Cold

**Treatment:**
Rest and drink plenty of fluids. Use over-the-counter medications for symptom relief.

**Medication:**
- Paracetamol 500mg
- Ibuprofen 400mg

**Conclusion:**
I am an AI assistant. Doctor's recommendation is important for proper diagnosis and treatment.'''

print("Testing structured response parsing and saving...")

# Parse the response
disease, probability, severity, medication, other_diagnoses, conclusion = parse_structured_response(test_response)
print(f'Parsed - Disease: {repr(disease)}')
print(f'Parsed - Probability: {repr(probability)}')
print(f'Parsed - Severity: {repr(severity)}')
print(f'Parsed - Medication: {repr(medication)}')
print(f'Parsed - Other Diagnoses: {repr(other_diagnoses)}')
print(f'Parsed - Conclusion: {repr(conclusion)}')

# Test saving to database (using dummy user_id and thread_id)
# Note: This will fail if no database exists or user/thread don't exist, but will show if the function works
try:
    result = save_structured_response(1, 1, "Test query about cold symptoms", disease, probability, severity, medication, other_diagnoses, conclusion)
    print(f'Database save result: {result}')
except Exception as e:
    print(f'Database save error (expected if no valid user/thread): {e}')
