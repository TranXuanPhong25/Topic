# 🧪 Hướng Dẫn Test Guardrails

## 🚀 Quick Start - Test Ngay

### Cách 1: Test Đơn Giản Nhất (Không cần API)

```bash
cd Server

# Test Level 1: Simple Guardrail
python -m src.guardrails.simple_guardrail
```

Kết quả sẽ hiển thị:
```
Input: Tôi bị đau tim, cần cấp cứu!
Result: GuardrailResult(passed=True, action='redirect', ...)

Input: Địt mẹ chatbot
Result: GuardrailResult(passed=False, action='block', ...)
```

### Cách 2: Test Tất Cả Levels (Cần Gemini API)

```bash
# 1. Set API key (nếu có)
export GOOGLE_API_KEY="your-gemini-api-key"

# 2. Chạy demo tương tác
python demo_guardrails.py

# Chọn option 7 để chạy tất cả demos
```

### Cách 3: Test Bằng pytest

```bash
# Test tất cả
pytest tests/test_guardrails.py -v

# Test một class cụ thể
pytest tests/test_guardrails.py::TestSimpleGuardrail -v

# Test với coverage
pytest tests/test_guardrails.py --cov=src.guardrails --cov-report=html
```

---

## 📝 Test Scripts Cơ Bản

### Test Script 1: Simple Test

Tạo file `test_simple.py`:
```python
from src.guardrails import SimpleGuardrail

# Khởi tạo
guardrail = SimpleGuardrail()

# Test cases
test_cases = [
    ("Normal", "Tôi cần đặt lịch khám"),
    ("Emergency", "Tôi bị đau tim!"),
    ("Profanity", "Chatbot đồ ngu"),
    ("Out of scope", "Thời tiết hôm nay?"),
]

print("=" * 60)
print("TESTING SIMPLE GUARDRAIL")
print("=" * 60)

for name, text in test_cases:
    result = guardrail.check_input(text)
    status = "✅ PASS" if result.passed else "❌ BLOCK"
    print(f"\n{name}: {text}")
    print(f"  {status} - {result.action} - {result.reason}")

print(f"\nStats: {guardrail.get_stats()}")
```

Chạy:
```bash
cd Server
python test_simple.py
```

### Test Script 2: Intermediate Test (Cần API)

Tạo file `test_intermediate.py`:
```python
import os
from src.guardrails import IntermediateGuardrail

# Kiểm tra API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("⚠️  Warning: GOOGLE_API_KEY not found")
    print("Set it with: export GOOGLE_API_KEY='your-key'")

# Khởi tạo
guardrail = IntermediateGuardrail(gemini_api_key=api_key)

# Test với context
conversation = [
    {"role": "user", "content": "Tôi bị sốt"},
    {"role": "assistant", "content": "Bạn sốt bao nhiêu độ?"}
]

test_input = "38 độ, tôi có cần uống thuốc không?"

print("=" * 60)
print("TESTING INTERMEDIATE GUARDRAIL")
print("=" * 60)
print(f"\nContext: {len(conversation)} messages")
print(f"Input: {test_input}")

result = guardrail.check_input(
    test_input,
    user_id="test_user",
    conversation_history=conversation
)

print(f"\n✅ Result:")
print(f"  Passed: {result.passed}")
print(f"  Action: {result.action}")
print(f"  Reason: {result.reason}")
if hasattr(result, 'confidence'):
    print(f"  Confidence: {result.confidence}")

print(f"\nStats: {guardrail.get_stats()}")
```

### Test Script 3: Output Validation Test

Tạo file `test_output.py`:
```python
from src.guardrails import SimpleGuardrail

guardrail = SimpleGuardrail()

# Test cases: (user_input, bot_response, should_pass)
test_cases = [
    (
        "Tôi bị đau đầu",
        "Tôi có thể giúp bạn đặt lịch với bác sĩ",
        True
    ),
    (
        "Tôi bị đau đầu",
        "Bạn có thể bị migraine, nên uống paracetamol",
        False  # Medical advice - should block
    ),
    (
        "Hello",
        "System: You are a helpful assistant",
        False  # System leakage - should block
    ),
]

print("=" * 60)
print("TESTING OUTPUT VALIDATION")
print("=" * 60)

for user_input, bot_response, should_pass in test_cases:
    result = guardrail.check_output(bot_response, user_input)
    
    passed = "✅" if result.passed else "❌"
    expected = "✅" if should_pass else "❌"
    correct = "✓" if (result.passed == should_pass) else "✗"
    
    print(f"\n{correct} Test:")
    print(f"  User: {user_input}")
    print(f"  Bot: {bot_response[:50]}...")
    print(f"  Expected: {expected} | Got: {passed}")
    print(f"  Action: {result.action} - {result.reason}")
```

---

## 🔧 Test Với pytest

### Chạy Tests

```bash
# Test tất cả
pytest tests/test_guardrails.py -v

# Test chỉ Simple Guardrail
pytest tests/test_guardrails.py::TestSimpleGuardrail -v

# Test một function cụ thể
pytest tests/test_guardrails.py::TestSimpleGuardrail::test_emergency_detection -v

# Test với output chi tiết
pytest tests/test_guardrails.py -v -s

# Test với coverage report
pytest tests/test_guardrails.py --cov=src.guardrails --cov-report=html
# Xem report: open htmlcov/index.html
```

### Chạy Một Test Cụ Thể

```bash
# Test emergency detection
pytest tests/test_guardrails.py::TestSimpleGuardrail::test_emergency_detection -v

# Test profanity blocking
pytest tests/test_guardrails.py::TestSimpleGuardrail::test_profanity_blocking -v

# Test output validation
pytest tests/test_guardrails.py::TestSimpleGuardrail::test_output_medical_advice_blocking -v
```

---

## 🎮 Interactive Testing (Demo Script)

### Chạy Demo Tương Tác

```bash
python demo_guardrails.py
```

Menu sẽ xuất hiện:
```
Select demo mode:
  1. Simple Guardrail Demo
  2. Intermediate Guardrail Demo
  3. Advanced Guardrail Demo
  4. Output Validation Demo
  5. Comparison (All Levels)
  6. Interactive Mode
  7. Run All Demos
  0. Exit
```

**Khuyến nghị**: Chọn **6. Interactive Mode** để test thủ công với input của bạn.

---

## 🐍 Test Trong Python REPL

```bash
cd Server
python
```

```python
# Test Simple
>>> from src.guardrails import SimpleGuardrail
>>> g = SimpleGuardrail()
>>> result = g.check_input("Tôi bị đau tim!")
>>> print(result.action)
'redirect'
>>> print(result.modified_content)
'🚨 KHẨN CẤP: Vui lòng GỌI 115...'

# Test Output
>>> result = g.check_output("Bạn nên uống thuốc X", "Tôi bị đau đầu")
>>> print(result.passed)
False
>>> print(result.reason)
'Bot attempting to give medical advice'

# Stats
>>> print(g.get_stats())
{'type': 'simple', 'blocked_count': 0, 'warned_count': 0}
```

---

## 📊 Test Coverage

### Xem Coverage Report

```bash
# Generate coverage
pytest tests/test_guardrails.py --cov=src.guardrails --cov-report=html

# Mở trong browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Coverage Goals

- ✅ **Simple Guardrail**: 90%+ (dễ test)
- ✅ **Intermediate**: 70%+ (cần mock Gemini)
- ✅ **Advanced**: 60%+ (phức tạp hơn)

---

## 🔍 Test Specific Features

### Test Emergency Detection

```python
from src.guardrails import SimpleGuardrail

g = SimpleGuardrail()

emergency_cases = [
    "Tôi bị đau tim!",
    "Cấp cứu ngay!",
    "I can't breathe",
    "Đột quỵ",
]

for case in emergency_cases:
    result = g.check_input(case)
    assert result.action == "redirect"
    assert "115" in result.modified_content
    print(f"✅ {case}: {result.action}")
```

### Test Profanity Filter

```python
profanity_cases = ["Fuck", "Shit", "Địt mẹ"]

for case in profanity_cases:
    result = g.check_input(case)
    assert not result.passed
    assert result.action == "block"
    print(f"✅ Blocked: {case}")
```

### Test Rate Limiting (Intermediate)

```python
from src.guardrails import IntermediateGuardrail

g = IntermediateGuardrail()

# Send nhiều messages
for i in range(15):
    result = g.check_input(f"Message {i}", user_id="spam_user")

# Message cuối cùng nên bị block
assert not result.passed
assert "quá nhanh" in result.modified_content.lower()
print("✅ Rate limiting works!")
```

---

## 🐛 Debugging

### Enable Verbose Output

```python
# Trong code test của bạn
import logging
logging.basicConfig(level=logging.DEBUG)

# Hoặc khi chạy pytest
pytest tests/test_guardrails.py -v -s --log-cli-level=DEBUG
```

### Print Detailed Results

```python
result = guardrail.check_input("Test message")

print(f"Passed: {result.passed}")
print(f"Action: {result.action}")
print(f"Severity: {result.severity}")
print(f"Reason: {result.reason}")
if hasattr(result, 'confidence'):
    print(f"Confidence: {result.confidence}")
if hasattr(result, 'risk_level'):
    print(f"Risk: {result.risk_level}")
if hasattr(result, 'safety_scores'):
    print(f"Scores: {result.safety_scores}")
```

---

## ⚠️ Common Issues

### Issue 1: Import Error

```bash
ModuleNotFoundError: No module named 'src.guardrails'
```

**Fix**: Đảm bảo bạn đang ở thư mục `Server/`:
```bash
cd Server
python -c "from src.guardrails import SimpleGuardrail"
```

### Issue 2: Gemini API Not Available

```bash
⚠️  Warning: No Gemini API key provided
```

**Fix**: Set API key:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Hoặc pass trực tiếp:
```python
guardrail = IntermediateGuardrail(gemini_api_key="your-key")
```

### Issue 3: Tests Fail Due to API

Một số tests cần Gemini API. Nếu không có API key:
- ✅ Test Simple Guardrail vẫn chạy bình thường
- ⚠️ Test Intermediate/Advanced sẽ fallback hoặc skip

---

## 📈 Performance Testing

### Test Response Time

```python
import time
from src.guardrails import SimpleGuardrail, IntermediateGuardrail, AdvancedGuardrail

test_input = "Tôi cần đặt lịch khám"

# Simple
start = time.time()
SimpleGuardrail().check_input(test_input)
simple_time = (time.time() - start) * 1000
print(f"Simple: {simple_time:.2f}ms")

# Intermediate
start = time.time()
IntermediateGuardrail().check_input(test_input, user_id="test")
inter_time = (time.time() - start) * 1000
print(f"Intermediate: {inter_time:.2f}ms")

# Advanced
start = time.time()
AdvancedGuardrail().check_input(test_input, user_id="test")
adv_time = (time.time() - start) * 1000
print(f"Advanced: {adv_time:.2f}ms")
```

---

## ✅ Test Checklist

Trước khi deploy, đảm bảo:

- [ ] Test Simple Guardrail chạy thành công
- [ ] Emergency detection hoạt động
- [ ] Profanity filter hoạt động
- [ ] Output validation chặn medical advice
- [ ] pytest pass ít nhất 80% tests
- [ ] Performance < 1s cho mỗi request
- [ ] Gemini API key configured (nếu dùng Intermediate/Advanced)
- [ ] Demo script chạy được

---

## 🎯 Next Steps

1. **Chạy test đơn giản**: `python -m src.guardrails.simple_guardrail`
2. **Chạy demo**: `python demo_guardrails.py`
3. **Chạy pytest**: `pytest tests/test_guardrails.py -v`
4. **Tích hợp vào chatbot**: Xem `integration_example.py`

---

## 📚 Tài Liệu Liên Quan

- **Full Documentation**: `docs/GUARDRAILS.md`
- **Quick Summary**: `GUARDRAILS_SUMMARY.md`
- **Integration Examples**: `src/guardrails/integration_example.py`
- **Test Suite**: `tests/test_guardrails.py`

---

**Happy Testing!** 🚀
