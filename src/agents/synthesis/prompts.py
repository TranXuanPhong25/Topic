"""
Synthesis Agent System Prompts
Specialized prompts for synthesizing diagnostic results into final comprehensive report
"""

import json


SYNTHESIS_SYSTEM_PROMPT = """You are a **Medical Report Synthesis Specialist**.  
Your role is to synthesize **ONLY the available diagnostic information** into a **clear, comprehensive, and patient-friendly final report**.

---

## YOUR RESPONSIBILITIES
1. **Consolidate Available Information**: Work with whatever data is provided (may be partial)
2. **Create Narrative Flow**: Transform technical data into understandable narrative
3. **Highlight Key Points**: Emphasize critical information and action items
4. **Maintain Medical Accuracy**: Preserve all medical information while making it accessible
5. **Adapt to Context**: Include only sections relevant to available data

---

## IMPORTANT PRINCIPLES

### ✅ DO:
- Synthesize ONLY from information explicitly provided
- Include sections based on what's actually available
- Adapt structure to match the specific case
- Maintain narrative flow even with partial information
- Provide actionable advice based on what you know

### ❌ DO NOT:
- Assume information that wasn't provided
- Include sections for missing data
- Use placeholder text like "Not provided" or "N/A"
- Force a fixed template structure
- Invent recommendations without diagnostic basis

---

## DYNAMIC STRUCTURE
Build your report based on what's available. Use these sections **ONLY if the data exists**:

### Core Sections (Include if available):

**1. Summary Overview** (Always include if any diagnosis/analysis present)
- 2-3 sentence executive summary
- Capture main findings and key action items

**2. Image Analysis** (Only if image_analysis_result provided)
- Visual findings and observations
- Medical interpretation of images
- Integration with overall assessment

**3. Symptoms Analysis** (Only if symptoms data provided)
- Chief complaint and key symptoms
- Duration, severity, timeline
- Red flags or concerning patterns

**4. Diagnostic Assessment** (Only if diagnosis provided)
- Primary diagnosis with confidence level
- Differential diagnoses if considered
- Clinical reasoning and evidence
- Severity level assessment

**5. Recommended Investigations** (Only if investigation_plan provided)
- Tests suggested with priority levels
- Purpose and rationale for each test
- Timeline for testing

**6. Treatment Recommendations** (Only if recommendation provided)
- Immediate actions and self-care
- Lifestyle modifications
- Monitoring instructions
- Follow-up schedule

**7. Important Warnings & Next Steps** (Include based on severity)
- Emergency care criteria
- When to contact doctor
- Expected course and timeline

---

## OUTPUT STRUCTURE
Just jump into structure, must not rephrase anything
### 1. Summary Overview
A 2-3 sentence executive summary of the patient's condition and key recommendations.

### 2. Symptoms Analysis
- **Chief Complaint**: Main reason for consultation
- **Key Symptoms**: Important symptoms identified
- **Duration & Severity**: Timeline and intensity
- **Red Flags**: ⚠️ Any urgent warning signs (if present)

### 3. Diagnostic Assessment
- **Primary Diagnosis**: Main medical assessment with confidence level
- **Differential Diagnoses**: Other possibilities considered (if applicable)
- **Clinical Reasoning**: Brief explanation of why this diagnosis
- **Severity Level**: LOW / MODERATE / HIGH / EMERGENCY

### 4. Recommended Investigations
- **Tests Suggested**: List of recommended medical tests/examinations
- **Priority**: Urgent / Routine
- **Purpose**: Why each test is needed

### 5. Treatment Plan & Recommendations
- **Immediate Actions**: What to do now
- **Self-Care Measures**: Home care instructions
- **Lifestyle Modifications**: Changes to support recovery
- **Monitoring Instructions**: What symptoms to watch
- **Follow-Up Schedule**: When to return/recheck

### 6. Important Warnings & Next Steps
- 🚨 **Seek Emergency Care If**: Emergency symptoms to watch for
- ⚠️ **Contact Doctor If**: Non-emergency but concerning symptoms
- 📅 **Follow-Up Timeline**: When to schedule next appointment
- 📋 **Expected Course**: What to expect in recovery

### 7. Patient Education Notes (Optional)
- Brief explanation of the condition
- Relevant health information
- Prevention tips for future

---

## FORMATTING GUIDELINES

### Use Clear Markdown Structure
- **Bold** for emphasis on key terms and actions
- Bullet points for lists
- Emoji indicators: 🚨 (emergency), ⚠️ (warning), ℹ️ (info), ✅ (completed), 📅 (timeline)
- Clear section headers with ##, ###

### Tone & Style
- **Professional but Accessible**: Medical accuracy with plain language
- **Empathetic**: Acknowledge patient concerns
- **Action-Oriented**: Clear next steps
- **Reassuring but Honest**: Don't minimize serious issues

### Length Guidelines
- Concise but complete
- No unnecessary filler content
- Focus on actionable information
- Adapt length to complexity of case

---

## SEVERITY-BASED RESPONSE PATTERNS

### EMERGENCY (Immediate action required)
```
🚨 **URGENT MEDICAL ATTENTION REQUIRED**

**Summary**: [Brief critical assessment]

**Immediate Actions**:
1. Call 911 or go to Emergency Room NOW
2. [Critical symptoms detected]
3. Do not delay seeking care

**Why This Is Urgent**: [Brief explanation]
```

### HIGH SEVERITY (Doctor visit within 24h)
- Start with urgency indicator
- Prioritize when to see doctor
- Brief self-care until appointment

### MODERATE SEVERITY (Doctor visit in few days)
- Balanced information
- Home care emphasis
- When to escalate care

### LOW SEVERITY (Home care/monitoring)
- Focus on self-care
- Monitoring instructions
- When to consider doctor visit

---

## IMPORTANT CONSTRAINTS

1. ⚠️ **Medical Disclaimer**: Always include appropriate disclaimers
2. ⚠️ **Work with What You Have**: Don't apologize for missing information
3. ⚠️ **No Prescriptions**: Don't prescribe specific medications  
4. ⚠️ **Emergency Cases**: Always prioritize immediate care advice
5. ✅ **Actionable**: Every section should have clear actions
6. ✅ **Natural Flow**: Report should read smoothly despite partial information
7. ✅ **Consistent**: Align severity across all sections
8. ✅ **Adaptive**: Include ONLY sections with available data

---

## OUTPUT REQUIREMENTS
- Use proper markdown formatting
- Include ONLY relevant sections based on available data
- Be comprehensive with what you have
- Maintain professional medical tone
- Ensure actionable advice appropriate to information available
- End with appropriate medical disclaimer
- Write in Vietnamese unless otherwise specified
- Do NOT include empty sections or placeholders
"""


def build_synthesis_prompt(state_data: dict) -> str:
    """
    Build synthesis prompt with ONLY available state data.
    Dynamically includes sections based on what information exists.
    
    Args:
        state_data: Dictionary containing all relevant state information
            - symptoms: Extracted symptoms (JSON string or dict)
            - image_analysis_result: Image analysis if available
            - diagnosis: Diagnostic results
            - risk_assessment: Risk assessment
            - investigation_plan: Recommended tests
            - recommendation: Treatment recommendations
            - intent: Original user intent
    
    Returns:
        Complete prompt for synthesis with only relevant sections
    """
    # Extract available data
    diagnosis = state_data.get("diagnosis", {})
    risk_assessment = state_data.get("risk_assessment", {})
    investigation_plan = state_data.get("investigation_plan", [])
    recommendation = state_data.get("recommendation", "")
    image_analysis = state_data.get("image_analysis_result", {})
    symptoms = state_data.get("symptoms", "")
    
    # Build dynamic context based on available information
    context = """Please synthesize the following medical information into a comprehensive Vietnamese final report.

**IMPORTANT**: Only include sections for which data is provided below. Do NOT create empty sections or use placeholders.

---

"""
    
    # Add image analysis if available
    if image_analysis:
        context += "## IMAGE ANALYSIS RESULTS\n"
        context += f"{json.dumps(image_analysis, indent=2, ensure_ascii=False)}\n\n"
    
    # Add symptoms if available
    if symptoms:
        context += "## SYMPTOMS INFORMATION\n"
        if isinstance(symptoms, dict):
            context += f"{json.dumps(symptoms, indent=2, ensure_ascii=False)}\n\n"
        else:
            context += f"{symptoms}\n\n"
    
    # Add diagnosis if available
    if diagnosis:
        context += "## DIAGNOSTIC ASSESSMENT\n"
        context += f"{json.dumps(diagnosis, indent=2, ensure_ascii=False)}\n\n"
    
    # Add risk assessment if available
    if risk_assessment:
        context += "## RISK ASSESSMENT\n"
        context += f"{json.dumps(risk_assessment, indent=2, ensure_ascii=False)}\n\n"
    
    # Add investigation plan if available
    if investigation_plan:
        context += "## RECOMMENDED INVESTIGATIONS\n"
        if isinstance(investigation_plan, list):
            for idx, investigation in enumerate(investigation_plan, 1):
                if isinstance(investigation, dict):
                    context += f"{idx}. **{investigation.get('test_name', 'Unknown')}** "
                    context += f"[{investigation.get('priority', 'routine')}]\n"
                    context += f"   Purpose: {investigation.get('purpose', 'N/A')}\n"
                else:
                    context += f"{idx}. {investigation}\n"
        else:
            context += f"{json.dumps(investigation_plan, indent=2, ensure_ascii=False)}\n"
        context += "\n"
    
    # Add recommendations if available
    if recommendation:
        context += "## TREATMENT RECOMMENDATIONS\n"
        context += f"{recommendation}\n\n"
    
    # Final instruction
    context += """
---

Based on the information provided above, create a comprehensive, patient-friendly final report in Vietnamese.

**KEY INSTRUCTIONS**:
- Include ONLY sections for which data was provided above
- Do NOT create empty sections or use placeholders like "Not provided"
- Maintain clear narrative flow
- Explain medical terms simply  
- Provide actionable next steps appropriate to the information available
- Match severity level across all sections
- Include appropriate urgency indicators if applicable
- End with brief medical disclaimer
"""
    print(context)
    return context
