#!/usr/bin/env python3
"""
跨数据源验证器
使用多数据源交叉验证提高数据准确性
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CrossDataValidator:
    """跨数据源验证器"""

    def __init__(self, tolerance_pct: float = 1.0):
        """
        Args:
            tolerance_pct: 允许的差异百分比（默认1%）
        """
        self.tolerance_pct = tolerance_pct
        self.validation_results = []

    async def validate_stock_data(self, symbol: str, date: str,
                                 data_sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """交叉验证股票数据

        Args:
            symbol: 股票代码
            date: 日期
            data_sources: 数据源字典，格式: {source_name: data}

        Returns:
            验证结果
        """
        validation_result = {
            "symbol": symbol,
            "date": date,
            "sources": list(data_sources.keys()),
            "consistency_score": 100,
            "differences": [],
            "validation_status": "passed",
            "timestamp": time.time()
        }

        if len(data_sources) < 2:
            validation_result["validation_status"] = "skipped"
            validation_result["reason"] = "需要至少2个数据源进行交叉验证"
            return validation_result

        # 定义需要比较的关键字段
        comparison_fields = [
            ("close", "收盘价"),
            ("open", "开盘价"),
            ("high", "最高价"),
            ("low", "最低价"),
            ("volume", "成交量")
        ]

        source_names = list(data_sources.keys())
        differences_found = False

        # 对每个字段进行比较
        for field, field_name in comparison_fields:
            field_differences = self._compare_field_across_sources(
                symbol, date, field, field_name, data_sources
            )
            if field_differences:
                differences_found = True
                validation_result["differences"].extend(field_differences)
                validation_result["consistency_score"] -= len(field_differences) * 2

        # 检查整体一致性
        if differences_found:
            validation_result["validation_status"] = "warning"
            if validation_result["consistency_score"] < 80:
                validation_result["validation_status"] = "failed"

        # 添加详细分析
        validation_result["analysis"] = self._analyze_differences(
            validation_result["differences"]
        )

        return validation_result

    def _compare_field_across_sources(self, symbol: str, date: str,
                                     field: str, field_name: str,
                                     data_sources: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """比较单个字段在不同数据源中的值"""
        differences = []

        source_names = list(data_sources.keys())
        field_values = {}

        # 提取所有数据源的字段值
        for source_name, data in data_sources.items():
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    field_values[source_name] = value
                except (ValueError, TypeError):
                    logger.warning(f"Invalid {field} value from {source_name}: {data.get(field)}")

        if len(field_values) < 2:
            return differences

        # 计算所有数据源的统计信息
        values = list(field_values.values())
        avg_value = sum(values) / len(values)
        min_value = min(values)
        max_value = max(values)
        max_diff_pct = ((max_value - min_value) / avg_value * 100) if avg_value > 0 else 0

        # 如果差异超过阈值，记录差异
        if max_diff_pct > self.tolerance_pct:
            differences.append({
                "field": field,
                "field_name": field_name,
                "max_difference_pct": round(max_diff_pct, 2),
                "tolerance_pct": self.tolerance_pct,
                "source_values": {k: round(v, 4) for k, v in field_values.items()},
                "average": round(avg_value, 4),
                "severity": "high" if max_diff_pct > 5.0 else "medium"
            })

        return differences

    def _analyze_differences(self, differences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析差异模式"""
        if not differences:
            return {"summary": "所有数据源一致"}

        analysis = {
            "total_differences": len(differences),
            "severity_breakdown": {
                "high": len([d for d in differences if d.get("severity") == "high"]),
                "medium": len([d for d in differences if d.get("severity") == "medium"]),
                "low": len([d for d in differences if d.get("severity") == "low"])
            },
            "most_problematic_field": None,
            "recommendations": []
        }

        # 找出问题最多的字段
        field_counts = {}
        for diff in differences:
            field = diff["field"]
            field_counts[field] = field_counts.get(field, 0) + 1

        if field_counts:
            analysis["most_problematic_field"] = max(field_counts.items(), key=lambda x: x[1])[0]

        # 生成建议
        if analysis["severity_breakdown"]["high"] > 0:
            analysis["recommendations"].append("发现严重差异，建议检查数据源质量")
        if analysis["total_differences"] > 3:
            analysis["recommendations"].append("差异数量较多，建议增加数据清洗步骤")
        if analysis["most_problematic_field"]:
            analysis["recommendations"].append(
                f"'{analysis['most_problematic_field']}'字段差异较多，建议重点检查"
            )

        return analysis

    async def batch_validate(self, validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量验证并生成报告

        Args:
            validations: 验证结果列表

        Returns:
            批量验证报告
        """
        total_validations = len(validations)
        passed = len([v for v in validations if v["validation_status"] == "passed"])
        warnings = len([v for v in validations if v["validation_status"] == "warning"])
        failed = len([v for v in validations if v["validation_status"] == "failed"])
        skipped = len([v for v in validations if v["validation_status"] == "skipped"])

        avg_consistency_score = (
            sum(v["consistency_score"] for v in validations) / max(1, total_validations)
        )

        report = {
            "summary": {
                "total": total_validations,
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": (passed / max(1, total_validations)) * 100,
                "average_consistency_score": avg_consistency_score
            },
            "differences_summary": self._summarize_differences(validations),
            "recommendations": self._generate_batch_recommendations(passed, warnings, failed)
        }

        return report

    def _summarize_differences(self, validations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """汇总所有差异"""
        all_differences = []
        for validation in validations:
            all_differences.extend(validation.get("differences", []))

        if not all_differences:
            return {"message": "未发现差异"}

        field_stats = {}
        for diff in all_differences:
            field = diff["field"]
            if field not in field_stats:
                field_stats[field] = {
                    "count": 0,
                    "avg_diff_pct": 0,
                    "max_diff_pct": 0
                }
            field_stats[field]["count"] += 1
            field_stats[field]["avg_diff_pct"] += diff["max_difference_pct"]
            field_stats[field]["max_diff_pct"] = max(
                field_stats[field]["max_diff_pct"],
                diff["max_difference_pct"]
            )

        # 计算平均差异
        for field in field_stats:
            count = field_stats[field]["count"]
            field_stats[field]["avg_diff_pct"] /= count

        return {
            "total_differences": len(all_differences),
            "fields_affected": list(field_stats.keys()),
            "field_statistics": field_stats
        }

    def _generate_batch_recommendations(self, passed: int, warnings: int, failed: int) -> List[str]:
        """生成批量验证建议"""
        recommendations = []

        total = passed + warnings + failed
        if total == 0:
            return ["无验证数据"]

        pass_rate = (passed / total) * 100

        if pass_rate < 80:
            recommendations.append("整体通过率较低，建议全面检查数据质量")
        elif pass_rate < 90:
            recommendations.append("通过率有待提高，建议优化数据清洗流程")
        else:
            recommendations.append("数据质量良好，建议保持当前标准")

        if failed > 0:
            recommendations.append(f"存在{failed}个验证失败，建议优先处理")

        if warnings > passed:
            recommendations.append("警告数量较多，建议降低验证阈值或提高数据质量")

        return recommendations

    def save_validation_report(self, report: Dict[str, Any],
                              symbol: str = None,
                              output_dir: str = "data_quality"):
        """保存验证报告"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = time.strftime('%Y%m%d_%H%M%S')
        if symbol:
            filename = f"{symbol}_cross_validation_report_{timestamp}.json"
        else:
            filename = f"cross_validation_report_{timestamp}.json"

        filepath = output_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"Validation report saved: {filepath}")
        return str(filepath)


# 模拟数据源
def mock_data_source_1(symbol: str, date: str) -> Dict[str, Any]:
    """模拟数据源1"""
    import random
    base_price = 100.0
    return {
        "symbol": symbol,
        "date": date,
        "open": base_price + random.uniform(-1, 1),
        "high": base_price + random.uniform(0, 2),
        "low": base_price + random.uniform(-2, 0),
        "close": base_price + random.uniform(-0.5, 0.5),
        "volume": random.randint(1000000, 10000000),
        "source": "DataSource1"
    }


def mock_data_source_2(symbol: str, date: str) -> Dict[str, Any]:
    """模拟数据源2（带轻微差异）"""
    import random
    base_price = 100.0
    # 模拟数据源2有微小差异
    return {
        "symbol": symbol,
        "date": date,
        "open": base_price + random.uniform(-1.2, 1.2),
        "high": base_price + random.uniform(0, 2.2),
        "low": base_price + random.uniform(-2.2, 0),
        "close": base_price + random.uniform(-0.8, 0.8),
        "volume": random.randint(1100000, 11000000),
        "source": "DataSource2"
    }


async def test_cross_validator():
    """测试交叉验证器"""
    print("Testing Cross Data Validator")
    print("=" * 60)

    validator = CrossDataValidator(tolerance_pct=2.0)

    # 测试多个股票
    test_symbols = ["600000.SH", "600036.SH", "601318.SH"]
    test_date = "2025-12-09"

    all_validations = []

    for symbol in test_symbols:
        print(f"\nValidating {symbol}...")

        # 获取多个数据源的数据
        data_sources = {
            "source1": mock_data_source_1(symbol, test_date),
            "source2": mock_data_source_2(symbol, test_date)
        }

        # 进行交叉验证
        validation = await validator.validate_stock_data(
            symbol, test_date, data_sources
        )

        print(f"  Consistency Score: {validation['consistency_score']}")
        print(f"  Status: {validation['validation_status']}")
        if validation['differences']:
            print(f"  Differences found: {len(validation['differences'])}")

        all_validations.append(validation)

    # 生成批量报告
    print("\n" + "=" * 60)
    print("Batch Validation Report")
    print("=" * 60)

    batch_report = await validator.batch_validate(all_validations)
    print(json.dumps(batch_report, ensure_ascii=False, indent=2))

    # 保存报告
    report_file = validator.save_validation_report(batch_report)
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_cross_validator())
