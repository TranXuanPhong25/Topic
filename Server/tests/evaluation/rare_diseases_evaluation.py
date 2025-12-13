import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add the Server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph

# Danh sách các bệnh hiếm gặp với triệu chứng đặc trưng
RARE_DISEASES_TEST_CASES = [
    {
        "disease": "Hội chứng Marfan",
        "symptoms": [
            "Tôi cao bất thường, tay chân dài và gầy",
            "Ngực lõm, xương sườn nổi bật",
            "Thị lực giảm, có thể có vấn đề về tim",
            "Da có vết rạn da, khớp linh hoạt quá mức"
        ],
        "expected_diagnoses": ["hội chứng marfan", "marfan syndrome", "bệnh di truyền mô liên kết"],
        "key_symptoms": ["cao bất thường", "tay chân dài", "ngực lõm", "khớp linh hoạt", "thị lực giảm"],
        "category": "bệnh di truyền"
    },
    {
        "disease": "Bệnh Addison",
        "symptoms": [
            "Tôi bị mệt mỏi kinh niên, yếu cơ",
            "Da tối màu bất thường, đặc biệt ở nếp gấp",
            "Giảm cân không rõ nguyên nhân",
            "Thèm ăn mặn, huyết áp thấp"
        ],
        "expected_diagnoses": ["addison", "suy thượng thận", "hypoadrenalism"],
        "key_symptoms": ["da tối màu", "mệt mỏi kinh niên", "thèm mặn", "huyết áp thấp"],
        "category": "bệnh nội tiết"
    },
    {
        "disease": "Hội chứng Sjögren",
        "symptoms": [
            "Mắt khô liên tục, cảm giác có cát trong mắt",
            "Miệng khô, khó nuốt thức ăn khô",
            "Khớp đau nhức, sưng khớp",
            "Mệt mỏi thường xuyên"
        ],
        "expected_diagnoses": ["sjögren", "khô miệng khô mắt", "bệnh tự miễn"],
        "key_symptoms": ["mắt khô", "miệng khô", "khớp đau", "mệt mỏi"],
        "category": "bệnh tự miễn dịch"
    },
    {
        "disease": "Bệnh Wilson",
        "symptoms": [
            "Vàng da, vàng mắt từ từ",
            "Run tay không kiểm soát được",
            "Khó nói, thay đổi tính cách",
            "Đau bụng, buồn nôn"
        ],
        "expected_diagnoses": ["wilson", "tích đồng", "hepatolenticular degeneration"],
        "key_symptoms": ["vàng da", "run tay", "khó nói", "thay đổi tính cách"],
        "category": "bệnh chuyển hóa"
    },
    {
        "disease": "Hội chứng Cushing",
        "symptoms": [
            "Mặt tròn như mặt trăng",
            "Tăng cân ở thân mình, tay chân gầy",
            "Vết rạn da tím ở bụng",
            "Cao huyết áp, tiểu đường"
        ],
        "expected_diagnoses": ["cushing", "thừa cortisol", "hypercortisolism"],
        "key_symptoms": ["mặt tròn", "vết rạn tím", "tăng cân thân mình"],
        "category": "bệnh nội tiết"
    },
    {
        "disease": "Xơ cứng teo cơ một bên (ALS)",
        "symptoms": [
            "Yếu cơ dần dần, bắt đầu từ tay hoặc chân",
            "Co giật cơ, chuột rút",
            "Nói khó, nuốt khó",
            "Thở khó dần"
        ],
        "expected_diagnoses": ["als", "xơ cứng teo cơ", "motor neuron disease"],
        "key_symptoms": ["yếu cơ dần", "co giật cơ", "nuốt khó", "thở khó"],
        "category": "bệnh thần kinh"
    },
    {
        "disease": "Hội chứng Ehlers-Danlos",
        "symptoms": [
            "Da rất mềm và co giãn được",
            "Khớp cực kỳ linh hoạt",
            "Da dễ tím, vết thương lâu lành",
            "Đau khớp mãn tính"
        ],
        "expected_diagnoses": ["ehlers-danlos", "eds", "bệnh mô liên kết"],
        "key_symptoms": ["da co giãn", "khớp linh hoạt", "da dễ tím"],
        "category": "bệnh di truyền"
    },
    {
        "disease": "Bệnh Ménière",
        "symptoms": [
            "Chóng mặt xoay quay dữ dội",
            "Ù tai một bên",
            "Giảm thính lực từng đợt",
            "Cảm giác đầy tai"
        ],
        "expected_diagnoses": ["ménière", "meniere", "bệnh tiền đình"],
        "key_symptoms": ["chóng mặt xoay", "ù tai", "giảm thính lực"],
        "category": "bệnh tai mũi họng"
    },
    {
        "disease": "Hội chứng PCOS (Buồng trứng đa nang)",
        "symptoms": [
            "Kinh nguyệt không đều hoặc mất kinh",
            "Lông mọc nhiều ở mặt và cơ thể",
            "Mụn trứng cá dai dẳng",
            "Tăng cân khó giảm"
        ],
        "expected_diagnoses": ["pcos", "buồng trứng đa nang", "polycystic ovary"],
        "key_symptoms": ["kinh không đều", "lông mọc nhiều", "mụn trứng cá"],
        "category": "bệnh phụ khoa"
    },
    {
        "disease": "Bệnh Hashimoto",
        "symptoms": [
            "Mệt mỏi, uể oải liên tục",
            "Tăng cân không kiểm soát",
            "Rụng tóc nhiều, da khô",
            "Cảm giác lạnh thường xuyên"
        ],
        "expected_diagnoses": ["hashimoto", "viêm tuyến giáp", "hypothyroid"],
        "key_symptoms": ["mệt mỏi", "tăng cân", "rụng tóc", "cảm giác lạnh"],
        "category": "bệnh nội tiết"
    }
]


class RareDiseasesEvaluator:
    def __init__(self):
        self.graph = MedicalDiagnosticGraph()
        self.results = []
        
    async def evaluate_single_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        disease_name = case["disease"]
        symptoms = case["symptoms"]
        expected_diagnoses = case["expected_diagnoses"]
        key_symptoms = case["key_symptoms"]
        
        print(f"\nĐánh giá bệnh: {disease_name}")
        print(f"Triệu chứng: {symptoms}")
        
        # Tạo input từ các triệu chứng
        user_input = ". ".join(symptoms)
        
        try:
            # Chạy phân tích
            result = await self.graph.analyze(
                user_input=user_input,
                image=None,
                chat_history=[]
            )
            
            response = result.get("final_response", "")
            success = result.get("success", False)
            
            if not success:
                return {
                    "disease": disease_name,
                    "category": case["category"],
                    "status": "error",
                    "response": response,
                    "diagnosis_accuracy": 0,
                    "symptom_recognition": 0,
                    "error": result.get("error", "Unknown error")
                }
            
            # Phân tích độ chính xác
            diagnosis_score = self._evaluate_diagnosis_accuracy(response, expected_diagnoses)
            symptom_score = self._evaluate_symptom_recognition(response, key_symptoms)
            
            evaluation_result = {
                "disease": disease_name,
                "category": case["category"],
                "status": "success",
                "response": response,
                "diagnosis_accuracy": diagnosis_score,
                "symptom_recognition": symptom_score,
                "overall_score": (diagnosis_score + symptom_score) / 2,
                "expected_diagnoses": expected_diagnoses,
                "key_symptoms": key_symptoms
            }
            
            print(f"Chẩn đoán: {diagnosis_score:.1f}/10")
            print(f"Nhận biết triệu chứng: {symptom_score:.1f}/10")
            print(f"Điểm tổng: {evaluation_result['overall_score']:.1f}/10")
            
            return evaluation_result
            
        except Exception as e:
            print(f"Lỗi: {str(e)}")
            return {
                "disease": disease_name,
                "category": case["category"],
                "status": "error",
                "response": "",
                "diagnosis_accuracy": 0,
                "symptom_recognition": 0,
                "error": str(e)
            }
    
    def _evaluate_diagnosis_accuracy(self, response: str, expected_diagnoses: List[str]) -> float:
        response_lower = response.lower()
        
        # Kiểm tra xem có chẩn đoán nào trùng khớp không
        matches = 0
        for diagnosis in expected_diagnoses:
            if diagnosis.lower() in response_lower:
                matches += 1
        
        if matches > 0:
            # Có ít nhất một chẩn đoán đúng
            base_score = 7.0
            
            # Bonus nếu có nhiều chẩn đoán liên quan
            if matches > 1:
                base_score += 1.5
            
            # Kiểm tra tính chi tiết của phản hồi
            if len(response) > 200:  # Phản hồi chi tiết
                base_score += 0.5
            if "chẩn đoán" in response_lower:
                base_score += 0.5
            if any(word in response_lower for word in ["khuyến nghị", "nên", "cần"]):
                base_score += 0.5
                
            return min(base_score, 10.0)
        else:
            # Không có chẩn đoán đúng
            # Kiểm tra xem có đề cập đến hệ thống cơ quan liên quan không
            if any(word in response_lower for word in ["tim", "phổi", "gan", "thận", "thần kinh", "nội tiết"]):
                return 3.0
            elif any(word in response_lower for word in ["bác sĩ", "khám", "xét nghiệm"]):
                return 2.0
            else:
                return 0.0
    
    def _evaluate_symptom_recognition(self, response: str, key_symptoms: List[str]) -> float:
        response_lower = response.lower()
        
        recognized_symptoms = 0
        for symptom in key_symptoms:
            # Tách từ khóa để tìm kiếm linh hoạt hơn
            symptom_words = symptom.lower().split()
            if len(symptom_words) == 1:
                if symptom_words[0] in response_lower:
                    recognized_symptoms += 1
            else:
                # Kiểm tra xem có ít nhất một nửa từ khóa xuất hiện không
                word_matches = sum(1 for word in symptom_words if word in response_lower)
                if word_matches >= len(symptom_words) / 2:
                    recognized_symptoms += 1
        
        # Tính điểm dựa trên tỷ lệ triệu chứng được nhận biết
        symptom_ratio = recognized_symptoms / len(key_symptoms)
        base_score = symptom_ratio * 8.0
        
        # Bonus nếu phản hồi thể hiện hiểu biết về mối liên hệ giữa các triệu chứng
        if any(word in response_lower for word in ["liên quan", "kết hợp", "cùng với"]):
            base_score += 1.0
        
        # Bonus nếu đề cập đến việc cần thêm thông tin
        if any(word in response_lower for word in ["thêm thông tin", "chi tiết hơn", "xét nghiệm"]):
            base_score += 1.0
        
        return min(base_score, 10.0)
    
    async def run_evaluation(self) -> Dict[str, Any]:
        print("Bắt đầu đánh giá chatbot với các bệnh hiếm gặp...")
        print(f"Tổng số ca test: {len(RARE_DISEASES_TEST_CASES)}")
        
        results = []
        
        for i, case in enumerate(RARE_DISEASES_TEST_CASES, 1):
            print(f"\n--- Test case {i}/{len(RARE_DISEASES_TEST_CASES)} ---")
            result = await self.evaluate_single_case(case)
            results.append(result)
            
            # Nghỉ giữa các test để tránh overload
            await asyncio.sleep(1)
        
        # Tính toán thống kê
        stats = self._calculate_statistics(results)
        
        # Tạo báo cáo
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_cases": len(RARE_DISEASES_TEST_CASES),
            "results": results,
            "statistics": stats
        }
        
        self._print_summary(stats)
        return report
    
    def _calculate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        successful_cases = [r for r in results if r["status"] == "success"]
        error_cases = [r for r in results if r["status"] == "error"]
        
        if not successful_cases:
            return {
                "success_rate": 0,
                "error_rate": 100,
                "avg_diagnosis_accuracy": 0,
                "avg_symptom_recognition": 0,
                "avg_overall_score": 0,
                "category_performance": {},
                "top_performing_diseases": [],
                "challenging_diseases": []
            }
        
        # Tính trung bình
        avg_diagnosis = sum(r["diagnosis_accuracy"] for r in successful_cases) / len(successful_cases)
        avg_symptom = sum(r["symptom_recognition"] for r in successful_cases) / len(successful_cases)
        avg_overall = sum(r["overall_score"] for r in successful_cases) / len(successful_cases)
        
        # Phân tích theo danh mục
        category_performance = {}
        for result in successful_cases:
            category = result["category"]
            if category not in category_performance:
                category_performance[category] = {
                    "count": 0,
                    "diagnosis_score": 0,
                    "symptom_score": 0,
                    "overall_score": 0
                }
            
            cat_perf = category_performance[category]
            cat_perf["count"] += 1
            cat_perf["diagnosis_score"] += result["diagnosis_accuracy"]
            cat_perf["symptom_score"] += result["symptom_recognition"] 
            cat_perf["overall_score"] += result["overall_score"]
        
        # Tính trung bình cho từng danh mục
        for category in category_performance:
            perf = category_performance[category]
            count = perf["count"]
            perf["avg_diagnosis"] = perf["diagnosis_score"] / count
            perf["avg_symptom"] = perf["symptom_score"] / count
            perf["avg_overall"] = perf["overall_score"] / count
        
        # Tìm bệnh có kết quả tốt nhất và khó nhất
        sorted_by_score = sorted(successful_cases, key=lambda x: x["overall_score"], reverse=True)
        top_performing = sorted_by_score[:3]
        challenging = sorted_by_score[-3:]
        
        return {
            "success_rate": len(successful_cases) / len(results) * 100,
            "error_rate": len(error_cases) / len(results) * 100,
            "avg_diagnosis_accuracy": avg_diagnosis,
            "avg_symptom_recognition": avg_symptom,
            "avg_overall_score": avg_overall,
            "category_performance": category_performance,
            "top_performing_diseases": [{"disease": r["disease"], "score": r["overall_score"]} for r in top_performing],
            "challenging_diseases": [{"disease": r["disease"], "score": r["overall_score"]} for r in challenging]
        }
    
    def _print_summary(self, stats: Dict[str, Any]):
        print("\n" + "="*60)
        print("TÓM TẮT KẾT QUẢ ĐÁNH GIÁ")
        print("="*60)
        
        print(f"Tỷ lệ thành công: {stats['success_rate']:.1f}%")
        print(f"Tỷ lệ lỗi: {stats['error_rate']:.1f}%")
        print(f"Điểm chẩn đoán trung bình: {stats['avg_diagnosis_accuracy']:.1f}/10")
        print(f"Điểm nhận biết triệu chứng: {stats['avg_symptom_recognition']:.1f}/10")
        print(f"Điểm tổng trung bình: {stats['avg_overall_score']:.1f}/10")
        
        print(f"\nHIỆU SUẤT THEO DANH MỤC:")
        for category, perf in stats['category_performance'].items():
            print(f"  • {category}: {perf['avg_overall']:.1f}/10 ({perf['count']} ca)")
        
        print(f"\nTOP 3 BỆNH ĐƯỢC CHẨN ĐOÁN TỐT NHẤT:")
        for i, disease in enumerate(stats['top_performing_diseases'], 1):
            print(f"  {i}. {disease['disease']}: {disease['score']:.1f}/10")
        
        print(f"\nTOP 3 BỆNH KHÓ CHẨN ĐOÁN NHẤT:")
        for i, disease in enumerate(stats['challenging_diseases'], 1):
            print(f"  {i}. {disease['disease']}: {disease['score']:.1f}/10")
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rare_diseases_evaluation_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\nBáo cáo đã được lưu: {filepath}")


async def main():
    evaluator = RareDiseasesEvaluator()
    
    try:
        report = await evaluator.run_evaluation()
        evaluator.save_report(report)
        
        print(f"\nĐánh giá hoàn thành!")
        print(f"Điểm tổng trung bình: {report['statistics']['avg_overall_score']:.1f}/10")
        
    except KeyboardInterrupt:
        print(f"\nĐánh giá bị dừng bởi người dùng")
    except Exception as e:
        print(f"\nLỗi trong quá trình đánh giá: {e}")


if __name__ == "__main__":
    asyncio.run(main())