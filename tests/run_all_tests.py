"""
Run All Tests - Procurement Agent
Execute all module tests sequentially
"""
import sys
sys.path.append('..')

print("=" * 60)
print("Procurement AGENT - COMPLETE TEST SUITE")
print("=" * 60)
print()

# Test 1: Email Detection
print("TEST 1: Email Detection")
print("-" * 60)
from test_email_detection import test_tender_email, test_non_tender_email
try:
    test1 = test_tender_email() and test_non_tender_email()
    print("✅ Email Detection: PASSED\n")
except Exception as e:
    print(f"❌ Email Detection: FAILED - {e}\n")
    test1 = False

# Test 2: Document Classifier
print("TEST 2: Document Classification")
print("-" * 60)
from test_document_classifier import test_classification
try:
    test2 = test_classification()
    print()
except Exception as e:
    print(f"❌ Document Classification: FAILED - {e}\n")
    test2 = False

# Test 3: File Manager
print("TEST 3: File Manager")
print("-" * 60)
from test_file_manager import test_file_manager
try:
    test3 = test_file_manager()
    print()
except Exception as e:
    print(f"❌ File Manager: FAILED - {e}\n")
    test3 = False

# Test 4: Procurement Generator
print("TEST 4: Procurement Generator")
print("-" * 60)
from test_procurement_generator import test_procurement_generator
try:
    test4 = test_procurement_generator()
    print()
except Exception as e:
    print(f"❌ Procurement Generator: FAILED - {e}\n")
    test4 = False

# Test 5: Metadata Extractor
print("TEST 5: Metadata Extractor")
print("-" * 60)
from test_metadata_extractor import test_metadata_extraction
try:
    test5 = test_metadata_extraction()
    print()
except Exception as e:
    print(f"❌ Metadata Extractor: FAILED - {e}\n")
    test5 = False

# Summary
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
tests = [test1, test2, test3, test4, test5]
test_names = [
    "Email Detection",
    "Document Classification",
    "File Manager",
    "Procurement Generator",
    "Metadata Extractor"
]

for name, passed in zip(test_names, tests):
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{name:30} {status}")

total_passed = sum(tests)
print()
print(f"Total: {total_passed}/{len(tests)} tests passed")

if total_passed == len(tests):
    print("\n🎉 ALL TESTS PASSED! Procurement Agent is ready!")
else:
    print(f"\n⚠️ {len(tests) - total_passed} test(s) failed. Please review.")
