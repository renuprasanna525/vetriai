from .base_agent import BaseAgent


class QAAgent(BaseAgent):

    name = "QA Agent"

    description = (
        "Handles testing, quality assurance, test results, "
        "test cases, defects, regression testing, and quality metrics"
    )

    def can_handle(self, request):

        qa_keywords = [
            "qa",
            "quality assurance",
            "testing",
            "test results",
            "test cases",
            "test case",
            "test execution",
            "quality",
            "regression testing",
            "regression",
            "bug testing",
            "bugs",
            "defects",
            "defect",
            "test coverage",
            "coverage",
            "passed tests",
            "failed tests",
            "tests passed",
            "tests failed",
            "how many tests passed",
            "how many tests failed",
        ]

        request_lower = request.lower()

        return any(keyword in request_lower for keyword in qa_keywords)

    def get_required_permission(self, request):

        return "view_qa"

    def process(self, request, user, credentials=None):

        request_lower = request.lower()

        qa_keywords = [
            "qa",
            "quality assurance",
            "testing",
            "test results",
            "test cases",
            "test case",
            "test execution",
            "quality",
            "regression testing",
            "regression",
            "bug testing",
            "bugs",
            "defects",
            "defect",
            "test coverage",
            "coverage",
            "passed tests",
            "failed tests",
            "tests passed",
            "tests failed",
            "how many tests passed",
            "how many tests failed",
        ]

        if not any(keyword in request_lower for keyword in qa_keywords):
            return {
                "agent": self.name,
                "status": "unsupported",
                "data": {},
                "message": (
                    "The requested QA information " "is not currently supported."
                ),
            }

        data = {
            "total_test_cases": 120,
            "passed_tests": 108,
            "failed_tests": 12,
            "test_coverage": "90%",
        }

        # Focused: Passed Tests

        if (
            "passed test" in request_lower
            or "passed tests" in request_lower
            or "tests passed" in request_lower
            or "test cases passed" in request_lower
            or "test case passed" in request_lower
        ):
            message = f"{data['passed_tests']} test cases passed."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"passed_tests": data["passed_tests"]},
                "message": message,
            }

        # Focused: Failed Tests

        if (
            "failed test" in request_lower
            or "failed tests" in request_lower
            or "tests failed" in request_lower
            or "test cases failed" in request_lower
            or "test case failed" in request_lower
        ):
            message = f"{data['failed_tests']} test cases failed."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"failed_tests": data["failed_tests"]},
                "message": message,
            }

        # Focused: Total Test Cases

        if (
            "total test" in request_lower
            or "total tests" in request_lower
            or "how many test cases" in request_lower
            or "how many test case" in request_lower
        ):
            message = f"There are {data['total_test_cases']} total test cases."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"total_test_cases": data["total_test_cases"]},
                "message": message,
            }

        # Focused: Test Coverage

        if (
            "test coverage" in request_lower
            or "qa coverage" in request_lower
            or "coverage" in request_lower
        ):
            message = f"QA test coverage is {data['test_coverage']}."

            return {
                "agent": self.name,
                "status": "success",
                "data": {"test_coverage": data["test_coverage"]},
                "message": message,
            }

        # Default: QA Summary

        message = (
            "QA Summary:\n"
            f"Total Test Cases: {data['total_test_cases']}\n"
            f"Passed Tests: {data['passed_tests']}\n"
            f"Failed Tests: {data['failed_tests']}\n"
            f"Test Coverage: {data['test_coverage']}"
        )

        return {
            "agent": self.name,
            "status": "success",
            "data": data,
            "message": message,
        }
