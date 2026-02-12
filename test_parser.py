from response_parser import parse_structured_response

# Test with a sample response that should match the expected format
test_response = '''**Case Description:**
The patient is experiencing symptoms of a common respiratory infection.

**Primary Diagnosis:**
Common Cold (85%)

**Severity Level:**
Mild

**Treatment:**
Rest and drink plenty of fluids. Use over-the-counter medications for symptom relief.

**Medication:**
- Paracetamol 500mg, 1 tablet twice a day for 3 days
- Ibuprofen 400mg, 1 tablet every 6 hours for 5 days

**Other Probable Diagnoses:**
None

**Disclaimer:**
I am an AI assistant. Doctor's recommendation is important for proper diagnosis and treatment.'''

print("Testing with properly formatted response:")
case_desc, disease, probability, severity, medication, other_diagnoses, disclaimer = parse_structured_response(test_response)
print('Case Description:', repr(case_desc))
print('Disease:', repr(disease))
print('Probability:', repr(probability))
print('Severity:', repr(severity))
print('Medication:', repr(medication))
print('Other Diagnoses:', repr(other_diagnoses))
print('Disclaimer:', repr(disclaimer))

print("\n" + "="*50 + "\n")

# Test with a different format to see how robust the parser is
test_response2 = '''Understanding:
The patient has a fever and cough.

Disease Diagnosis:
Flu (90%)

Severity level: Moderate

Treatment:
Rest and drink fluids.

Medication:
- Paracetamol

Conclusion:
Consult a doctor.'''

print("Testing with differently formatted response:")
case_desc2, disease2, probability2, severity2, medication2, other_diagnoses2, disclaimer2 = parse_structured_response(test_response2)
print('Case Description:', repr(case_desc2))
print('Disease:', repr(disease2))
print('Probability:', repr(probability2))
print('Severity:', repr(severity2))
print('Medication:', repr(medication2))
print('Other Diagnoses:', repr(other_diagnoses2))
print('Disclaimer:', repr(disclaimer2))
