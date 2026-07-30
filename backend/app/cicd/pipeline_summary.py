"""Pipeline summary for CI/CD integration engine.

Generates pipeline summaries, health scores, and recommendations.
"""

import logging
from typing import Any

from app.cicd.pipeline_detector import PipelineStructure

logger = logging.getLogger(__name__)


class PipelineSummary:
    """Generates pipeline summaries and health assessments.

    Reuses repository analysis patterns from other modules.
    """

    def __init__(self):
        """Initialize the pipeline summary generator."""
        pass

    def generate_summary(
        self,
        pipeline_structure: PipelineStructure,
        execution_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a comprehensive pipeline summary.

        Args:
            pipeline_structure: Detected pipeline structure.
            execution_data: Optional execution data from provider.

        Returns:
            Dictionary with pipeline summary information.
        """
        health_score = self._calculate_health_score(pipeline_structure, execution_data)
        
        summary = {
            "provider": pipeline_structure.provider,
            "pipeline_health": health_score,
            "summary": {
                "workflows": len(pipeline_structure.files),
                "jobs": len(pipeline_structure.jobs),
                "stages": len(pipeline_structure.stages),
                "deployments": 1 if pipeline_structure.has_deploy else 0,
                "tests": 1 if pipeline_structure.has_test else 0,
            },
            "workflow_inventory": [
                {
                    "path": file.path,
                    "type": file.type,
                }
                for file in pipeline_structure.files
            ],
            "job_statistics": {
                "total_jobs": len(pipeline_structure.jobs),
                "job_names": pipeline_structure.jobs,
            },
            "execution_summary": self._generate_execution_summary(execution_data),
            "readiness": self._assess_readiness(pipeline_structure),
            "recommendations": self._generate_recommendations(
                pipeline_structure,
                execution_data,
            ),
        }

        return summary

    def _calculate_health_score(
        self,
        pipeline_structure: PipelineStructure,
        execution_data: dict[str, Any] | None = None,
    ) -> int:
        """Calculate pipeline health score (0-100).

        Args:
            pipeline_structure: Detected pipeline structure.
            execution_data: Optional execution data from provider.

        Returns:
            Health score between 0 and 100.
        """
        score = 50  # Base score

        # Bonus for having pipeline files
        if pipeline_structure.files:
            score += 20
        else:
            return 0  # No pipeline = 0 health

        # Bonus for having test stage
        if pipeline_structure.has_test:
            score += 10

        # Bonus for having build stage
        if pipeline_structure.has_build:
            score += 10

        # Bonus for having deployment stage
        if pipeline_structure.has_deploy:
            score += 5

        # Bonus for having multiple stages
        if len(pipeline_structure.stages) >= 2:
            score += 5

        # Bonus for having triggers configured
        if pipeline_structure.triggers:
            score += 5

        # Deduction for having secrets references without clear management
        if pipeline_structure.secrets_refs and not execution_data:
            score -= 5

        # Bonus from execution data if available
        if execution_data:
            total_runs = execution_data.get("total_runs", 0) or execution_data.get("total_pipelines", 0) or execution_data.get("total_builds", 0)
            successful_runs = execution_data.get("successful_runs", 0) or execution_data.get("successful_pipelines", 0) or execution_data.get("successful_builds", 0)
            failed_runs = execution_data.get("failed_runs", 0) or execution_data.get("failed_pipelines", 0) or execution_data.get("failed_builds", 0)

            if total_runs > 0:
                success_rate = (successful_runs / total_runs) * 100
                score += int((success_rate - 50) / 2)  # Scale success rate to score
                
                # Deduction for high failure rate
                if total_runs > 10 and (failed_runs / total_runs) > 0.2:
                    score -= 10

        # Ensure score is within bounds
        return max(0, min(100, score))

    def _generate_execution_summary(
        self,
        execution_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate execution summary from provider data.

        Args:
            execution_data: Optional execution data from provider.

        Returns:
            Execution summary dictionary.
        """
        if not execution_data:
            return {
                "status": "no_data",
                "message": "No execution data available",
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate": 0,
            }

        # Normalize different provider response formats
        total_runs = (
            execution_data.get("total_runs") or
            execution_data.get("total_pipelines") or
            execution_data.get("total_builds") or
            0
        )
        
        successful_runs = (
            execution_data.get("successful_runs") or
            execution_data.get("successful_pipelines") or
            execution_data.get("successful_builds") or
            0
        )
        
        failed_runs = (
            execution_data.get("failed_runs") or
            execution_data.get("failed_pipelines") or
            execution_data.get("failed_builds") or
            0
        )

        summary = {
            "status": "available",
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
        }

        # Add last run information if available
        last_run = execution_data.get("last_run") or execution_data.get("last_pipeline") or execution_data.get("last_build")
        if last_run:
            summary["last_run"] = {
                "status": last_run.get("status") or last_run.get("result") or last_run.get("state") or "unknown",
                "timestamp": last_run.get("created_at") or last_run.get("timestamp") or last_run.get("created_on") or "unknown",
            }

        return summary

    def _assess_readiness(self, pipeline_structure: PipelineStructure) -> dict[str, Any]:
        """Assess repository CI/CD readiness.

        Args:
            pipeline_structure: Detected pipeline structure.

        Returns:
            Readiness assessment dictionary.
        """
        readiness = {
            "has_pipeline": len(pipeline_structure.files) > 0,
            "has_build": pipeline_structure.has_build,
            "has_test": pipeline_structure.has_test,
            "has_deploy": pipeline_structure.has_deploy,
            "has_triggers": len(pipeline_structure.triggers) > 0,
            "score": 0,
            "level": "none",
        }

        # Calculate readiness score
        score = 0
        if readiness["has_pipeline"]:
            score += 25
        if readiness["has_build"]:
            score += 25
        if readiness["has_test"]:
            score += 25
        if readiness["has_deploy"]:
            score += 15
        if readiness["has_triggers"]:
            score += 10

        readiness["score"] = score

        # Determine readiness level
        if score >= 80:
            readiness["level"] = "excellent"
        elif score >= 60:
            readiness["level"] = "good"
        elif score >= 40:
            readiness["level"] = "basic"
        elif score >= 20:
            readiness["level"] = "minimal"
        else:
            readiness["level"] = "none"

        return readiness

    def _generate_recommendations(
        self,
        pipeline_structure: PipelineStructure,
        execution_data: dict[str, Any] | None = None,
    ) -> list[str]:
        """Generate pipeline improvement recommendations.

        Args:
            pipeline_structure: Detected pipeline structure.
            execution_data: Optional execution data from provider.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        # Check for missing pipeline
        if not pipeline_structure.files:
            recommendations.append("No CI/CD pipeline detected. Consider setting up a pipeline for automated builds and tests.")
            return recommendations

        # Check for missing build stage
        if not pipeline_structure.has_build:
            recommendations.append("Add a build stage to compile and build your project.")

        # Check for missing test stage
        if not pipeline_structure.has_test:
            recommendations.append("Add automated tests to your pipeline to ensure code quality.")

        # Check for missing deployment stage
        if not pipeline_structure.has_deploy:
            recommendations.append("Consider adding a deployment stage for automated deployments.")

        # Check for missing triggers
        if not pipeline_structure.triggers:
            recommendations.append("Configure pipeline triggers (e.g., on push, pull request) for automated execution.")

        # Check for secrets management
        if pipeline_structure.secrets_refs:
            recommendations.append("Ensure secrets are properly managed using provider secret management.")

        # Check execution data for issues
        if execution_data:
            total_runs = execution_data.get("total_runs") or execution_data.get("total_pipelines") or execution_data.get("total_builds") or 0
            failed_runs = execution_data.get("failed_runs") or execution_data.get("failed_pipelines") or execution_data.get("failed_builds") or 0

            if total_runs > 10 and (failed_runs / total_runs) > 0.2:
                recommendations.append("High failure rate detected. Review failed runs and fix common issues.")

            if total_runs == 0:
                recommendations.append("No pipeline executions found. Ensure your pipeline is triggered correctly.")

        # Check for artifacts
        if not pipeline_structure.artifacts and pipeline_structure.has_build:
            recommendations.append("Consider storing build artifacts for later use or debugging.")

        # Provider-specific recommendations
        if pipeline_structure.provider == "github":
            recommendations.append("Enable dependency caching in GitHub Actions to speed up builds.")
        elif pipeline_structure.provider == "gitlab":
            recommendations.append("Use GitLab CI/CD caching to improve pipeline performance.")
        elif pipeline_structure.provider == "jenkins":
            recommendations.append("Consider using Jenkins shared libraries for common pipeline logic.")

        # General best practices
        if len(pipeline_structure.files) > 1:
            recommendations.append("Consider separating build and deployment workflows for better modularity.")

        return recommendations


pipeline_summary = PipelineSummary()
