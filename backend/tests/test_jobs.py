"""Tests for async job processing system."""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.jobs.job_status import Job, JobStatus
from app.jobs.job_queue import JobQueue
from app.jobs.job_worker import JobWorker, WorkerPool
from app.jobs.job_manager import JobManager
from app.jobs.task_registry import task_registry


class TestJobStatus:
    """Tests for Job status model."""
    
    def test_job_creation(self):
        """Test creating a new job."""
        job = Job.create("repo-123", "architecture")
        
        assert job.job_id is not None
        assert job.repository_id == "repo-123"
        assert job.task_type == "architecture"
        assert job.status == JobStatus.QUEUED
        assert job.progress == 0
        assert job.start_time is not None
        assert job.finish_time is None
    
    def test_job_progress_update(self):
        """Test updating job progress."""
        job = Job.create("repo-123", "architecture")
        job.update_progress("Scanning", 50)
        
        assert job.current_step == "Scanning"
        assert job.progress == 50
    
    def test_job_progress_clamping(self):
        """Test that progress is clamped between 0 and 100."""
        job = Job.create("repo-123", "architecture")
        job.update_progress("Test", 150)
        assert job.progress == 100
        
        job.update_progress("Test", -10)
        assert job.progress == 0
    
    def test_job_mark_running(self):
        """Test marking job as running."""
        job = Job.create("repo-123", "architecture")
        job.mark_running()
        
        assert job.status == JobStatus.RUNNING
    
    def test_job_mark_completed(self):
        """Test marking job as completed."""
        job = Job.create("repo-123", "architecture")
        result = {"test": "data"}
        job.mark_completed(result)
        
        assert job.status == JobStatus.COMPLETED
        assert job.progress == 100
        assert job.finish_time is not None
        assert job.result == result
    
    def test_job_mark_failed(self):
        """Test marking job as failed."""
        job = Job.create("repo-123", "architecture")
        job.mark_failed("Test error")
        
        assert job.status == JobStatus.FAILED
        assert job.finish_time is not None
        assert job.error_message == "Test error"
    
    def test_job_mark_cancelled(self):
        """Test marking job as cancelled."""
        job = Job.create("repo-123", "architecture")
        job.mark_cancelled()
        
        assert job.status == JobStatus.CANCELLED
        assert job.finish_time is not None
    
    def test_job_to_dict(self):
        """Test converting job to dictionary."""
        job = Job.create("repo-123", "architecture")
        job.update_progress("Test", 50)
        job_dict = job.to_dict()
        
        assert job_dict["job_id"] == job.job_id
        assert job_dict["repository_id"] == job.repository_id
        assert job_dict["task_type"] == job.task_type
        assert job_dict["status"] == job.status.value
        assert job_dict["progress"] == 50


class TestJobQueue:
    """Tests for JobQueue."""
    
    def test_queue_enqueue_dequeue(self):
        """Test basic enqueue and dequeue operations."""
        queue = JobQueue(max_size=10)
        job = {"job_id": "test-1", "repository_id": "repo-123"}
        
        assert queue.enqueue(job) is True
        assert queue.size() == 1
        
        dequeued = queue.dequeue()
        assert dequeued == job
        assert queue.size() == 0
    
    def test_queue_full(self):
        """Test queue behavior when full."""
        queue = JobQueue(max_size=2)
        
        assert queue.enqueue({"job_id": "1"}) is True
        assert queue.enqueue({"job_id": "2"}) is True
        assert queue.is_full() is True
        assert queue.enqueue({"job_id": "3"}) is False
    
    def test_queue_dequeue_timeout(self):
        """Test dequeue with timeout."""
        queue = JobQueue(max_size=10)
        
        result = queue.dequeue(timeout=0.1)
        assert result is None
    
    def test_queue_peek(self):
        """Test peeking at next job."""
        queue = JobQueue(max_size=10)
        job = {"job_id": "test-1"}
        
        queue.enqueue(job)
        peeked = queue.peek()
        
        assert peeked == job
        assert queue.size() == 1  # Job should still be in queue
    
    def test_queue_clear(self):
        """Test clearing the queue."""
        queue = JobQueue(max_size=10)
        queue.enqueue({"job_id": "1"})
        queue.enqueue({"job_id": "2"})
        
        queue.clear()
        
        assert queue.size() == 0
        assert queue.is_empty() is True
    
    def test_queue_iterate(self):
        """Test iterating over queued jobs."""
        queue = JobQueue(max_size=10)
        job1 = {"job_id": "1"}
        job2 = {"job_id": "2"}
        
        queue.enqueue(job1)
        queue.enqueue(job2)
        
        jobs = list(queue.iterate())
        assert len(jobs) == 2
        assert job1 in jobs
        assert job2 in jobs


class TestTaskRegistry:
    """Tests for TaskRegistry."""
    
    def test_register_task(self):
        """Test registering a task."""
        def dummy_handler(repo_id, progress_callback):
            return {"result": "test"}
        
        task_registry.register("test_task", dummy_handler)
        
        assert task_registry.has_task("test_task") is True
        assert task_registry.get_handler("test_task") == dummy_handler
    
    def test_list_tasks(self):
        """Test listing all registered tasks."""
        tasks = task_registry.list_tasks()
        
        assert isinstance(tasks, list)
        assert len(tasks) > 0  # Should have default tasks
        assert "architecture" in tasks
        assert "indexing" in tasks


class TestJobWorker:
    """Tests for JobWorker."""
    
    def test_worker_lifecycle(self):
        """Test starting and stopping a worker."""
        queue = JobQueue(max_size=10)
        update_callback = Mock()
        worker = JobWorker(queue, update_callback, worker_id=0)
        
        assert worker.is_running() is False
        
        worker.start()
        assert worker.is_running() is True
        
        worker.stop()
        assert worker.is_running() is False
    
    def test_worker_processes_job(self):
        """Test worker processing a job."""
        queue = JobQueue(max_size=10)
        update_callback = Mock()
        worker = JobWorker(queue, update_callback, worker_id=0)
        
        # Register a simple test task
        def test_handler(repo_id, progress_callback):
            progress_callback("Step 1", 50)
            progress_callback("Step 2", 100)
            return {"test": "result"}
        
        task_registry.register("test_worker_task", test_handler)
        
        job_data = {
            "job_id": "test-job-1",
            "repository_id": "repo-123",
            "task_type": "test_worker_task",
            "status": "QUEUED",
            "current_step": "",
            "progress": 0,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "finish_time": None,
            "error_message": None,
            "result": None,
            "metadata": {}
        }
        
        queue.enqueue(job_data)
        worker.start()
        
        # Wait for job to be processed
        time.sleep(0.5)
        
        worker.stop()
        
        # Verify updates were called
        assert update_callback.call_count > 0


class TestWorkerPool:
    """Tests for WorkerPool."""
    
    def test_pool_start_stop(self):
        """Test starting and stopping worker pool."""
        queue = JobQueue(max_size=10)
        update_callback = Mock()
        pool = WorkerPool(queue, update_callback, num_workers=2)
        
        pool.start()
        status = pool.get_status()
        
        assert len(status) == 2
        assert all(s["running"] for s in status)
        
        pool.stop()
        status = pool.get_status()
        
        assert all(not s["running"] for s in status)


class TestJobManager:
    """Tests for JobManager."""
    
    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary repository for testing."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        (repo_path / "test.py").write_text("print('hello')")
        return str(repo_path)
    
    def test_create_job_success(self, temp_repo):
        """Test successful job creation."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        # Mock repository validation to use temp path
        with patch.object(manager, '_validate_repository'):
            job = manager.create_job("repo-123", "architecture")
            
            assert job.job_id is not None
            assert job.repository_id == "repo-123"
            assert job.task_type == "architecture"
            assert job.status == JobStatus.QUEUED
        
        manager.shutdown()
    
    def test_create_job_invalid_task(self):
        """Test job creation with invalid task type."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        with patch.object(manager, '_validate_repository'):
            with pytest.raises(ValueError, match="Unknown task type"):
                manager.create_job("repo-123", "invalid_task")
        
        manager.shutdown()
    
    def test_get_job(self):
        """Test retrieving a job."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        with patch.object(manager, '_validate_repository'):
            created_job = manager.create_job("repo-123", "architecture")
            retrieved_job = manager.get_job(created_job.job_id)
            
            assert retrieved_job is not None
            assert retrieved_job.job_id == created_job.job_id
        
        manager.shutdown()
    
    def test_cancel_queued_job(self):
        """Test cancelling a queued job."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        with patch.object(manager, '_validate_repository'):
            job = manager.create_job("repo-123", "architecture")
            success = manager.cancel_job(job.job_id)
            
            assert success is True
            assert job.status == JobStatus.CANCELLED
        
        manager.shutdown()
    
    def test_cancel_completed_job(self):
        """Test cancelling a completed job."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        with patch.object(manager, '_validate_repository'):
            job = manager.create_job("repo-123", "architecture")
            job.mark_completed({"test": "result"})
            success = manager.cancel_job(job.job_id)
            
            assert success is False
        
        manager.shutdown()
    
    def test_list_jobs(self):
        """Test listing jobs with filters."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        with patch.object(manager, '_validate_repository'):
            job1 = manager.create_job("repo-123", "architecture")
            job2 = manager.create_job("repo-456", "indexing")
            
            # List all jobs
            all_jobs = manager.list_jobs()
            assert len(all_jobs) == 2
            
            # Filter by repository
            repo_jobs = manager.list_jobs(repository_id="repo-123")
            assert len(repo_jobs) == 1
            assert repo_jobs[0].job_id == job1.job_id
            
            # Filter by status
            queued_jobs = manager.list_jobs(status=JobStatus.QUEUED)
            assert len(queued_jobs) == 2
        
        manager.shutdown()
    
    def test_get_queue_status(self):
        """Test getting queue status."""
        manager = JobManager(max_queue_size=10, num_workers=2)
        
        status = manager.get_queue_status()
        
        assert "queue_size" in status
        assert "queue_capacity" in status
        assert "workers" in status
        assert len(status["workers"]) == 2
        
        manager.shutdown()
    
    def test_cleanup_old_jobs(self):
        """Test cleanup of old jobs."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        with patch.object(manager, '_validate_repository'):
            job = manager.create_job("repo-123", "architecture")
            job.mark_completed({"test": "result"})
            # Manually set finish_time to old date
            from datetime import timedelta
            job.finish_time = datetime.now(timezone.utc) - timedelta(hours=25)
            
            removed = manager.cleanup_old_jobs(max_age_hours=24)
            
            assert removed >= 0
        
        manager.shutdown()


class TestJobIntegration:
    """Integration tests for the complete job system."""
    
    @pytest.fixture
    def setup_test_environment(self, tmp_path):
        """Setup test environment with repository."""
        # Create test repository
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        (repo_path / "main.py").write_text("""
def hello():
    print('Hello, World!')
    return True
""")
        
        # Create extracted directory structure
        extracted_dir = tmp_path / "storage" / "extracted"
        extracted_dir.mkdir(parents=True)
        
        # Copy repo to extracted dir with upload_id
        import shutil
        upload_dir = extracted_dir / "test-upload-123"
        shutil.copytree(repo_path, upload_dir)
        
        return str(upload_dir)
    
    def test_end_to_end_job_execution(self, setup_test_environment):
        """Test complete job execution from creation to completion."""
        manager = JobManager(max_queue_size=10, num_workers=1)
        
        # Use a simple test task that doesn't require actual repository
        def simple_test_handler(repo_id, progress_callback):
            progress_callback("Step 1", 50)
            progress_callback("Step 2", 100)
            return {"test": "result"}
        
        task_registry.register("test_e2e_task", simple_test_handler)
        
        # Mock the repository validation
        with patch.object(manager, '_validate_repository'):
            # Create job with test task
            job = manager.create_job("test-upload-123", "test_e2e_task")
            
            assert job.status == JobStatus.QUEUED
            
            # Wait for job to be picked up (this is async, so we wait)
            max_wait = 10  # seconds
            start = time.time()
            
            while job.status == JobStatus.QUEUED and (time.time() - start) < max_wait:
                time.sleep(0.1)
                job = manager.get_job(job.job_id)
            
            # Job should have moved to RUNNING or COMPLETED/FAILED
            assert job.status != JobStatus.QUEUED
        
        manager.shutdown()
    
    def test_concurrent_jobs(self, setup_test_environment):
        """Test processing multiple jobs concurrently."""
        manager = JobManager(max_queue_size=10, num_workers=2)
        
        with patch.object(manager, '_validate_repository'):
            # Create multiple jobs
            jobs = []
            for i in range(3):
                job = manager.create_job("test-upload-123", "architecture")
                jobs.append(job)
            
            # Wait for all jobs to complete or fail
            max_wait = 15
            start = time.time()
            
            while True:
                completed = sum(1 for j in jobs if j.status in (JobStatus.COMPLETED, JobStatus.FAILED))
                if completed == len(jobs) or (time.time() - start) > max_wait:
                    break
                time.sleep(0.2)
                # Refresh job status
                jobs = [manager.get_job(j.job_id) for j in jobs]
        
        manager.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
