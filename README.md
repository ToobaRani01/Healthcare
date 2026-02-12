# 🩺 Healthcare AI Chatbot - Simple Guide

Yeh ek Healthcare AI Chatbot hai jo aapko medical symptoms aur images analyze karne mein help karta hai. Ismein do tarah ke AI models use hote hain - local models (jo aapke computer par hain) aur Google Gemini API (online).

## 📋 Project Kya Karta Hai?

Yeh chatbot aapko:
- Medical symptoms ke bare mein baat karne ki facility deta hai
- Medical images (chest X-ray, skin disease photos) analyze karta hai
- Disease diagnosis aur treatment suggestions deta hai
- Saari baat-cheet ko database mein save karta hai

## 🎯 Kaise Kaam Karta Hai? (Simple Explanation)

### **Step 1: Image Upload Hone Par - Complete Flow**

#### **Stage 1: Image Type Detection (Pehle Yeh Hota Hai)**
- System pehle image ko analyze karta hai ke **kis type ki image hai**
- Image type detect karne ke liye width/height ratio check hota hai
- Possible types:
  - **Chest X-ray** (wider images - width > height * 1.2)
  - **Skin Disease** (square ya varied ratio)
  - **Unknown** (agar detect nahi ho paya)

#### **Stage 2: Model Analysis (Agar Image Type Match Kare)**
- **Agar Chest X-ray Detect Hui:**
  - `pneumonia_classification_model.h5` model load hota hai
  - Model image ko analyze karke result deta hai (Normal/Pneumonia with confidence)
  - Model ka output text format mein milta hai (e.g., "Chest X-ray Analysis: pneumonia (confidence: 85%)")

- **Agar Skin Disease Detect Hui:**
  - `skin_disease_final_model_2.h5` model load hota hai
  - Model image ko analyze karke disease classify karta hai (e.g., "Melanoma", "Basal Cell Carcinoma")
  - Model ka output text format mein milta hai (e.g., "Skin Disease Analysis: Melanoma (confidence: 92%)")

- **Agar Image Type Unknown Hai (CT Scan, MRI, Ultrasound, etc.):**
  - Dono models try kiye jate hain (optional)
  - Lekin inka result reliable nahi hota kyunki yeh models sirf chest X-ray aur skin disease ke liye trained hain
  - Model output mil sakta hai ya nahi - koi problem nahi

#### **Stage 3: API Call (Kab Hoti Hai Aur Kab Nahi)**
- **Gemini API call tab hoti hai jab:**
  1. **Image upload hui ho** (chahe text query ho ya na ho) → API call hoti hai
  2. **Symptom-based text query ho** (chahe image ho ya na ho) → API call hoti hai
  
- **API call nahi hoti jab:**
  - **Sirf non-medical text query ho** (jaise "Hello", "How are you") → API call nahi hoti, simple message show hota hai

- **Jab API call hoti hai, to API ko yeh information milti hai:**
  1. **Model ka output** (agar image upload hui aur model ka result mila to - text format mein):
     - Example: "Chest X-ray Analysis: pneumonia (confidence: 85%)"
     - Ya: "Skin Disease Analysis: Melanoma (confidence: 92%)"
  2. **User ka text query** (agar symptoms describe kiye hain):
     - Example: "Mujhe 3 din se cough hai aur chest pain ho raha hai"
  3. **Original image** (agar image upload hui ho - API khud bhi image dekh sakta hai)

#### **Stage 4: API Analysis & Final Result**
- API **sab kuch analyze karke** final response generate karta hai:
  - Model ka output + User ke symptoms + Original image - **teeno ko combine karke**
  - Agar model ka result sahi hai → API use enhance karke detailed explanation deta hai
  - Agar model ka result galat hai → API khud image dekhkar correct analysis deta hai
  - Agar image type unknown hai → API directly image analyze karta hai
- API detailed response deta hai:
  - Disease diagnosis
  - Treatment suggestions
  - Medication recommendations
  - Conclusion

#### **Summary Flow:**
```
Image Upload 
  ↓
Image Type Detect (Chest X-ray / Skin Disease / Unknown)
  ↓
Agar Match → Corresponding Model Analyze → Model Output (Text)
  ↓
Model Output + Text Symptoms + Original Image → Gemini API
  ↓
API Final Analysis → Result Generate
```

### **Step 2: Text Query Hone Par**

**Important:** Agar image bhi upload hui ho, to API call hamesha hoti hai (Step 1 follow hota hai). Yeh section sirf text-only queries ke liye hai.

1. **Pehle Check Hota Hai:**
   - Kya aapki query medical/symptom related hai?
   - `symptom_detector.py` file yeh check karti hai

2. **Agar Medical/Symptom Query Hai:**
   - Google Gemini API ko bheja jata hai
   - API detailed diagnosis aur treatment suggest karta hai
   - **API call hoti hai**

3. **Agar Non-Medical Query Hai (Sirf Text, No Image):**
   - Simple message show hota hai ke yeh sirf medical queries ke liye hai
   - **API call nahi hoti** (kyunki non-medical query hai aur koi image bhi nahi hai)

## 📁 Files Aur Unka Kaam

### **Main Application Files:**

1. **`app.py`** - Main file hai
   - Web application start karta hai
   - User login/signup handle karta hai
   - Image upload aur chat messages receive karta hai
   - Frontend ko responses bhejta hai

2. **`api_connection.py`** - Sabse important file
   - **Yeh decide karta hai ke model use karna hai ya API**
   - Local models se pehle try karta hai
   - Agar model fail ho jaye to API call karta hai
   - Saari logic yahi manage hoti hai

3. **`image_analyzer.py`** - Image analysis ke liye
   - Do models load karta hai:
     - `pneumonia_classification_model.h5` - Chest X-ray ke liye
     - `skin_disease_final_model_2.h5` - Skin disease ke liye
   - Images ko process karke analysis deta hai
   - Agar model load nahi ho paya, error return karta hai

4. **`api_handler.py`** - Google Gemini API ke liye
   - Gemini API ko connect karta hai
   - API calls handle karta hai
   - Responses receive karta hai

5. **`symptom_detector.py`** - Query check karne ke liye
   - Check karta hai ke user ki query medical hai ya nahi
   - Medical keywords detect karta hai (pain, fever, cough, etc.)

6. **`prompt_builder.py`** - API ke liye prompts banata hai
   - Medical queries ke liye structured prompts banata hai
   - API ko sahi format mein query bhejta hai

7. **`response_parser.py`** - API responses ko parse karta hai
   - API se aaye responses ko structured format mein convert karta hai
   - Disease, medication, conclusion extract karta hai

### **Database Files:**

8. **`db_manager.py`** - Database setup ke liye
   - MySQL connection banata hai
   - Database tables create karta hai (users, chat_threads, posts, structured_responses)

9. **`user_db_operations.py`** - Database operations ke liye
   - User registration/login handle karta hai
   - Chat threads create/delete karta hai
   - Messages save karta hai
   - Chat history retrieve karta hai

10. **`config.py`** - Settings ke liye
    - Database credentials store karta hai
    - API keys store karta hai
    - Configuration settings

### **Frontend Files:**

11. **`templates/`** - HTML pages
    - `login.html` - Login page
    - `signup.html` - Registration page
    - `main.html` - Main chat interface
    - `sidebar_threads.html` - Chat threads sidebar

12. **`static/css/style.css`** - Styling
13. **`static/js/`** - JavaScript files
    - `login.js` - Login functionality
    - `signup.js` - Signup functionality
    - `main.js` - Chat functionality

## 🗄️ Database Setup (MySQL)

### **Step 1: MySQL Install Karein**
- MySQL server install karein (agar nahi hai)
- MySQL server ko start karein

### **Step 2: Database Create Karein**
MySQL command line ya MySQL Workbench mein yeh command run karein:

```sql
CREATE DATABASE chatbot;
```

### **Step 3: Database Credentials Update Karein**
`config.py` file mein apne MySQL credentials update karein:

```python
MYSQL_HOST = "localhost"  # Ya aapka MySQL server address
MYSQL_USER = "root"        # Aapka MySQL username
MYSQL_PASSWORD = "your_password"  # Aapka MySQL password
MYSQL_DB = "chatbot"      # Database name
```

### **Step 4: Tables Automatically Create Honge**
Jab aap `app.py` run karenge, tables automatically create ho jayenge:
- `users` - User accounts ke liye
- `chat_threads` - Chat conversations ke liye
- `posts` - Messages ke liye
- `structured_responses` - Medical responses ke liye

## 🔑 API Setup (Google Gemini)

### **Step 1: API Key Leni Hai**
1. Google AI Studio (https://makersuite.google.com/app/apikey) par jayein
2. Apna Google account se login karein
3. "Create API Key" button click karein
4. API key copy karein

### **Step 2: API Key Set Karein**
`config.py` file mein API key add karein:

```python
GEMINI_API_KEY = "aapki-api-key-yahan"
```

Ya environment variable set karein:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="aapki-api-key-yahan"

# Windows CMD
set GEMINI_API_KEY=aapki-api-key-yahan
```

## 🚀 Installation & Setup

### **Step 1: Dependencies Install Karein**
```bash
pip install -r requirements.txt
```

### **Step 2: Application Run Karein**
```bash
python app.py
```

### **Step 3: Browser Mein Open Karein**
```
http://localhost:5000
```

## 🔄 Kaise Kaam Karta Hai - Complete Flow

### **Scenario 1: Image Upload (Chest X-ray) with Text Symptoms**

**Step-by-Step Flow:**
1. **Image Type Detection:**
   - User chest X-ray image upload karta hai
   - `image_analyzer.py` image ko analyze karke type detect karta hai → **"chest_xray"** detect hota hai

2. **Model Analysis:**
   - `pneumonia_classification_model.h5` model load hota hai
   - Model image ko analyze karta hai
   - Model ka output text format mein milta hai: **"Chest X-ray Analysis: pneumonia (confidence: 85%)"**

3. **API Call with Combined Data:**
   - **Model ka output (text)** + **User ke text symptoms** (agar hain) + **Original image** → **Gemini API ko bheje jate hain**
   - Example: API ko milta hai:
     - Model output: "Chest X-ray Analysis: pneumonia (confidence: 85%)"
     - User symptoms: "Mujhe 3 din se cough hai aur chest pain ho raha hai"
     - Original image: (actual image file)

4. **API Final Analysis:**
   - API teeno ko combine karke analyze karta hai
   - Model ka result verify karta hai aur image bhi khud dekhkar check karta hai
   - Final detailed response generate karta hai (disease, treatment, medication)

5. **Response Display:**
   - Response user ko show hota hai aur database mein save hota hai

**Note:** Agar model load nahi hua, to bhi API ko original image + text symptoms bheje jate hain, API directly analyze karta hai.

---

### **Scenario 2: Image Upload (Skin Disease) with Text Symptoms**

**Step-by-Step Flow:**
1. **Image Type Detection:**
   - User skin disease photo upload karta hai
   - `image_analyzer.py` image ko analyze karke type detect karta hai → **"skin_disease"** detect hota hai

2. **Model Analysis:**
   - `skin_disease_final_model_2.h5` model load hota hai
   - Model image ko analyze karta hai
   - Model ka output text format mein milta hai: **"Skin Disease Analysis: Melanoma (confidence: 92%)"**

3. **API Call with Combined Data:**
   - **Model ka output (text)** + **User ke text symptoms** (agar hain) + **Original image** → **Gemini API ko bheje jate hain**
   - Example: API ko milta hai:
     - Model output: "Skin Disease Analysis: Melanoma (confidence: 92%)"
     - User symptoms: "Yeh mole 2 mahine se badh raha hai aur itch ho raha hai"
     - Original image: (actual image file)

4. **API Final Analysis:**
   - API teeno ko combine karke analyze karta hai
   - Model ka result verify karta hai aur image bhi khud analyze karta hai
   - Final detailed response generate karta hai

5. **Response Display:**
   - Response user ko show hota hai aur database mein save hota hai

**Note:** Agar model load nahi hua, to bhi API ko original image + text symptoms bheje jate hain, API directly analyze karta hai.

---

### **Scenario 2.5: Image Upload (Other Types - CT Scan, MRI, Ultrasound, etc.)**

**Step-by-Step Flow:**
1. **Image Type Detection:**
   - User koi aur medical image upload karta hai (CT scan, MRI, ultrasound, etc.)
   - `image_analyzer.py` image ko analyze karke type detect karta hai → **"unknown"** detect hota hai

2. **Model Analysis (Optional):**
   - System dono models try karta hai (optional)
   - Lekin yeh models CT scan/MRI ke liye trained nahi hain
   - Model output mil sakta hai ya nahi - koi problem nahi

3. **API Call (Hamesha Hoti Hai):**
   - **Model ka output (agar mila to)** + **User ke text symptoms** (agar hain) + **Original image** → **Gemini API ko bheje jate hain**
   - API ko hamesha original image milti hai (yeh zaroori hai)
   - Model ka result (agar mila to) sirf hint ke taur par hota hai

4. **API Direct Analysis:**
   - API directly image ko analyze karta hai (kyunki yeh CT scan/MRI hai, models ke liye nahi)
   - Model ka result ignore kar sakta hai (agar galat ya irrelevant hai)
   - Complete independent analysis karta hai
   - Detailed explanation deta hai ke image mein kya dikh raha hai

5. **Response Display:**
   - Response user ko show hota hai aur database mein save hota hai

### **Scenario 3: Text Query (Medical)**
1. User medical query type karta hai (e.g., "Mujhe 3 din se fever hai")
2. `symptom_detector.py` check karta hai - medical query hai
3. `prompt_builder.py` structured prompt banata hai
4. Gemini API ko query bheji jati hai
5. API detailed response deta hai (disease, treatment, medication)
6. Response user ko show hota hai aur database mein save hota hai

### **Scenario 4: Text Query (Non-Medical)**
1. User non-medical query type karta hai (e.g., "Hello")
2. `symptom_detector.py` check karta hai - medical query nahi hai
3. Simple message show hota hai ke yeh sirf medical queries ke liye hai
4. API call nahi hota

## 📊 Models Ka Details

### **1. Pneumonia Classification Model**
- **File:** `pneumonia_classification_model.h5`
- **Kaam:** Chest X-ray images ko analyze karke pneumonia detect karta hai
- **Output:** Normal ya Pneumonia (confidence percentage ke saath)
- **Agar Load Nahi Hua:** Gemini API se analysis hota hai

### **2. Skin Disease Classification Model**
- **File:** `skin_disease_final_model_2.h5`
- **Kaam:** Skin disease images ko analyze karke disease classify karta hai
- **Output:** Disease name (Actinic Keratosis, Basal Cell Carcinoma, etc.) confidence ke saath
- **Agar Load Nahi Hua:** Gemini API se analysis hota hai

## ⚠️ Important Notes

1. **Models Optional Hain:**
   - Agar models load nahi hote, tab bhi application kaam karega
   - Gemini API se direct analysis ho jayega

2. **API Call Rules:**
   - **API call hoti hai jab:**
     - Image upload hui ho (hamesha API call hoti hai, chahe text query ho ya na ho)
     - Symptom-based text query ho (hamesha API call hoti hai, chahe image ho ya na ho)
   - **API call nahi hoti jab:**
     - Sirf non-medical text query ho (jaise "Hello", "How are you") aur koi image bhi nahi ho
   - **Model ka result (agar mila to) hamesha Gemini API ko bheja jata hai verification ke liye**
   - API model ka result + original image dono ko check karta hai
   - Agar model ka result galat hai, API khud correct analysis deta hai
   - Model ka result sirf "hint" hota hai, final decision API leta hai

3. **Other Image Types Handling:**
   - Agar image chest X-ray ya skin disease ke alawa koi aur type ki hai (CT scan, MRI, ultrasound, etc.)
   - System automatically dono models try karta hai
   - Jis model ka confidence zyada hota hai, uska result use hota hai
   - Lekin **Gemini API hamesha image ko khud bhi analyze karta hai**
   - API independent analysis karke final result deta hai
   - **Yani kisi bhi type ki medical image upload kar sakte hain, system handle kar lega**

4. **API Key Zaroori Hai:**
   - Gemini API key ke bina application kaam nahi karega
   - API key `config.py` mein set karni hogi

5. **Database Zaroori Hai:**
   - MySQL database setup karna zaroori hai
   - Credentials `config.py` mein update karne honge

6. **Medical Disclaimer:**
   - Yeh application sirf informational purposes ke liye hai
   - Professional doctor ki jagah nahi le sakta
   - Serious medical issues ke liye doctor se consult karein

## 🛠️ Troubleshooting

### **Problem: Models Load Nahi Ho Rahe**
- **Solution:** Koi problem nahi, Gemini API automatically use ho jayega
- Models optional hain, API se kaam chal jayega

### **Problem: Database Connection Error**
- **Solution:** Check karein:
  - MySQL server running hai ya nahi
  - `config.py` mein credentials sahi hain ya nahi
  - Database `chatbot` create hua hai ya nahi

### **Problem: API Error**
- **Solution:** Check karein:
  - API key sahi hai ya nahi
  - Internet connection hai ya nahi
  - API quota exceed to nahi hua

## 📝 Summary - Complete Flow

### **Image Upload Flow (Organized Way):**

1. **Image Type Detection (Pehle Yeh):**
   - System pehle image ko analyze karke type detect karta hai
   - Types: Chest X-ray / Skin Disease / Unknown

2. **Model Analysis (Agar Type Match Kare):**
   - Agar Chest X-ray → `pneumonia_classification_model.h5` analyze karta hai
   - Agar Skin Disease → `skin_disease_final_model_2.h5` analyze karta hai
   - Model ka output text format mein milta hai

3. **API Call:**
   - **API call tab hoti hai jab:**
     - Image upload hui ho (hamesha API call hoti hai)
     - Ya symptom-based text query ho (hamesha API call hoti hai)
   - **API call nahi hoti jab:**
     - Sirf non-medical text query ho (no image)
   - **Jab API call hoti hai:**
     - **Model ka output (text)** + **Text Symptoms** (agar hain) + **Original Image** → **Gemini API**
     - API teeno ko combine karke analyze karta hai
     - Final detailed response generate karta hai

4. **Result Display & Save:**
   - Response user ko show hota hai
   - Database mein save hota hai

### **Key Points:**
- ✅ **Image type pehle detect hoti hai** - phir corresponding model use hota hai
- ✅ **Model output text format mein** API ko bheja jata hai
- ✅ **API call hoti hai jab:** Image upload hui ho YA symptom query ho
- ✅ **API call nahi hoti:** Sirf non-medical text query (no image)
- ✅ **Model output + Text Symptoms + Original Image** - teeno API ko milte hain (jab API call hoti hai)
- ✅ **API final decision leta hai** - model ka result verify karke

### **Complete Flow Diagram:**
```
Image Upload
  ↓
Image Type Detect (Chest X-ray / Skin Disease / Unknown)
  ↓
Agar Match → Corresponding Model Analyze
  ↓
Model Output (Text) + Text Symptoms + Original Image
  ↓
Gemini API (Hamesha Call Hoti Hai)
  ↓
API Final Analysis & Response Generate
  ↓
Display & Database Save
```

---

**Built with ❤️ for better healthcare accessibility**
