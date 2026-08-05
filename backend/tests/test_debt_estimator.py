"""Tests for the debt estimator."""

import pytest

from app.smells.debt_estimator import debt_estimator, DebtEstimator, DebtEstimate


@pytest.fixture
def estimator() -> DebtEstimator:
    """Fixture for the debt estimator."""
    return DebtEstimator()


class TestDebtEstimator:
    """Tests for the DebtEstimator class."""

    def test_estimate_no_smells(self, estimator: DebtEstimator) -> None:
        """Test estimation with no smells."""
        result = estimator.estimate([])

        assert isinstance(result, DebtEstimate)
        assert result.level == "low"
        assert result.estimated_effort == "< 1 day"
        assert result.affected_files == 0
        assert result.refactoring_priority == "low"

    def test_estimate_minor_smells(self, estimator: DebtEstimator) -> None:
        """Test estimation with minor smells."""
        smells = [
            {"severity": "minor", "file": "test.py"},
            {"severity": "minor", "file": "test2.py"},
        ]

        result = estimator.estimate(smells)

        assert result.level == "low"
        assert result.affected_files == 2

    def test_estimate_major_smells(self, estimator: DebtEstimator) -> None:
        """Test estimation with major smells."""
        smells = [
            {"severity": "major", "file": "test.py"},
            {"severity": "major", "file": "test2.py"},
            {"severity": "major", "file": "test3.py"},
            {"severity": "major", "file": "test4.py"},
            {"severity": "major", "file": "test5.py"},
        ]

        result = estimator.estimate(smells)

        assert result.level == "medium"
        assert result.affected_files == 5

    def test_estimate_critical_smells(self, estimator: DebtEstimator) -> None:
        """Test estimation with critical smells."""
        smells = [
            {"severity": "critical", "file": "test.py"},
        ]

        result = estimator.estimate(smells)

        assert result.level == "high"
        assert result.refactoring_priority == "high"

    def test_estimate_multiple_critical(self, estimator: DebtEstimator) -> None:
        """Test estimation with multiple critical smells."""
        smells = [
            {"severity": "critical", "file": "test.py"},
            {"severity": "critical", "file": "test2.py"},
            {"severity": "critical", "file": "test3.py"},
        ]

        result = estimator.estimate(smells)

        assert result.level == "critical"
        assert result.refactoring_priority == "critical"

    def test_estimate_mixed_severities(self, estimator: DebtEstimator) -> None:
        """Test estimation with mixed severities."""
        smells = [
            {"severity": "critical", "file": "test.py"},
            {"severity": "major", "file": "test2.py"},
            {"severity": "minor", "file": "test3.py"},
        ]

        result = estimator.estimate(smells)

        assert result.affected_files == 3
        assert result.level in ["high", "critical"]

    def test_estimate_effort_calculation(self, estimator: DebtEstimator) -> None:
        """Test effort estimation based on debt score."""
        # High debt score
        smells = [{"severity": "critical", "file": f"test{i}.py"} for i in range(10)]
        result = estimator.estimate(smells)
        assert "weeks" in result.estimated_effort

        # Low debt score
        smells = [{"severity": "minor", "file": "test.py"}]
        result = estimator.estimate(smells)
        assert "day" in result.estimated_effort

    def test_estimate_affected_files(self, estimator: DebtEstimator) -> None:
        """Test affected files counting."""
        smells = [
            {"severity": "minor", "file": "test.py"},
            {"severity": "minor", "file": "test.py"},  # Same file
            {"severity": "major", "file": "test2.py"},
        ]

        result = estimator.estimate(smells)

        assert result.affected_files == 2  # Unique files

    def test_determine_priority(self, estimator: DebtEstimator) -> None:
        """Test priority determination."""
        # Critical level
        priority = estimator._determine_priority("critical", 2, 0)
        assert priority == "critical"

        # High level
        priority = estimator._determine_priority("high", 1, 0)
        assert priority == "high"

        # Medium level
        priority = estimator._determine_priority("medium", 0, 5)
        assert priority == "medium"

        # Low level
        priority = estimator._determine_priority("low", 0, 0)
        assert priority == "low"

    def test_estimate_effort_with_many_files(self, estimator: DebtEstimator) -> None:
        """Test effort estimation with many affected files."""
        smells = [{"severity": "major", "file": f"test{i}.py"} for i in range(25)]

        result = estimator.estimate(smells)

        assert result.affected_files == 25
        # Should adjust effort for many files
