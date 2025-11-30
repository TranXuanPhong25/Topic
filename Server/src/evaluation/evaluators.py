"""
Specialized Evaluators for Medical Diagnostic System
Domain-specific evaluation logic for diagnosis, constraints, coordination, and performance
"""
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DiagnosisEvaluation:
    """Results from diagnosis quality evaluation"""
    has_primary_diagnosis: bool
    has_differential_diagnoses: bool
    has_confidence_score: bool
    has_risk_assessment: bool
    severity_appropriate: bool
    red_flags_identified: bool
    clinical_reasoning_present: bool
    
    quality_score: float  # 0-1
    issues: List[str]
    
    def passed(self) -> bool:
        """Check if diagnosis meets minimum quality standards"""
        return (
            self.has_primary_diagnosis and
            self.has_confidence_score and
            self.quality_score >= 0.6
        )


class DiagnosisEvaluator:
    """Evaluates diagnosis quality and completeness"""
    
    @staticmethod
    def evaluate(diagnosis: Dict[str, Any], expected_severity: Optional[str] = None) -> DiagnosisEvaluation:
        """
        Evaluate diagnosis output quality
        
        Args:
            diagnosis: Diagnosis dictionary from graph execution
            expected_severity: Optional expected severity level for validation
        
        Returns:
            DiagnosisEvaluation with quality assessment
        """
        issues = []
        
        # Check for primary diagnosis
        primary_diagnosis = diagnosis.get("primary_diagnosis")
        has_primary = bool(primary_diagnosis and primary_diagnosis.get("condition"))
        if not has_primary:
            issues.append("Missing primary diagnosis")
        
        # Check for differential diagnoses
        differential = diagnosis.get("differential_diagnosis", [])
        has_differential = len(differential) >= 2
        if not has_differential:
            issues.append(f"Insufficient differential diagnoses (found {len(differential)}, expected ≥2)")
        
        # Check confidence score
        confidence = diagnosis.get("confidence")
        has_confidence = confidence is not None and 0 <= confidence <= 1
        if not has_confidence:
            issues.append("Missing or invalid confidence score")
        
        # Check risk assessment
        risk_assessment = diagnosis.get("risk_assessment", {})
        has_risk = bool(risk_assessment)
        if not has_risk:
            issues.append("Missing risk assessment")
        
        # Check severity appropriateness
        severity = risk_assessment.get("severity")
        severity_appropriate = True
        if expected_severity and severity != expected_severity:
            severity_appropriate = False
            issues.append(f"Severity mismatch: expected {expected_severity}, got {severity}")
        
        # Check red flags
        red_flags = risk_assessment.get("red_flags", [])
        red_flags_identified = len(red_flags) > 0 if severity == "EMERGENCY" else True
        if severity == "EMERGENCY" and not red_flags_identified:
            issues.append("Emergency case but no red flags identified")
        
        # Check clinical reasoning
        reasoning = diagnosis.get("clinical_reasoning", "")
        clinical_reasoning_present = len(reasoning) > 50
        if not clinical_reasoning_present:
            issues.append("Insufficient clinical reasoning")
        
        # Calculate quality score
        quality_components = [
            has_primary,
            has_differential,
            has_confidence,
            has_risk,
            severity_appropriate,
            red_flags_identified,
            clinical_reasoning_present
        ]
        quality_score = sum(quality_components) / len(quality_components)
        
        return DiagnosisEvaluation(
            has_primary_diagnosis=has_primary,
            has_differential_diagnoses=has_differential,
            has_confidence_score=has_confidence,
            has_risk_assessment=has_risk,
            severity_appropriate=severity_appropriate,
            red_flags_identified=red_flags_identified,
            clinical_reasoning_present=clinical_reasoning_present,
            quality_score=quality_score,
            issues=issues
        )


@dataclass
class ConstraintEvaluation:
    """Results from constraint adherence evaluation"""
    language_match: bool
    style_match: bool
    urgency_handled: bool
    
    expected_language: str
    actual_language: str
    expected_style: Optional[str]
    
    adherence_score: float  # 0-1
    violations: List[str]
    
    def passed(self) -> bool:
        """Check if constraints were followed"""
        return self.language_match and self.adherence_score >= 0.8


class ConstraintEvaluator:
    """Evaluates constraint adherence (language, style, urgency)"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect if text is primarily Vietnamese or English
        
        Args:
            text: Text to analyze
        
        Returns:
            "Vietnamese" or "English"
        """
        # Vietnamese-specific characters
        vietnamese_chars = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
        vietnamese_count = sum(1 for char in text.lower() if char in vietnamese_chars)
        
        # If more than 5% of characters are Vietnamese-specific, consider it Vietnamese
        if len(text) > 0 and vietnamese_count / len(text) > 0.05:
            return "Vietnamese"
        return "English"
    
    @staticmethod
    def evaluate_style(text: str, expected_style: str) -> bool:
        """
        Evaluate if response style matches expectation
        
        Args:
            text: Response text
            expected_style: "Brief" or "Detailed"
        
        Returns:
            True if style matches expectation
        """
        word_count = len(text.split())
        
        if expected_style == "Brief":
            return word_count < 150  # Brief should be concise
        elif expected_style == "Detailed":
            return word_count >= 150  # Detailed should be thorough
        
        return True  # No style constraint
    
    @staticmethod
    def evaluate(
        response: str,
        plan_step: Dict[str, Any],
        expected_constraints: Optional[Dict[str, str]] = None
    ) -> ConstraintEvaluation:
        """
        Evaluate constraint adherence in response
        
        Args:
            response: Final response text
            plan_step: Plan step with context field containing constraints
            expected_constraints: Optional explicit expected constraints
        
        Returns:
            ConstraintEvaluation with adherence assessment
        """
        violations = []
        
        # Extract constraints from plan step context
        context = plan_step.get("context", "")
        
        # Parse language constraint
        language_match = re.search(r"Language:\s*(Vietnamese|English)", context)
        expected_language = language_match.group(1) if language_match else "English"
        
        # Override with explicit constraints if provided
        if expected_constraints:
            expected_language = expected_constraints.get("language", expected_language)
        
        # Detect actual language
        actual_language = ConstraintEvaluator.detect_language(response)
        
        # Check language match
        language_matches = (expected_language == actual_language)
        if not language_matches:
            violations.append(f"Language mismatch: expected {expected_language}, got {actual_language}")
        
        # Parse style constraint
        style_match_result = re.search(r"Style:\s*(Brief|Detailed)", context)
        expected_style = style_match_result.group(1) if style_match_result else None
        
        if expected_constraints:
            expected_style = expected_constraints.get("style", expected_style)
        
        # Check style match
        style_matches = True
        if expected_style:
            style_matches = ConstraintEvaluator.evaluate_style(response, expected_style)
            if not style_matches:
                violations.append(f"Style mismatch: expected {expected_style}")
        
        # Parse urgency
        urgency_match = re.search(r"Urgency:\s*(Emergency|Urgent|Routine)", context)
        urgency = urgency_match.group(1) if urgency_match else "Routine"
        
        # Check urgency handling (placeholder - would need response analysis)
        urgency_handled = True  # Assume handled unless we can prove otherwise
        
        # Calculate adherence score
        components = [language_matches, style_matches, urgency_handled]
        adherence_score = sum(components) / len(components)
        
        return ConstraintEvaluation(
            language_match=language_matches,
            style_match=style_matches,
            urgency_handled=urgency_handled,
            expected_language=expected_language,
            actual_language=actual_language,
            expected_style=expected_style,
            adherence_score=adherence_score,
            violations=violations
        )


@dataclass
class CoordinationEvaluation:
    """Results from agent coordination evaluation"""
    plan_completed: bool
    agents_executed_correctly: bool
    state_consistency: bool
    handoff_success: bool
    
    expected_agents: List[str]
    actual_agents: List[str]
    missing_agents: List[str]
    unexpected_agents: List[str]
    
    coordination_score: float  # 0-1
    issues: List[str]
    
    def passed(self) -> bool:
        """Check if coordination was successful"""
        return self.plan_completed and self.coordination_score >= 0.7


class CoordinationEvaluator:
    """Evaluates multi-agent coordination quality"""
    
    @staticmethod
    def evaluate(
        final_state: Dict[str, Any],
        expected_agents: Optional[List[str]] = None
    ) -> CoordinationEvaluation:
        """
        Evaluate agent coordination and workflow execution
        
        Args:
            final_state: Final graph state after execution
            expected_agents: Optional list of expected agents for validation
        
        Returns:
            CoordinationEvaluation with coordination assessment
        """
        issues = []
        
        # Extract plan and execution details
        plan = final_state.get("plan", [])
        
        # Check plan completion
        completed_steps = [step for step in plan if step.get("status") == "completed"]
        plan_completed = len(completed_steps) == len(plan) or final_state.get("next_step") == "END"
        
        if not plan_completed:
            incomplete = len(plan) - len(completed_steps)
            issues.append(f"{incomplete} plan steps not completed")
        
        # Extract agents executed
        actual_agents = [step["step"] for step in completed_steps]
        
        # Check against expected agents if provided
        agents_executed_correctly = True
        missing_agents = []
        unexpected_agents = []
        
        if expected_agents:
            expected_set = set(expected_agents)
            actual_set = set(actual_agents)
            
            missing_agents = list(expected_set - actual_set)
            unexpected_agents = list(actual_set - expected_set)
            
            agents_executed_correctly = (expected_set == actual_set)
            
            if missing_agents:
                issues.append(f"Missing expected agents: {missing_agents}")
            if unexpected_agents:
                issues.append(f"Unexpected agents executed: {unexpected_agents}")
        
        # Check state consistency (no obvious corruption)
        state_consistency = True
        required_fields = ["input", "plan", "next_step"]
        for field in required_fields:
            if field not in final_state:
                state_consistency = False
                issues.append(f"Missing required field in state: {field}")
        
        # Check handoff success (no orphaned steps)
        handoff_success = True
        for i, step in enumerate(plan):
            status = step.get("status")
            if status == "current" and i < len(plan) - 1:
                # Found a "current" step that's not the last - suggests stuck handoff
                handoff_success = False
                issues.append(f"Agent handoff stuck at step {i}: {step.get('step')}")
        
        # Calculate coordination score
        components = [
            plan_completed,
            agents_executed_correctly,
            state_consistency,
            handoff_success
        ]
        coordination_score = sum(components) / len(components)
        
        return CoordinationEvaluation(
            plan_completed=plan_completed,
            agents_executed_correctly=agents_executed_correctly,
            state_consistency=state_consistency,
            handoff_success=handoff_success,
            expected_agents=expected_agents or [],
            actual_agents=actual_agents,
            missing_agents=missing_agents,
            unexpected_agents=unexpected_agents,
            coordination_score=coordination_score,
            issues=issues
        )


@dataclass
class PerformanceEvaluation:
    """Results from performance evaluation"""
    latency_acceptable: bool
    within_token_budget: bool
    efficient_execution: bool
    
    total_latency_seconds: float
    max_acceptable_latency: float
    plan_efficiency: float  # actual_steps / optimal_steps
    
    performance_score: float  # 0-1
    bottlenecks: List[str]
    
    def passed(self) -> bool:
        """Check if performance meets standards"""
        return self.latency_acceptable and self.performance_score >= 0.6


class PerformanceEvaluator:
    """Evaluates system performance (latency, efficiency)"""
    
    @staticmethod
    def evaluate(
        execution_metrics: Any,  # ExecutionMetrics from metrics_collector
        max_latency: float = 15.0,
        optimal_plan_length: Optional[int] = None
    ) -> PerformanceEvaluation:
        """
        Evaluate performance metrics
        
        Args:
            execution_metrics: ExecutionMetrics object
            max_latency: Maximum acceptable latency in seconds
            optimal_plan_length: Optimal number of steps (if known)
        
        Returns:
            PerformanceEvaluation with performance assessment
        """
        bottlenecks = []
        
        # Check latency
        total_latency = execution_metrics.total_latency_seconds
        latency_acceptable = total_latency <= max_latency
        
        if not latency_acceptable:
            bottlenecks.append(f"Total latency {total_latency:.2f}s exceeds limit {max_latency}s")
        
        # Check individual agent latencies for bottlenecks
        for agent, latency in execution_metrics.agent_latencies.items():
            if latency > 5.0:  # Agent taking more than 5 seconds
                bottlenecks.append(f"{agent} took {latency:.2f}s (slow)")
        
        # Token budget (placeholder - would need actual token counting)
        within_token_budget = True
        
        # Calculate plan efficiency
        actual_steps = execution_metrics.plan_length
        if optimal_plan_length:
            plan_efficiency = optimal_plan_length / actual_steps
            efficient_execution = plan_efficiency >= 0.8
            
            if not efficient_execution:
                bottlenecks.append(f"Plan inefficient: {actual_steps} steps vs {optimal_plan_length} optimal")
        else:
            plan_efficiency = 1.0
            efficient_execution = True
        
        # Calculate performance score
        components = [
            latency_acceptable,
            within_token_budget,
            efficient_execution
        ]
        performance_score = sum(components) / len(components)
        
        # Adjust score based on latency
        if total_latency > 0:
            latency_penalty = min(total_latency / max_latency - 1, 0.3)
            performance_score = max(0, performance_score - latency_penalty)
        
        return PerformanceEvaluation(
            latency_acceptable=latency_acceptable,
            within_token_budget=within_token_budget,
            efficient_execution=efficient_execution,
            total_latency_seconds=total_latency,
            max_acceptable_latency=max_latency,
            plan_efficiency=plan_efficiency,
            performance_score=performance_score,
            bottlenecks=bottlenecks
        )
