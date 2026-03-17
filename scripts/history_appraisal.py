#!/usr/bin/env python3
"""
历史学文献批判性评价工具
基于历史学研究特点提供结构化评价框架
"""

import sys
import json
from typing import Dict, List

# 历史学研究类型的评价清单
HISTORY_APPRAISAL_CHECKLISTS = {
    "primary_source": {
        "name": "一手史料研究 (Primary Source Analysis)",
        "questions": [
            {"id": "source_authenticity", "question": "史料真实性如何？", "details": "史料来源是否可靠？是否为原件或可信抄本？"},
            {"id": "source_context", "question": "史料背景是否清楚？", "details": "史料的创作时间、地点、作者、目的是否明确？"},
            {"id": "source_bias", "question": "是否存在偏见？", "details": "作者是否有特定立场？史料是否反映特定观点？"},
            {"id": "source_corroboration", "question": "是否有其他史料佐证？", "details": "该史料是否与其他独立史料相互印证？"},
            {"id": "source_interpretation", "question": "解释是否合理？", "details": "作者对史料的解释是否基于文本证据？是否过度解读？"},
            {"id": "source_silences", "question": "是否注意到沉默？", "details": "史料未提及的内容是否被考虑？缺失信息是否影响结论？"}
        ]
    },
    "secondary_source": {
        "name": "二手文献研究 (Secondary Source Analysis)",
        "questions": [
            {"id": "literature_review", "question": "文献综述是否全面？", "details": "是否涵盖相关领域的重要研究？是否包括不同观点？"},
            {"id": "thesis_clear", "question": "论点是否明确？", "details": "核心论点是否清晰陈述？是否有创新性？"},
            {"id": "evidence_support", "question": "证据是否支持论点？", "details": "使用的史料是否充分支持结论？是否存在选择性引用？"},
            {"id": "methodology", "question": "方法论是否恰当？", "details": "研究方法是否适合研究问题？是否借鉴其他学科方法？"},
            {"id": "historiography", "question": "史学史定位是否清晰？", "details": "该研究与既有史学传统的关系是否明确？"},
            {"id": "conclusions_valid", "question": "结论是否合理？", "details": "结论是否基于证据？是否避免过度概括？"}
        ]
    },
    "comparative_history": {
        "name": "比较历史研究 (Comparative History)",
        "questions": [
            {"id": "units_comparable", "question": "比较单位是否可比？", "details": "选择的比较对象是否具有合理的相似性和差异性？"},
            {"id": "comparison_framework", "question": "比较框架是否清晰？", "details": "比较的维度、标准是否明确？"},
            {"id": "contextual_factors", "question": "背景因素是否考虑？", "details": "是否充分考虑各国的历史背景和文化差异？"},
            {"id": "avoid_eurocentrism", "question": "是否避免欧洲中心主义？", "details": "比较是否基于多元视角？是否强加西方概念？"},
            {"id": "generalization", "question": "概括是否适度？", "details": "从比较中得出的结论是否谨慎？是否承认例外？"}
        ]
    },
    "quantitative_history": {
        "name": "量化历史研究 (Quantitative History)",
        "questions": [
            {"id": "data_reliable", "question": "数据是否可靠？", "details": "数据来源是否可信？数据质量如何？"},
            {"id": "data_representative", "question": "数据是否具有代表性？", "details": "样本是否能代表总体？是否存在选择偏倚？"},
            {"id": "methods_appropriate", "question": "统计方法是否恰当？", "details": "使用的统计方法是否适合数据类型和研究问题？"},
            {"id": "interpretation_cautious", "question": "解释是否谨慎？", "details": "是否避免过度依赖数字？是否考虑历史背景？"},
            {"id": "limitations_acknowledged", "question": "是否承认局限性？", "details": "数据和方法的局限性是否被讨论？"}
        ]
    },
    "microhistory": {
        "name": "微观史研究 (Microhistory)",
        "questions": [
            {"id": "source_density", "question": "史料密度是否足够？", "details": "是否有足够的细节重构个体或小群体的经历？"},
            {"id": "narrative_quality", "question": "叙事质量如何？", "details": "故事讲述是否生动？是否保持学术严谨？"},
            {"id": "broader_significance", "question": "是否具有更广泛意义？", "details": "个案研究是否揭示更大的历史模式？"},
            {"id": "avoid_anecdotal", "question": "是否避免轶事化？", "details": "研究是否超越有趣的故事，提供历史洞见？"}
        ]
    },
    "oral_history": {
        "name": "口述史研究 (Oral History)",
        "questions": [
            {"id": "interview_method", "question": "访谈方法是否恰当？", "details": "访谈设计、问题设置、记录方式是否合理？"},
            {"id": "sample_selection", "question": "样本选择是否合理？", "details": "受访者是否具有代表性？是否存在选择偏倚？"},
            {"id": "memory_reliability", "question": "记忆可靠性如何处理？", "details": "是否考虑记忆的可塑性和遗忘？是否与其他史料对比？"},
            {"id": "ethical_considerations", "question": "伦理考量是否充分？", "details": "是否获得知情同意？是否保护受访者隐私？"},
            {"id": "interpretation_context", "question": "解释是否考虑语境？", "details": "是否考虑访谈时的社会政治背景？"}
        ]
    },
    "book_review": {
        "name": "书评 (Book Review)",
        "questions": [
            {"id": "book_summary", "question": "书籍内容概括是否准确？", "details": "是否公正呈现原书的核心论点和结构？"},
            {"id": "critical_assessment", "question": "评价是否有批判性？", "details": "是否不仅描述，还提供分析和评价？"},
            {"id": "contextualization", "question": "是否定位学术背景？", "details": "该书与相关研究的关系是否被讨论？"},
            {"id": "balanced_evaluation", "question": "评价是否平衡？", "details": "是否既指出优点也指出不足？"}
        ]
    }
}


def get_appraisal_checklist(study_type: str) -> Dict:
    """获取指定研究类型的评价清单"""
    return HISTORY_APPRAISAL_CHECKLISTS.get(study_type, {
        "name": "通用历史研究评价",
        "questions": [
            {"id": "research_question", "question": "研究问题是否明确？", "details": "研究目的、问题意识是否清晰？"},
            {"id": "source_base", "question": "史料基础是否扎实？", "details": "使用的史料是否充分、多样、可靠？"},
            {"id": "argumentation", "question": "论证是否严密？", "details": "论点是否有证据支持？逻辑是否清晰？"},
            {"id": "originality", "question": "是否有创新性？", "details": "研究是否提供新见解、新材料或新方法？"},
            {"id": "significance", "question": "学术意义如何？", "details": "研究对史学领域的贡献是什么？"}
        ]
    })


def generate_appraisal_report(study_type: str, answers: Dict[str, str] = None) -> Dict:
    """
    生成批判性评价报告模板
    
    Args:
        study_type: 研究类型
        answers: 可选，预填的答案 {question_id: answer}
    
    Returns:
        评价报告字典
    """
    checklist = get_appraisal_checklist(study_type)
    
    report = {
        "study_type": study_type,
        "study_type_name": checklist["name"],
        "questions": [],
        "overall_assessment": ""
    }
    
    for q in checklist["questions"]:
        question_report = {
            "id": q["id"],
            "question": q["question"],
            "details": q["details"],
            "answer": answers.get(q["id"], "") if answers else "",
            "notes": ""
        }
        report["questions"].append(question_report)
    
    return report


def print_checklist_types():
    """打印可用的评价清单类型"""
    print("\n可用的历史学研究评价类型:\n")
    print("-" * 60)
    for key, value in HISTORY_APPRAISAL_CHECKLISTS.items():
        print(f"{key:20} - {value['name']}")
    print("-" * 60)
    print("\n使用示例:")
    print('  python3 history_appraisal.py primary_source')
    print('  python3 history_appraisal.py secondary_source > appraisal.json')


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("历史学文献批判性评价工具\n")
        print("Usage: python3 history_appraisal.py <study_type> [answers.json]")
        print("\n生成评价清单:")
        print("  python3 history_appraisal.py primary_source")
        print("  python3 history_appraisal.py secondary_source > my_appraisal.json")
        print("\n查看所有类型:")
        print("  python3 history_appraisal.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        print_checklist_types()
        sys.exit(0)
    
    study_type = sys.argv[1]
    
    # 检查类型是否有效
    if study_type not in HISTORY_APPRAISAL_CHECKLISTS:
        print(f"错误: 未知的研究类型 '{study_type}'", file=sys.stderr)
        print("\n可用类型:", file=sys.stderr)
        for key in HISTORY_APPRAISAL_CHECKLISTS.keys():
            print(f"  - {key}", file=sys.stderr)
        sys.exit(1)
    
    # 加载预填答案（如果有）
    answers = None
    if len(sys.argv) >= 3:
        try:
            with open(sys.argv[2], 'r', encoding='utf-8') as f:
                data = json.load(f)
                answers = data.get("answers", {})
        except Exception as e:
            print(f"警告: 无法加载答案文件: {e}", file=sys.stderr)
    
    # 生成报告
    report = generate_appraisal_report(study_type, answers)
    
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
