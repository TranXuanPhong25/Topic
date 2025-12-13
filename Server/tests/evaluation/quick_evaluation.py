import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add the Server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.medical_diagnostic_graph import MedicalDiagnosticGraph

# Test cases với triệu chứng đơn giản
QUICK_TEST_CASES = [
    {
        "input": "Tôi bị đau đầu và sốt",
        "expected_keywords": ["đau đầu", "sốt", "paracetamol", "nghỉ ngơi"],
        "category": "triệu chứng thường gặp"
    },
    {
        "input": "Tôi ho và có đờm",
        "expected_keywords": ["ho", "đờm", "hô hấp", "uống nước"],
        "category": "triệu chứng hô hấp"
    },
    {
        "input": "Bụng tôi đau và tiêu chảy",
        "expected_keywords": ["đau bụng", "tiêu chảy", "tiêu hóa", "nước"],
        "category": "triệu chứng tiêu hóa"
    },
    {
        "input": "Da tôi nổi mẩn đỏ và ngứa",
        "expected_keywords": ["mẩn đỏ", "ngứa", "da", "dị ứng"],
        "category": "triệu chứng da liễu"
    },
    {
        "input": "Tôi chóng mặt và buồn nôn",
        "expected_keywords": ["chóng mặt", "buồn nôn", "tiền đình", "nghỉ ngơi"],
        "category": "triệu chứng thần kinh"
    },
    {
        "input": "Tim tôi đập nhanh và khó thở",
        "expected_keywords": ["tim đập nhanh", "khó thở", "tim mạch", "bác sĩ"],
        "category": "triệu chứng tim mạch"
    },
    {
        "input": "Tôi đi tiểu buồt và có máu",
        "expected_keywords": ["tiểu buồt", "máu", "tiết niệu", "nhiễm trùng"],
        "category": "triệu chứng tiết niệu"
    },
    {
        "input": "Mắt tôi đỏ và chảy nước mắt",
        "expected_keywords": ["mắt đỏ", "nước mắt", "viêm", "mắt"],
        "category": "triệu chứng mắt"
    },
    {
        "input": "Tai tôi đau và ù tai",
        "expected_keywords": ["tai đau", "ù tai", "tai", "viêm"],
        "category": "triệu chứng tai mũi họng"
    },
    {
        "input": "Tôi mất ngủ và lo lắng",
        "expected_keywords": ["mất ngủ", "lo lắng", "tâm lý", "thư giãn"],
        "category": "triệu chứng tâm lý"
    }
]


class QuickEvaluator:
    def __init__(self):
        self.graph = MedicalDiagnosticGraph()
        
    async def evaluate_single_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        user_input = case["input"]
        expected_keywords = case["expected_keywords"]
        category = case["category"]
        
        print(f"\nTest: {user_input}")
        
        try:
            result = await self.graph.analyze(
                user_input=user_input,
                image=None,
                chat_history=[]
            )
            
            response = result.get("final_response", "")
            success = result.get("success", False)
            
            if not success:
                return {
                    "input": user_input,
                    "category": category,
                    "status": "error",
                    "response": response,
                    "score": 0,
                    "keywords_found": [],
                    "error": result.get("error", "Unknown error")
                }
            
            # Đánh giá response
            score, keywords_found = self._evaluate_response(response, expected_keywords)
            
            evaluation_result = {
                "input": user_input,
                "category": category,
                "status": "success",
                "response": response,
                "score": score,
                "keywords_found": keywords_found,
                "expected_keywords": expected_keywords
            }
            
            print(f"Điểm: {score:.1f}/10")
            print(f"Keywords tìm thấy: {len(keywords_found)}/{len(expected_keywords)}")
            
            return evaluation_result
            
        except Exception as e:
            print(f"Lỗi: {str(e)}")
            return {
                "input": user_input,
                "category": category,
                "status": "error",
                "response": "",
                "score": 0,
                "keywords_found": [],
                "error": str(e)
            }
    
    def _evaluate_response(self, response: str, expected_keywords: List[str]) -> tuple:
        response_lower = response.lower()
        keywords_found = []
        
        for keyword in expected_keywords:
            if keyword.lower() in response_lower:
                keywords_found.append(keyword)
        
        # Tính điểm cơ bản dựa trên keywords
        keyword_ratio = len(keywords_found) / len(expected_keywords)
        base_score = keyword_ratio * 6.0
        
        # Bonus points
        if len(response) > 100:  # Response chi tiết
            base_score += 1.0
        if any(word in response_lower for word in ["nên", "khuyến nghị", "cần"]):
            base_score += 1.0
        if any(word in response_lower for word in ["bác sĩ", "khám", "kiểm tra"]):
            base_score += 1.0
        if any(word in response_lower for word in ["nghỉ ngơi", "uống nước", "thuốc"]):
            base_score += 1.0
        
        return min(base_score, 10.0), keywords_found
    
    async def run_quick_evaluation(self) -> Dict[str, Any]:
        print("Bắt đầu đánh giá nhanh chatbot...")
        print(f"Tổng số ca test: {len(QUICK_TEST_CASES)}")
        
        results = []
        
        for i, case in enumerate(QUICK_TEST_CASES, 1):
            print(f"\n--- Test case {i}/{len(QUICK_TEST_CASES)} ---")
            result = await self.evaluate_single_case(case)
            results.append(result)
            
            # Nghỉ ngắn giữa các test
            await asyncio.sleep(0.5)
        
        # Tính thống kê
        stats = self._calculate_statistics(results)
        
        # Tạo báo cáo
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "quick_evaluation",
            "total_cases": len(QUICK_TEST_CASES),
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
                "avg_score": 0,
                "category_performance": {}
            }
        
        avg_score = sum(r["score"] for r in successful_cases) / len(successful_cases)
        
        # Phân tích theo danh mục
        category_performance = {}
        for result in successful_cases:
            category = result["category"]
            if category not in category_performance:
                category_performance[category] = {"scores": [], "count": 0}
            
            category_performance[category]["scores"].append(result["score"])
            category_performance[category]["count"] += 1
        
        # Tính trung bình cho từng danh mục
        for category in category_performance:
            scores = category_performance[category]["scores"]
            category_performance[category]["avg_score"] = sum(scores) / len(scores)
        
        return {
            "success_rate": len(successful_cases) / len(results) * 100,
            "error_rate": len(error_cases) / len(results) * 100,
            "avg_score": avg_score,
            "category_performance": category_performance,
            "total_keywords_expected": sum(len(r["expected_keywords"]) for r in successful_cases),
            "total_keywords_found": sum(len(r["keywords_found"]) for r in successful_cases)
        }
    
    def _print_summary(self, stats: Dict[str, Any]):
        print("\n" + "="*50)
        print("TÓM TẮT ĐÁNH GIÁ NHANH")
        print("="*50)
        
        print(f"Tỷ lệ thành công: {stats['success_rate']:.1f}%")
        print(f"Tỷ lệ lỗi: {stats['error_rate']:.1f}%")
        print(f"Điểm trung bình: {stats['avg_score']:.1f}/10")
        
        if 'total_keywords_expected' in stats and 'total_keywords_found' in stats:
            keyword_rate = stats['total_keywords_found'] / stats['total_keywords_expected'] * 100
            print(f"Tỷ lệ nhận biết keywords: {keyword_rate:.1f}%")
        
        print(f"\nHIỆU SUẤT THEO DANH MỤC:")
        for category, perf in stats['category_performance'].items():
            print(f"  • {category}: {perf['avg_score']:.1f}/10")
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quick_evaluation_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\nBáo cáo đã được lưu: {filepath}")


async def main():
    evaluator = QuickEvaluator()
    
    try:
        report = await evaluator.run_quick_evaluation()
        evaluator.save_report(report)
        
        print(f"\nĐánh giá nhanh hoàn thành!")
        print(f"Điểm trung bình: {report['statistics']['avg_score']:.1f}/10")
        
    except KeyboardInterrupt:
        print(f"\nĐánh giá bị dừng bởi người dùng")
    except Exception as e:
        print(f"\nLỗi: {e}")


if __name__ == "__main__":
    asyncio.run(main())