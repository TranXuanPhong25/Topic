import sys
import os
import time
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BASE_URL}/ma/chat"

class PatientSimulator:
    def __init__(self, name, scenario):
        self.name = name
        self.scenario = scenario
        self.session_id = None
        self.history = []

    def run(self):
        print(f"--- Starting Simulation: {self.name} ---")
        print(f"Scenario: {self.scenario['description']}")
        
        for step in self.scenario['steps']:
            user_msg = step['user']
            print(f"\n👤 Patient: {user_msg}")
            
            # Send to API
            try:
                payload = {
                    "message": user_msg,
                    "session_id": self.session_id,
                    "chat_history": self.history
                }
                
                start_time = time.time()
                response = requests.post(CHAT_ENDPOINT, json=payload)
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    bot_msg = data['response']
                    self.session_id = data['session_id']
                    
                    print(f"🤖 Bot ({latency:.2f}s): {bot_msg}")
                    
                    # Update history (simplified)
                    self.history.append({"role": "user", "parts": [{"text": user_msg}]})
                    self.history.append({"role": "model", "parts": [{"text": bot_msg}]})
                    
                    # Basic validation
                    if 'expected_keywords' in step:
                        found_any = False
                        missing_keywords = []
                        for kw in step['expected_keywords']:
                            if kw.lower() in bot_msg.lower():
                                found_any = True
                            else:
                                missing_keywords.append(kw)
                        
                        if len(missing_keywords) == len(step['expected_keywords']):
                             print(f"⚠️ Warning: None of the expected keywords found: {step['expected_keywords']}")

                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    break
                    
            except requests.exceptions.ConnectionError:
                print("❌ Could not connect to server. Is it running?")
                break
            
            # Simulate reading time
            time.sleep(1)

# Define Scenarios
SCENARIOS = [
    {
        "description": "Routine Checkup Booking (Vietnamese)",
        "steps": [
            {"user": "Xin chào", "expected_keywords": ["giúp", "hỗ trợ", "hello"]},
            {"user": "Tôi muốn đặt lịch khám bệnh", "expected_keywords": ["ngày", "giờ"]},
            {"user": "Ngày mai lúc 9 giờ sáng", "expected_keywords": ["lý do", "triệu chứng", "tên"]},
            {"user": "Tôi tên là Nguyễn Văn A, sđt 0912345678. Tôi muốn khám tổng quát.", "expected_keywords": ["đặt lịch", "xác nhận", "thành công", "đã đặt"]}
        ]
    },
    {
        "description": "Emergency Scenario (Vietnamese)",
        "steps": [
            {"user": "Cứu tôi với", "expected_keywords": ["giúp", "hỗ trợ"]},
            {"user": "Tôi bị đau ngực dữ dội và khó thở", "expected_keywords": ["911", "cấp cứu", "khẩn cấp", "ngay lập tức"]}
        ]
    }
]

if __name__ == "__main__":
    print("Ensure the server is running on localhost:8000")
    
    # Run Scenario 1
    sim1 = PatientSimulator("Nguyen Van A", SCENARIOS[0])
    sim1.run()
    
    print("\n" + "="*30 + "\n")
    
    # Run Scenario 2
    sim2 = PatientSimulator("Tran Thi B", SCENARIOS[1])
    sim2.run()
