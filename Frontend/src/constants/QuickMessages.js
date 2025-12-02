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

export const appointmentTests = [
  // Standard appointment requests
  { 
    text: '📅 General Checkup', 
    message: 'I need to schedule a general checkup appointment for next Monday at 9 AM. My name is John Smith, phone: 0123456789.',
    category: 'standard'
  },
  { 
    text: '🦷 Dental Checkup', 
    message: 'Can I book a dental checkup? I\'m available Tuesday afternoon, around 2 PM. Name: Sarah Johnson, phone: 0987654321.',
    category: 'standard'
  },
  { 
    text: '💉 Vaccination', 
    message: 'I want to get my flu vaccine. Can we schedule for December 15th at 10:30 AM? My name is Michael Lee, phone: 0912345678.',
    category: 'standard'
  },
  { 
    text: '🩺 Follow-up Visit', 
    message: 'Need to schedule a follow-up appointment for my blood test results. Next Friday morning would be great. Name: Emily Davis, phone: 0945678901.',
    category: 'standard'
  },
  
  // Urgent appointments
  { 
    text: '🚨 Urgent - Fever', 
    message: 'My child has high fever (39°C) for 2 days. Can we get an appointment today? ASAP please. Name: Linda Brown, phone: 0923456789.',
    category: 'urgent'
  },
  { 
    text: '⚠️ Urgent - Injury', 
    message: 'I hurt my ankle badly, it\'s very swollen. Need to see a doctor soon. Can you fit me in today? Name: David Wilson, phone: 0934567890.',
    category: 'urgent'
  },
  { 
    text: '🤒 Same Day - Sick', 
    message: 'I feel very sick with flu symptoms. Is there any available slot today or tomorrow? Name: Rachel Martinez, phone: 0956789012.',
    category: 'urgent'
  },
  
  // Incomplete information (testing chatbot's ability to ask follow-up questions)
  { 
    text: '📅 Missing Time', 
    message: 'I need an appointment next week for a checkup. My name is Tom Anderson, phone: 0967890123.',
    category: 'incomplete'
  },
  { 
    text: '📅 Missing Name', 
    message: 'Can I book an appointment for December 10th at 2 PM for a general checkup?',
    category: 'incomplete'
  },
  { 
    text: '📅 Missing Phone', 
    message: 'I\'d like to schedule a visit on Monday at 11 AM for my annual physical. Name is Jessica Taylor.',
    category: 'incomplete'
  },
  { 
    text: '📅 Missing Reason', 
    message: 'Hi, I want to make an appointment for next Wednesday at 3 PM. I\'m Chris Roberts, phone: 0978901234.',
    category: 'incomplete'
  },
  { 
    text: '📅 Vague Request', 
    message: 'I need to see a doctor sometime next week.',
    category: 'incomplete'
  },
  
  // Specific time requests
  { 
    text: '🕐 Morning Slot', 
    message: 'I need an early morning appointment, preferably 8 AM on Thursday. Routine checkup. Name: Kevin Zhang, phone: 0989012345.',
    category: 'time-specific'
  },
  { 
    text: '🕒 Lunch Time', 
    message: 'Can I get an appointment during lunch break, around 12-1 PM tomorrow? Name: Amy White, phone: 0990123456.',
    category: 'time-specific'
  },
  { 
    text: '🕔 After Work', 
    message: 'Do you have evening slots after 5 PM? I work during the day. Need checkup. Name: Brian Thompson, phone: 0901234567.',
    category: 'time-specific'
  },
  { 
    text: '🗓️ Weekend', 
    message: 'I can only come on weekends. Is Saturday morning available? General consultation. Name: Nancy Green, phone: 0912345670.',
    category: 'time-specific'
  },
  
  // Multiple people
  { 
    text: '👨‍👩‍👧 Family Appointment', 
    message: 'Can we book appointments for the whole family? 3 people - me, my wife, and daughter. December 20th around 10 AM. Name: Paul Harris, phone: 0923456701.',
    category: 'multiple'
  },
  { 
    text: '👶 Mother & Baby', 
    message: 'I need appointments for both me and my baby for checkup. Can we do back-to-back? Next Tuesday 9 AM. Name: Maria Garcia, phone: 0934567012.',
    category: 'multiple'
  },
  
  // Rescheduling
  { 
    text: '🔄 Reschedule', 
    message: 'I have an appointment on Monday but need to change it to Wednesday same time. Name: Robert Kim, phone: 0945678123.',
    category: 'reschedule'
  },
  { 
    text: '❌ Cancel & Rebook', 
    message: 'Need to cancel my Friday appointment and book for next week instead. Name: Jennifer Lopez, phone: 0956789234.',
    category: 'reschedule'
  },
  
  // Special requirements
  { 
    text: '👨‍⚕️ Specific Doctor', 
    message: 'I want to see Dr. Smith if possible. Next Thursday afternoon. General checkup. Name: Mark Taylor, phone: 0967890345.',
    category: 'special'
  },
  { 
    text: '🌐 Language Request', 
    message: 'I need an appointment with a Vietnamese-speaking doctor. Next week any day. Name: Nguyen Van A, phone: 0978901456.',
    category: 'special'
  },
  { 
    text: '♿ Accessibility', 
    message: 'I use a wheelchair. Do I need to mention this when booking? Want appointment Dec 12 at 10 AM. Name: Susan Clark, phone: 0989012567.',
    category: 'special'
  },
  
  // Vietnamese language
  { 
    text: '🇻🇳 Đặt Lịch Khám', 
    message: 'Tôi muốn đặt lịch khám tổng quát vào thứ 2 tuần sau lúc 9 giờ sáng. Tên: Trần Văn B, SĐT: 0990123678.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Khám Cho Con', 
    message: 'Con tôi cần khám bệnh gấp, con bị sốt. Có thể đặt lịch hôm nay không? Tên: Lê Thị C, SĐT: 0901234789.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Tái Khám', 
    message: 'Đặt lịch tái khám kết quả xét nghiệm. Thứ 6 này 2 giờ chiều được không? Tên: Phạm Văn D, SĐT: 0912345890.',
    category: 'vietnamese'
  },
  { 
    text: '🇻🇳 Hỏi Giờ Trống', 
    message: 'Thứ 4 tuần sau buổi sáng có giờ nào trống không ạ? Khám nội khoa. Tên: Hoàng Thị E, SĐT: 0923456901.',
    category: 'vietnamese'
  },
  
  // Edge cases
  { 
    text: '⏰ Very Early', 
    message: 'Can I get the first appointment of the day? Like 7 AM? Checkup. Name: William Brown, phone: 0934567012.',
    category: 'edge-case'
  },
  { 
    text: '🌙 Late Evening', 
    message: 'Do you have any slots after 7 PM? I work late. Name: Olivia Martinez, phone: 0945678123.',
    category: 'edge-case'
  },
  { 
    text: '📅 Far Future', 
    message: 'I want to book an appointment for March 2026. Annual physical. Name: Ethan Anderson, phone: 0956789234.',
    category: 'edge-case'
  },
  { 
    text: '🔜 Tomorrow', 
    message: 'Can I get in tomorrow? Any time works. Just need a quick consultation. Name: Sophia White, phone: 0967890345.',
    category: 'edge-case'
  },
  { 
    text: '📞 No Name Given', 
    message: 'Book me for Thursday 3 PM, general checkup, phone: 0978901456.',
    category: 'edge-case'
  },
  
  // Natural conversation style
  { 
    text: '💬 Casual Style', 
    message: 'Hey, can you squeeze me in sometime next week? Need to get my knee checked. Name\'s Alex Johnson, call me at 0989012567.',
    category: 'natural'
  },
  { 
    text: '💬 Polite Formal', 
    message: 'Good morning. I would like to request an appointment for a health screening. Would December 18th at 10:00 AM be available? My name is Dr. Richard Lee, contact: 0990123678.',
    category: 'natural'
  },
  { 
    text: '💬 Brief', 
    message: 'Appointment Dec 15, 2pm, checkup. John Doe, 0901234789.',
    category: 'natural'
  }
];