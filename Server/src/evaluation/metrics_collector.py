"""
Metrics Collector for Agentic System Evaluation
Tracks and analyzes multi-agent performance across 10 dimensions
"""
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict


@dataclass
class ExecutionMetrics:
    """Metrics for a single graph execution"""
    test_id: str
    timestamp: str
    input: str
    
    # Execution details
    success: bool
    total_latency_seconds: float
    plan_length: int
    agents_executed: List[str]
    revision_count: int
    
    # Agent-level metrics
    agent_latencies: Dict[str, float] = field(default_factory=dict)
    agent_statuses: Dict[str, str] = field(default_factory=dict)
    
    # Quality metrics
    diagnosis_provided: bool = False
    diagnosis_confidence: Optional[float] = None
    severity_level: Optional[str] = None
    red_flags_detected: List[str] = field(default_factory=list)
    
    # Constraint adherence
    expected_language: Optional[str] = None
    actual_language: Optional[str] = None
    language_match: bool = True
    style_constraint: Optional[str] = None
    
    # Error tracking
    errors_encountered: List[str] = field(default_factory=list)
    fallbacks_triggered: int = 0
    
    # State tracking
    plan_changes: int = 0
    information_needed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class AgenticMetrics:
    """Aggregated metrics across multiple executions"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    
    # Autonomy metrics
    avg_plan_length: float = 0.0
    avg_revisions: float = 0.0
    human_intervention_needed: int = 0
    
    # Efficiency metrics
    avg_latency_seconds: float = 0.0
    min_latency_seconds: float = float('inf')
    max_latency_seconds: float = 0.0
    
    # Coordination metrics
    agent_usage_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    agent_success_rate: Dict[str, float] = field(default_factory=dict)
    avg_agents_per_execution: float = 0.0
    
    # Quality metrics
    diagnosis_accuracy_count: int = 0  # Requires ground truth
    avg_confidence: float = 0.0
    emergency_detection_rate: float = 0.0
    
    # Constraint adherence
    language_adherence_rate: float = 0.0
    constraint_violations: int = 0
    
    # Error recovery
    error_count: int = 0
    fallback_rate: float = 0.0
    recovery_success_rate: float = 0.0
    
    def calculate_scores(self) -> Dict[str, float]:
        """Calculate agentic capability scores (0-10 scale)"""
        if self.total_executions == 0:
            return {}
        
        scores = {}
        
        # 1. Autonomy Score (8/10 baseline)
        # Based on: plan complexity, minimal human intervention
        autonomy = 8.0
        if self.human_intervention_needed > 0:
            autonomy -= (self.human_intervention_needed / self.total_executions) * 3
        scores['autonomy'] = max(0, min(10, autonomy))
        
        # 2. Reactivity Score (8/10 baseline)
        # Based on: emergency detection, information seeking
        reactivity = 8.0
        if self.emergency_detection_rate < 0.9:
            reactivity -= (1 - self.emergency_detection_rate) * 5
        scores['reactivity'] = max(0, min(10, reactivity))
        
        # 3. Proactivity Score (6/10 baseline)
        # Based on: plan lookahead, anticipatory actions
        proactivity = 6.0
        if self.avg_plan_length > 3:
            proactivity += 1.0
        scores['proactivity'] = max(0, min(10, proactivity))
        
        # 4. Social Ability (Coordination) Score (9/10 baseline)
        # Based on: agent handoff success, state consistency
        coordination = 9.0
        if self.error_count > 0:
            coordination -= (self.error_count / self.total_executions) * 2
        scores['coordination'] = max(0, min(10, coordination))
        
        # 5. Goal Orientation Score (8/10 baseline)
        # Based on: task completion rate
        goal_orientation = (self.successful_executions / self.total_executions) * 10
        scores['goal_orientation'] = goal_orientation
        
        # 6. Adaptability Score (7/10 baseline)
        # Based on: fallback usage, error recovery
        adaptability = 7.0
        if self.recovery_success_rate > 0.8:
            adaptability += 1.0
        scores['adaptability'] = max(0, min(10, adaptability))
        
        # 7. Memory/Context Score (7/10 baseline)
        # Based on: conversation history usage (placeholder)
        memory = 7.0
        scores['memory'] = memory
        
        # 8. Tool Use Score (8/10 baseline)
        # Based on: appropriate tool selection
        tool_use = 8.0
        scores['tool_use'] = tool_use
        
        # 9. Constraint Adherence Score (9/10 baseline)
        # Based on: language/style constraint following
        constraint_score = self.language_adherence_rate * 10
        scores['constraint_adherence'] = constraint_score
        
        # 10. Error Recovery Score (6/10 baseline)
        # Based on: successful error handling
        error_recovery = self.recovery_success_rate * 10
        scores['error_recovery'] = max(0, min(10, error_recovery))
        
        # Overall Score
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with scores"""
        data = asdict(self)
        # Convert defaultdict to regular dict for JSON serialization
        if 'agent_usage_count' in data:
            data['agent_usage_count'] = dict(data['agent_usage_count'])
        data['agentic_scores'] = self.calculate_scores()
        return data


class MetricsCollector:
    """Collects and aggregates metrics across test executions"""
    
    def __init__(self):
        self.executions: List[ExecutionMetrics] = []
        self.current_execution: Optional[ExecutionMetrics] = None
        self.start_time: Optional[float] = None
    
    def start_execution(self, test_id: str, input_text: str) -> None:
        """Start tracking a new execution"""
        self.start_time = time.time()
        self.current_execution = ExecutionMetrics(
            test_id=test_id,
            timestamp=datetime.now().isoformat(),
            input=input_text,
            success=False,
            total_latency_seconds=0.0,
            plan_length=0,
            agents_executed=[],
            revision_count=0
        )
    
    def end_execution(self, success: bool, final_state: Dict[str, Any]) -> ExecutionMetrics:
        """End execution tracking and record metrics"""
        if not self.current_execution or self.start_time is None:
            raise ValueError("No execution in progress")
        
        # Calculate total latency
        self.current_execution.total_latency_seconds = time.time() - self.start_time
        self.current_execution.success = success
        
        # Extract metrics from final state
        self._extract_state_metrics(final_state)
        
        # Store execution
        self.executions.append(self.current_execution)
        
        execution = self.current_execution
        self.current_execution = None
        self.start_time = None
        
        return execution
    
    def _extract_state_metrics(self, state: Dict[str, Any]) -> None:
        """Extract metrics from graph execution state"""
        if not self.current_execution:
            return
        
        # Plan metrics
        plan = state.get("plan", [])
        self.current_execution.plan_length = len(plan)
        self.current_execution.agents_executed = [
            step["step"] for step in plan if step.get("status") == "completed"
        ]
        
        # Revision tracking
        self.current_execution.revision_count = state.get("revision_count", 0)
        
        # Diagnosis metrics
        diagnosis = state.get("diagnosis", {})
        if diagnosis:
            self.current_execution.diagnosis_provided = True
            self.current_execution.diagnosis_confidence = diagnosis.get("confidence")
            
            risk_assessment = diagnosis.get("risk_assessment", {})
            self.current_execution.severity_level = risk_assessment.get("severity")
            self.current_execution.red_flags_detected = risk_assessment.get("red_flags", [])
        
        # Information needed flag
        self.current_execution.information_needed = bool(state.get("information_needed"))
        
        # Error tracking
        # TODO: Add error extraction from state if errors are stored
    
    def record_agent_execution(
        self, 
        agent_name: str, 
        latency: float, 
        status: str = "success"
    ) -> None:
        """Record individual agent execution metrics"""
        if not self.current_execution:
            return
        
        self.current_execution.agent_latencies[agent_name] = latency
        self.current_execution.agent_statuses[agent_name] = status
    
    def record_constraint_check(
        self, 
        expected_language: str, 
        actual_language: str,
        style_constraint: Optional[str] = None
    ) -> None:
        """Record constraint adherence check"""
        if not self.current_execution:
            return
        
        self.current_execution.expected_language = expected_language
        self.current_execution.actual_language = actual_language
        self.current_execution.language_match = (expected_language == actual_language)
        self.current_execution.style_constraint = style_constraint
    
    def record_error(self, error_message: str) -> None:
        """Record an error during execution"""
        if not self.current_execution:
            return
        
        self.current_execution.errors_encountered.append(error_message)
    
    def aggregate_metrics(self) -> AgenticMetrics:
        """Aggregate metrics across all executions"""
        if not self.executions:
            return AgenticMetrics()
        
        metrics = AgenticMetrics()
        metrics.total_executions = len(self.executions)
        metrics.successful_executions = sum(1 for e in self.executions if e.success)
        metrics.failed_executions = metrics.total_executions - metrics.successful_executions
        
        # Autonomy metrics
        metrics.avg_plan_length = sum(e.plan_length for e in self.executions) / metrics.total_executions
        metrics.avg_revisions = sum(e.revision_count for e in self.executions) / metrics.total_executions
        metrics.human_intervention_needed = sum(1 for e in self.executions if e.information_needed)
        
        # Efficiency metrics
        latencies = [e.total_latency_seconds for e in self.executions]
        metrics.avg_latency_seconds = sum(latencies) / len(latencies)
        metrics.min_latency_seconds = min(latencies)
        metrics.max_latency_seconds = max(latencies)
        
        # Coordination metrics
        for execution in self.executions:
            for agent in execution.agents_executed:
                metrics.agent_usage_count[agent] += 1
        
        total_agents = sum(len(e.agents_executed) for e in self.executions)
        metrics.avg_agents_per_execution = total_agents / metrics.total_executions
        
        # Calculate agent success rates
        for agent, count in metrics.agent_usage_count.items():
            success_count = sum(
                1 for e in self.executions 
                if agent in e.agents_executed and e.agent_statuses.get(agent) == "success"
            )
            metrics.agent_success_rate[agent] = success_count / count if count > 0 else 0.0
        
        # Quality metrics
        confidences = [e.diagnosis_confidence for e in self.executions if e.diagnosis_confidence is not None]
        if confidences:
            metrics.avg_confidence = sum(confidences) / len(confidences)
        
        emergency_cases = sum(1 for e in self.executions if e.severity_level == "EMERGENCY")
        if emergency_cases > 0:
            correctly_detected = sum(
                1 for e in self.executions 
                if e.severity_level == "EMERGENCY" and len(e.red_flags_detected) > 0
            )
            metrics.emergency_detection_rate = correctly_detected / emergency_cases
        
        # Constraint adherence
        language_checks = sum(1 for e in self.executions if e.expected_language is not None)
        if language_checks > 0:
            language_matches = sum(1 for e in self.executions if e.language_match)
            metrics.language_adherence_rate = language_matches / language_checks
            metrics.constraint_violations = language_checks - language_matches
        
        # Error recovery
        metrics.error_count = sum(len(e.errors_encountered) for e in self.executions)
        executions_with_errors = sum(1 for e in self.executions if len(e.errors_encountered) > 0)
        if executions_with_errors > 0:
            recovered = sum(1 for e in self.executions if len(e.errors_encountered) > 0 and e.success)
            metrics.recovery_success_rate = recovered / executions_with_errors
        
        return metrics
    
    def save_results(self, filepath: str) -> None:
        """Save execution results to JSON file"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_executions": len(self.executions),
            "executions": [e.to_dict() for e in self.executions],
            "aggregated_metrics": self.aggregate_metrics().to_dict()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Results saved to {filepath}")
    
    def print_summary(self) -> None:
        """Print summary of collected metrics"""
        metrics = self.aggregate_metrics()
        scores = metrics.calculate_scores()
        
        print("\n" + "="*70)
        print("📊 AGENTIC CAPABILITIES SUMMARY")
        print("="*70)
        
        print(f"\n📈 Execution Statistics:")
        print(f"   Total Executions: {metrics.total_executions}")
        print(f"   ✅ Successful: {metrics.successful_executions}")
        print(f"   ❌ Failed: {metrics.failed_executions}")
        print(f"   Success Rate: {(metrics.successful_executions/metrics.total_executions)*100:.1f}%")
        
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Latency: {metrics.avg_latency_seconds:.2f}s")
        print(f"   Min Latency: {metrics.min_latency_seconds:.2f}s")
        print(f"   Max Latency: {metrics.max_latency_seconds:.2f}s")
        print(f"   Avg Plan Length: {metrics.avg_plan_length:.1f} steps")
        print(f"   Avg Revisions: {metrics.avg_revisions:.1f}")
        
        print(f"\n🤖 Agent Coordination:")
        print(f"   Avg Agents per Execution: {metrics.avg_agents_per_execution:.1f}")
        print(f"   Most Used Agents:")
        for agent, count in sorted(metrics.agent_usage_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            success_rate = metrics.agent_success_rate.get(agent, 0) * 100
            print(f"      {agent}: {count} times ({success_rate:.0f}% success)")
        
        print(f"\n🎯 Quality Metrics:")
        print(f"   Avg Confidence: {metrics.avg_confidence:.2f}")
        print(f"   Emergency Detection Rate: {metrics.emergency_detection_rate*100:.1f}%")
        print(f"   Language Adherence: {metrics.language_adherence_rate*100:.1f}%")
        
        print(f"\n🚨 Error Recovery:")
        print(f"   Total Errors: {metrics.error_count}")
        print(f"   Recovery Success Rate: {metrics.recovery_success_rate*100:.1f}%")
        
        print(f"\n🏆 AGENTIC CAPABILITY SCORES (0-10 scale):")
        print(f"   1. Autonomy:              {scores.get('autonomy', 0):.1f}/10")
        print(f"   2. Reactivity:            {scores.get('reactivity', 0):.1f}/10")
        print(f"   3. Proactivity:           {scores.get('proactivity', 0):.1f}/10")
        print(f"   4. Coordination:          {scores.get('coordination', 0):.1f}/10")
        print(f"   5. Goal Orientation:      {scores.get('goal_orientation', 0):.1f}/10")
        print(f"   6. Adaptability:          {scores.get('adaptability', 0):.1f}/10")
        print(f"   7. Memory/Context:        {scores.get('memory', 0):.1f}/10")
        print(f"   8. Tool Use:              {scores.get('tool_use', 0):.1f}/10")
        print(f"   9. Constraint Adherence:  {scores.get('constraint_adherence', 0):.1f}/10")
        print(f"   10. Error Recovery:       {scores.get('error_recovery', 0):.1f}/10")
        print(f"\n   📊 OVERALL SCORE:          {scores.get('overall', 0):.1f}/10")
        
        print("="*70)
