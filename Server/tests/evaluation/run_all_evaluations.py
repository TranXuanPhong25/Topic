#!/usr/bin/env python3
import asyncio
import json
import argparse
from datetime import datetime
from pathlib import Path
import sys
import os

# Add the Server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from quick_evaluation import QuickEvaluator
from rare_diseases_evaluation import RareDiseasesEvaluator


class MasterEvaluator:
    def __init__(self):
        self.results_dir = Path(__file__).parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def run_all_evaluations(self):
        print("BẮT ĐẦU ĐÁNH GIÁ TOÀN DIỆN CHATBOT Y TẾ")
        print("="*60)
        
        all_reports = {}
        
        print(f"\nBƯỚC 1: ĐÁNH GIÁ NHANH")
        print("-" * 40)
        try:
            quick_evaluator = QuickEvaluator()
            quick_report = await quick_evaluator.run_quick_evaluation()
            all_reports["quick_evaluation"] = quick_report
            print(f"Đánh giá nhanh hoàn thành: {quick_report['statistics']['avg_score']:.1f}/10")
        except Exception as e:
            print(f"Lỗi đánh giá nhanh: {e}")
            all_reports["quick_evaluation"] = {"error": str(e)}
        
        print(f"\nBƯỚC 2: ĐÁNH GIÁ BỆNH HIẾM GẶP")
        print("-" * 40)
        try:
            rare_evaluator = RareDiseasesEvaluator()
            rare_report = await rare_evaluator.run_evaluation()
            all_reports["rare_diseases_evaluation"] = rare_report
            print(f"Đánh giá bệnh hiếm hoàn thành: {rare_report['statistics']['avg_overall_score']:.1f}/10")
        except Exception as e:
            print(f"Lỗi đánh giá bệnh hiếm: {e}")
            all_reports["rare_diseases_evaluation"] = {"error": str(e)}
        
        print(f"\nBƯỚC 3: TẠO BÁO CÁO TỔNG HỢP")
        print("-" * 40)
        comprehensive_report = self._create_comprehensive_report(all_reports)
        
        # 4. Lưu báo cáo
        self._save_all_reports(all_reports, comprehensive_report)
        
        # 5. In tóm tắt cuối
        self._print_final_summary(comprehensive_report)
        
        return comprehensive_report
    
    def _create_comprehensive_report(self, all_reports: dict) -> dict:
        
        comprehensive = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "comprehensive",
            "summary": {},
            "detailed_reports": all_reports
        }
        
        # Tính toán metrics tổng hợp
        summary = {}
        
        # Từ quick evaluation
        if "quick_evaluation" in all_reports and "statistics" in all_reports["quick_evaluation"]:
            quick_stats = all_reports["quick_evaluation"]["statistics"]
            summary["quick_evaluation"] = {
                "avg_score": quick_stats.get("avg_score", 0),
                "success_rate": quick_stats.get("success_rate", 0),
                "total_cases": all_reports["quick_evaluation"].get("total_cases", 0)
            }
        
        # Từ rare diseases evaluation
        if "rare_diseases_evaluation" in all_reports and "statistics" in all_reports["rare_diseases_evaluation"]:
            rare_stats = all_reports["rare_diseases_evaluation"]["statistics"]
            summary["rare_diseases_evaluation"] = {
                "avg_overall_score": rare_stats.get("avg_overall_score", 0),
                "avg_diagnosis_accuracy": rare_stats.get("avg_diagnosis_accuracy", 0),
                "avg_symptom_recognition": rare_stats.get("avg_symptom_recognition", 0),
                "success_rate": rare_stats.get("success_rate", 0),
                "total_cases": all_reports["rare_diseases_evaluation"].get("total_cases", 0)
            }
        
        # Tính điểm tổng hợp
        total_score = 0
        score_count = 0
        
        if "quick_evaluation" in summary:
            total_score += summary["quick_evaluation"]["avg_score"]
            score_count += 1
        
        if "rare_diseases_evaluation" in summary:
            total_score += summary["rare_diseases_evaluation"]["avg_overall_score"]
            score_count += 1
        
        summary["overall"] = {
            "comprehensive_score": total_score / score_count if score_count > 0 else 0,
            "total_test_cases": (
                summary.get("quick_evaluation", {}).get("total_cases", 0) +
                summary.get("rare_diseases_evaluation", {}).get("total_cases", 0)
            ),
            "evaluation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        comprehensive["summary"] = summary
        return comprehensive
    
    def _save_all_reports(self, all_reports: dict, comprehensive_report: dict):
        
        # Lưu báo cáo tổng hợp
        comprehensive_file = self.results_dir / f"comprehensive_evaluation_{self.timestamp}.json"
        with open(comprehensive_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
        
        # Lưu từng báo cáo riêng
        for eval_type, report in all_reports.items():
            if "error" not in report:
                individual_file = self.results_dir / f"{eval_type}_{self.timestamp}.json"
                with open(individual_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"Tất cả báo cáo đã được lưu với timestamp: {self.timestamp}")
    
    def _print_final_summary(self, comprehensive_report: dict):
        print("\n" + "="*70)
        print("KẾT QUẢ ĐÁNH GIÁ TOÀN DIỆN CHATBOT Y TẾ")
        print("="*70)
        
        summary = comprehensive_report.get("summary", {})
        overall = summary.get("overall", {})
        
        print(f"Ngày đánh giá: {overall.get('evaluation_date', 'N/A')}")
        print(f"Tổng số test cases: {overall.get('total_test_cases', 0)}")
        print(f"ĐIỂM TỔNG HỢP: {overall.get('comprehensive_score', 0):.1f}/10")
        
        # Chi tiết từng loại đánh giá
        if "quick_evaluation" in summary:
            quick = summary["quick_evaluation"]
            print(f"\nĐánh giá nhanh:")
            print(f"   • Điểm trung bình: {quick.get('avg_score', 0):.1f}/10")
            print(f"   • Tỷ lệ thành công: {quick.get('success_rate', 0):.1f}%")
            print(f"   • Số ca test: {quick.get('total_cases', 0)}")
        
        if "rare_diseases_evaluation" in summary:
            rare = summary["rare_diseases_evaluation"]
            print(f"\nĐánh giá bệnh hiếm:")
            print(f"   • Điểm tổng: {rare.get('avg_overall_score', 0):.1f}/10")
            print(f"   • Điểm chẩn đoán: {rare.get('avg_diagnosis_accuracy', 0):.1f}/10")
            print(f"   • Điểm nhận biết triệu chứng: {rare.get('avg_symptom_recognition', 0):.1f}/10")
            print(f"   • Tỷ lệ thành công: {rare.get('success_rate', 0):.1f}%")
            print(f"   • Số ca test: {rare.get('total_cases', 0)}")
        
        # Đánh giá tổng thể
        score = overall.get('comprehensive_score', 0)
        if score >= 8:
            grade = "XUẤT SẮC"
        elif score >= 7:
            grade = "TỐT"
        elif score >= 6:
            grade = "KHỐNG"
        elif score >= 5:
            grade = "TRUNG BÌNH"
        else:
            grade = "CẦN CẢI THIỆN"
        
        print(f"\nĐÁNH GIÁ TỔNG THỂ: {grade}")
        
        print(f"\nBáo cáo chi tiết đã được lưu với timestamp: {self.timestamp}")
        print("="*70)


async def main():
    parser = argparse.ArgumentParser(description="Đánh giá toàn diện chatbot y tế")
    parser.add_argument("--quick-only", action="store_true", help="Chỉ chạy đánh giá nhanh")
    parser.add_argument("--rare-only", action="store_true", help="Chỉ chạy đánh giá bệnh hiếm")
    
    args = parser.parse_args()
    
    master_evaluator = MasterEvaluator()
    
    try:
        if args.quick_only:
            print("Chạy đánh giá nhanh...")
            evaluator = QuickEvaluator()
            report = await evaluator.run_quick_evaluation()
            evaluator.save_report(report)
        elif args.rare_only:
            print("Chạy đánh giá bệnh hiếm...")
            evaluator = RareDiseasesEvaluator()
            report = await evaluator.run_evaluation()
            evaluator.save_report(report)
        else:
            # Chạy đánh giá toàn diện
            await master_evaluator.run_all_evaluations()
            
    except KeyboardInterrupt:
        print(f"\nĐánh giá bị dừng bởi người dùng")
    except Exception as e:
        print(f"\nLỗi trong quá trình đánh giá: {e}")


if __name__ == "__main__":
    asyncio.run(main())