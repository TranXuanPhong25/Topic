const quickMessages = [
    { text: '🕐 Hours', message: 'What are your hours?' },
    { text: '📍 Location', message: 'Where are you located?' },
    { text: '💳 Insurance', message: 'Do you accept insurance?' },
    { text: '📅 Book Appointment', message: 'I need to schedule an appointment' },
    { text: '🏥 Services', message: 'What services do you offer?' },
    { text: '💰 Pricing', message: 'How much does a visit cost?' },
    { text: '👨‍⚕️ Doctors', message: 'What doctors are available?' },
    { text: '📞 Contact', message: 'How can I contact you?' },
    { text: '🚗 Parking', message: 'Is parking available?' },
    { text: '♿ Accessibility', message: 'Is the clinic wheelchair accessible?' },
    { text: '🌐 Languages', message: 'What languages do you speak?' },
    { text: '📋 New Patient', message: 'I am a new patient. What do I need to bring?' },
    { text: '💉 Vaccinations', message: 'Do you provide vaccinations?' },
    { text: '🧪 Lab Tests', message: 'Can I get lab tests done at your clinic?' },
    { text: '🩺 Telemedicine', message: 'Do you offer online consultations?' },
    { text: '⏰ Emergency', message: 'Do you handle emergencies?' },
    { text: '👶 Pediatrics', message: 'Do you see children?' },
    { text: '🤰 Pregnancy', message: 'Do you offer prenatal care?' },
    { text: '🔄 Reschedule', message: 'I need to reschedule my appointment' },
    { text: '❌ Cancel', message: 'I need to cancel my appointment' },
    { text: '📄 Medical Records', message: 'How do I get my medical records?' },
    { text: '💊 Prescriptions', message: 'Can I get a prescription refill?' },
    { text: '🏃 Sports Physical', message: 'Do you do sports physicals?' },
    { text: '✈️ Travel Medicine', message: 'Do you offer travel consultations?' }
  ];

export { quickMessages };

export const imageActions = [
  { 
    text: '📸 Vitiligo Sample', 
    imagePath: '/src/public/12419-vitiligo.jpg',
    message: 'Please analyze this vitiligo (bạch biến) image and provide diagnosis'
  },
  { 
    text: '📸 Jaundice Sample', 
    imagePath: '/src/public/350--trieu-chung-vang-da-la-dau-hieu-cua-nhung-benh-gi1_41181.jpg',
    message: 'My hand looks like this. What could be the issue?'
  },
  { 
    text: '📸 Skin Rash', 
    imagePath: '/src/public/rash-sample.jpg',
    message: 'I have this rash on my arm for 3 days. What could it be?'
  },
  { 
    text: '📸 Mole Check', 
    imagePath: '/src/public/mole-sample.jpg',
    message: 'This mole has been changing color and size. Should I be concerned?'
  },
  { 
    text: '📸 Acne Problem', 
    imagePath: '/src/public/acne-sample.jpg',
    message: 'I have severe acne. What treatment do you recommend?'
  },
  { 
    text: '📸 Eczema', 
    imagePath: '/src/public/eczema-sample.jpg',
    message: 'My skin is very dry, itchy and red. Is this eczema?'
  }
];

export const symptomTests = [
  // Common symptoms
  { 
    text: '🤒 Fever & Headache', 
    message: 'I have a high fever (39°C), severe headache, and body aches for 3 days. What could this be?',
    category: 'common'
  },
  { 
    text: '🤧 Cold Symptoms', 
    message: 'I have runny nose, sore throat, sneezing, and mild cough for 2 days. What should I do?',
    category: 'common'
  },
  { 
    text: '😷 COVID-19 Symptoms', 
    message: 'I have fever, dry cough, loss of taste and smell, and fatigue. Could this be COVID-19?',
    category: 'common'
  },
  { 
    text: '🤢 Nausea & Vomiting', 
    message: 'I have been experiencing nausea, vomiting, and diarrhea since last night. What might be the cause?',
    category: 'common'
  },
  { 
    text: '💔 Chest Pain', 
    message: 'I feel chest pain and shortness of breath when exercising. Should I be concerned?',
    category: 'common'
  },
  { 
    text: '🩸 Diabetes Symptoms', 
    message: 'I have excessive thirst, frequent urination, and unexplained weight loss. Could this be diabetes?',
    category: 'common'
  },
  
  // Emergency symptoms
  { 
    text: '🚨 Severe Chest Pain', 
    message: 'Sudden severe chest pain radiating to left arm, sweating, difficulty breathing. Male 55 years old.',
    category: 'emergency'
  },
  { 
    text: '🧠 Stroke Symptoms', 
    message: 'Sudden weakness on right side, slurred speech, facial drooping. Started 30 minutes ago.',
    category: 'emergency'
  },
  { 
    text: '🤕 Severe Allergic Reaction', 
    message: 'Throat swelling, difficulty breathing, hives after eating peanuts 10 minutes ago.',
    category: 'emergency'
  },
  
  // Chronic conditions
  { 
    text: '💊 High Blood Pressure', 
    message: 'Blood pressure consistently 150/95, headaches, dizziness. Family history of heart disease.',
    category: 'chronic'
  },
  { 
    text: '🫁 Asthma Attack', 
    message: 'Wheezing, chest tightness, shortness of breath. Inhaler not helping much.',
    category: 'chronic'
  },
  { 
    text: '🦴 Joint Pain', 
    message: 'Pain and stiffness in knees and hands, worse in morning. Getting worse over months.',
    category: 'chronic'
  },
  
  // Digestive issues
  { 
    text: '🤢 Food Poisoning', 
    message: 'Severe stomach cramps, vomiting, diarrhea after eating seafood last night.',
    category: 'digestive'
  },
  { 
    text: '🔥 Heartburn', 
    message: 'Burning sensation in chest, especially after meals and at night. Happens frequently.',
    category: 'digestive'
  },
  { 
    text: '💩 Constipation', 
    message: 'Haven\'t had bowel movement for 5 days, abdominal pain, bloating.',
    category: 'digestive'
  },
  
  // Women's health
  { 
    text: '👩 Irregular Periods', 
    message: 'Very irregular periods, heavy bleeding, severe cramps. Age 28.',
    category: 'womens-health'
  },
  { 
    text: '🤰 Pregnancy Symptoms', 
    message: 'Missed period, morning sickness, fatigue. Positive home pregnancy test.',
    category: 'womens-health'
  },
  { 
    text: '🌡️ Menopause Symptoms', 
    message: 'Hot flashes, night sweats, mood swings, irregular periods. Age 48.',
    category: 'womens-health'
  },
  
  // Mental health
  { 
    text: '😰 Anxiety', 
    message: 'Constant worry, racing heart, trouble sleeping, panic attacks. Affecting daily life.',
    category: 'mental-health'
  },
  { 
    text: '😔 Depression', 
    message: 'Feeling sad for weeks, no energy, lost interest in everything, trouble concentrating.',
    category: 'mental-health'
  },
  { 
    text: '😴 Insomnia', 
    message: 'Can\'t fall asleep, lying awake for hours. Exhausted during day. Ongoing for months.',
    category: 'mental-health'
  },
  
  // Pediatric
  { 
    text: '👶 Baby Fever', 
    message: 'My 8-month-old has fever 38.8°C, fussy, not eating well, pulling at ear.',
    category: 'pediatric'
  },
  { 
    text: '🤧 Child Cough', 
    message: 'My 5-year-old has persistent cough for 2 weeks, worse at night. No fever.',
    category: 'pediatric'
  },
  { 
    text: '🤮 Child Vomiting', 
    message: 'My child vomited 4 times today, diarrhea, looks pale and tired. Age 6.',
    category: 'pediatric'
  },
  { 
    text: '🦠 Hand Foot Mouth', 
    message: 'Child has fever, sores in mouth, rash on hands and feet. Daycare outbreak. Age 3.',
    category: 'pediatric'
  },
  
  // Respiratory
  { 
    text: '🫁 Shortness of Breath', 
    message: 'Difficulty breathing even at rest, chest tightness, wheezing. Getting worse.',
    category: 'respiratory'
  },
  { 
    text: '😷 Persistent Cough', 
    message: 'Dry cough for 4 weeks, worse at night, sometimes coughing up phlegm.',
    category: 'respiratory'
  },
  { 
    text: '🤧 Sinus Infection', 
    message: 'Facial pain, thick yellow/green nasal discharge, headache, fever for 10 days.',
    category: 'respiratory'
  },
  
  // Skin conditions
  { 
    text: '🔴 Severe Acne', 
    message: 'Painful acne on face, back and chest. Tried OTC products, not working. Scarring.',
    category: 'dermatology'
  },
  { 
    text: '🦠 Fungal Rash', 
    message: 'Itchy, red, circular rash spreading on leg. Looks like ringworm.',
    category: 'dermatology'
  },
  { 
    text: '🌞 Suspicious Mole', 
    message: 'Mole changing shape and color, irregular borders, bigger than 6mm. Should I worry?',
    category: 'dermatology'
  },
  
  // Injuries
  { 
    text: '🏀 Ankle Sprain', 
    message: 'Twisted ankle playing sports. Very swollen, can\'t walk on it, bruising.',
    category: 'injury'
  },
  { 
    text: '🔪 Deep Cut', 
    message: 'Cut hand with knife, deep cut, bleeding controlled. Happened 3 hours ago. Need stitches?',
    category: 'injury'
  },
  { 
    text: '🔥 Burn Injury', 
    message: 'Burned hand on hot pan. Red, blistering, very painful. What should I do?',
    category: 'injury'
  },
  
  // Vietnamese language
  { 
    text: '🇻🇳 Sốt Cao', 
    message: 'Con tôi bị sốt 39 độ, ho nhiều, khó thở. Bé 4 tuổi, sốt được 3 ngày rồi.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Đau Bụng', 
    message: 'Đau bụng quặn thắt, tiêu chảy, buồn nôn từ tối qua. Ăn hải sản hôm qua.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Đau Ngực', 
    message: 'Đau ngực dữ dội lan ra cánh tay, ra mồ hôi lạnh, khó thở. Nam 55 tuổi.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Dị Ứng', 
    message: 'Nổi mẩn đỏ khắp người, ngứa nhiều, sưng môi sau khi ăn tôm.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Đau Lưng', 
    message: 'Đau lưng dưới lan xuống chân, tê bì, khó cử động. Đau 2 tuần rồi.',
    category: 'vietnamese'
  },
  
  // Complex multi-symptom
  { 
    text: '🤒 Flu-like Illness', 
    message: 'Fever, chills, body aches, headache, sore throat, exhaustion for 4 days. Can\'t get out of bed.',
    category: 'complex'
  },
  { 
    text: '🦠 UTI Symptoms', 
    message: 'Painful urination, frequent urge to pee, lower abdominal pain, cloudy urine. Female 32.',
    category: 'complex'
  },
  { 
    text: '🤕 Migraine', 
    message: 'Severe one-sided headache, nausea, sensitivity to light and sound. Lasting 2 days.',
    category: 'complex'
  },
  
  // Senior health
  { 
    text: '👴 Memory Loss', 
    message: 'My father (75) is forgetting things frequently, confused, personality changes over months.',
    category: 'senior'
  },
  { 
    text: '💊 Multiple Medications', 
    message: 'Taking 8 medications daily, experiencing dizziness, confusion, falls. Age 80.',
    category: 'senior'
  },
  
  // Preventive & wellness
  { 
    text: '💪 Annual Checkup', 
    message: 'I\'m 40 years old. What health screenings should I get for my age?',
    category: 'prevention'
  },
  { 
    text: '💉 Vaccination', 
    message: 'Need to update my vaccinations. What vaccines do adults need?',
    category: 'prevention'
  },
  { 
    text: '🏃 Weight Management', 
    message: 'Need help losing weight. BMI 32, pre-diabetes, high cholesterol. Age 45.',
    category: 'wellness'
  }
];