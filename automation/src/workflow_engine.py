#!/usr/bin/env python3
"""
Workflow Engine - Manages and executes automated workflows
Coordinates agent execution, queue management, and result processing
"""

import json
import logging
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from config import get_config
from claude_integration import AgentCoordinator
from utils import load_state, save_state


class WorkflowQueue:
    """Thread-safe workflow queue with priority management"""
    
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
        self.priorities = {'high': 0, 'medium': 1, 'low': 2}
        
    def add(self, workflow_item: Dict):
        """Add workflow item to queue"""
        with self.lock:
            # Add timestamp and ID if not present
            if 'id' not in workflow_item:
                workflow_item['id'] = str(uuid4())
            if 'queued_at' not in workflow_item:
                workflow_item['queued_at'] = datetime.now().isoformat()
            if 'priority' not in workflow_item:
                workflow_item['priority'] = 'medium'
                
            self.queue.append(workflow_item)
            self._sort_by_priority()
    
    def get_next(self) -> Optional[Dict]:
        """Get next workflow item from queue"""
        with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None
    
    def size(self) -> int:
        """Get current queue size"""
        with self.lock:
            return len(self.queue)
    
    def peek(self) -> Optional[Dict]:
        """Peek at next item without removing it"""
        with self.lock:
            if self.queue:
                return self.queue[0]
            return None
    
    def clear(self):
        """Clear all items from queue"""
        with self.lock:
            self.queue.clear()
    
    def _sort_by_priority(self):
        """Sort queue by priority"""
        self.queue = deque(sorted(
            self.queue,
            key=lambda x: self.priorities.get(x.get('priority', 'medium'), 1)
        ))
    
    def to_list(self) -> List[Dict]:
        """Get queue contents as list"""
        with self.lock:
            return list(self.queue)


class WorkflowEngine:
    """Main workflow engine for processing automated tasks"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.coordinator = AgentCoordinator()
        
        # Queue management
        self.queue = WorkflowQueue()
        self.processing = False
        self.worker_thread = None
        
        # State management
        self.state_file = self.config.get_state_file('workflow_engine')
        self.state = self._load_state()
        
        # Performance tracking
        self.metrics = {
            'workflows_processed': 0,
            'workflows_successful': 0,
            'workflows_failed': 0,
            'average_processing_time': 0,
            'last_processed': None
        }
        
        # Start processing thread
        self.start_processing()
    
    def start_processing(self):
        """Start the workflow processing thread"""
        if not self.processing:
            self.processing = True
            self.worker_thread = threading.Thread(target=self._process_workflows, daemon=True)
            self.worker_thread.start()
            self.logger.info("Workflow engine processing started")
    
    def stop_processing(self):
        """Stop the workflow processing thread"""
        if self.processing:
            self.processing = False
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=10)
            self.logger.info("Workflow engine processing stopped")
    
    def queue_workflow(self, workflow_type: str, trigger_event: str, 
                      file_path: Optional[str] = None, priority: str = 'medium',
                      **kwargs) -> str:
        """Queue a workflow for execution"""
        
        workflow_item = {
            'workflow_type': workflow_type,
            'trigger_event': trigger_event,
            'file_path': file_path,
            'priority': priority,
            'context': kwargs,
            'status': 'queued'
        }
        
        self.queue.add(workflow_item)
        
        workflow_id = workflow_item['id']
        self.logger.info(f"Queued workflow {workflow_type} with ID {workflow_id}")
        
        return workflow_id
    
    def execute_workflow_now(self, workflow_type: str, context: Dict) -> Dict:
        """Execute a workflow immediately (bypass queue)"""
        self.logger.info(f"Executing workflow immediately: {workflow_type}")
        
        start_time = time.time()
        result = self.coordinator.execute_workflow(workflow_type, context)
        end_time = time.time()
        
        # Update metrics
        self.metrics['workflows_processed'] += 1
        if result.get('success'):
            self.metrics['workflows_successful'] += 1
        else:
            self.metrics['workflows_failed'] += 1
        
        processing_time = end_time - start_time
        self.metrics['average_processing_time'] = (
            (self.metrics['average_processing_time'] * (self.metrics['workflows_processed'] - 1) + processing_time) /
            self.metrics['workflows_processed']
        )
        self.metrics['last_processed'] = datetime.now().isoformat()
        
        # Save result
        self._save_workflow_result(result, processing_time)
        
        return result
    
    def _process_workflows(self):
        """Main workflow processing loop"""
        self.logger.info("Starting workflow processing loop")
        
        while self.processing:
            try:
                # Check for queued workflows
                workflow_item = self.queue.get_next()
                
                if workflow_item:
                    self._execute_queued_workflow(workflow_item)
                else:
                    # No workflows to process, sleep briefly
                    time.sleep(1)
                
                # Periodic maintenance
                self._periodic_maintenance()
                
            except Exception as e:
                self.logger.error(f"Error in workflow processing loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _execute_queued_workflow(self, workflow_item: Dict):
        """Execute a queued workflow item"""
        workflow_id = workflow_item['id']
        workflow_type = workflow_item['workflow_type']
        
        self.logger.info(f"Processing workflow {workflow_id}: {workflow_type}")
        
        # Update status
        workflow_item['status'] = 'processing'
        workflow_item['started_at'] = datetime.now().isoformat()
        
        try:
            # Prepare context
            context = workflow_item.get('context', {})
            context.update({
                'workflow_id': workflow_id,
                'trigger_event': workflow_item.get('trigger_event'),
                'file_path': workflow_item.get('file_path'),
                'queued_at': workflow_item.get('queued_at'),
                'priority': workflow_item.get('priority', 'medium')
            })
            
            # Execute workflow
            start_time = time.time()
            result = self.coordinator.execute_workflow(workflow_type, context)
            end_time = time.time()
            
            # Update workflow item with results
            workflow_item['status'] = 'completed' if result.get('success') else 'failed'
            workflow_item['completed_at'] = datetime.now().isoformat()
            workflow_item['processing_time'] = end_time - start_time
            workflow_item['result'] = result
            
            # Update metrics
            self.metrics['workflows_processed'] += 1
            if result.get('success'):
                self.metrics['workflows_successful'] += 1
                self.logger.info(f"Workflow {workflow_id} completed successfully")
            else:
                self.metrics['workflows_failed'] += 1
                self.logger.error(f"Workflow {workflow_id} failed: {result.get('errors', [])}")
            
            # Update average processing time
            processing_time = workflow_item['processing_time']
            self.metrics['average_processing_time'] = (
                (self.metrics['average_processing_time'] * (self.metrics['workflows_processed'] - 1) + processing_time) /
                self.metrics['workflows_processed']
            )
            self.metrics['last_processed'] = datetime.now().isoformat()
            
            # Save result
            self._save_workflow_result(workflow_item, processing_time)
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {e}")
            
            workflow_item['status'] = 'error'
            workflow_item['error'] = str(e)
            workflow_item['completed_at'] = datetime.now().isoformat()
            
            self.metrics['workflows_failed'] += 1
    
    def _save_workflow_result(self, workflow_result: Dict, processing_time: float):
        """Save workflow result to history"""
        
        # Create workflow history entry
        history_entry = {
            'id': workflow_result.get('id', str(uuid4())),
            'workflow_type': workflow_result.get('workflow_type'),
            'success': workflow_result.get('success', False),
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'agents_executed': len(workflow_result.get('agents_executed', [])),
            'errors': workflow_result.get('errors', [])
        }
        
        # Load and update history
        history_file = self.config.get_state_file('workflow_history')
        history = load_state(history_file, default={'workflows': []})
        
        history['workflows'].append(history_entry)
        
        # Keep only recent history (last 100 workflows)
        if len(history['workflows']) > 100:
            history['workflows'] = history['workflows'][-100:]
        
        save_state(history_file, history)
        
        # Save detailed result if successful
        if workflow_result.get('success'):
            result_file = self.config.state_dir / f"workflow_result_{history_entry['id']}.json"
            save_state(result_file, workflow_result)
    
    def _periodic_maintenance(self):
        """Perform periodic maintenance tasks"""
        
        # Save state every 60 seconds
        if not hasattr(self, '_last_state_save'):
            self._last_state_save = 0
            
        current_time = time.time()
        if current_time - self._last_state_save > 60:
            self.state['metrics'] = self.metrics
            self.state['queue_size'] = self.queue.size()
            self.state['last_heartbeat'] = datetime.now().isoformat()
            self._save_state()
            self._last_state_save = current_time
        
        # Clean up old result files (older than 30 days)
        if not hasattr(self, '_last_cleanup'):
            self._last_cleanup = 0
            
        if current_time - self._last_cleanup > 86400:  # Once per day
            self._cleanup_old_results()
            self._last_cleanup = current_time
    
    def _cleanup_old_results(self):
        """Clean up old workflow result files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for result_file in self.config.state_dir.glob("workflow_result_*.json"):
                if result_file.stat().st_mtime < cutoff_date.timestamp():
                    result_file.unlink()
                    self.logger.debug(f"Cleaned up old result file: {result_file}")
                    
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> Dict:
        """Get current workflow engine status"""
        return {
            'processing': self.processing,
            'queue_size': self.queue.size(),
            'metrics': self.metrics.copy(),
            'next_workflow': self.queue.peek(),
            'last_heartbeat': self.state.get('last_heartbeat'),
            'uptime': self._calculate_uptime()
        }
    
    def get_queue_status(self) -> List[Dict]:
        """Get current queue contents"""
        return self.queue.to_list()
    
    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get recent workflow history"""
        history_file = self.config.get_state_file('workflow_history')
        history = load_state(history_file, default={'workflows': []})
        
        return history['workflows'][-limit:]
    
    def is_healthy(self) -> bool:
        """Check if workflow engine is healthy"""
        try:
            # Check if processing thread is alive
            if not self.processing or not self.worker_thread or not self.worker_thread.is_alive():
                return False
            
            # Check if we've processed something recently (within last hour)
            if self.metrics.get('last_processed'):
                last_processed = datetime.fromisoformat(self.metrics['last_processed'])
                if datetime.now() - last_processed > timedelta(hours=1):
                    # Only unhealthy if queue has items but nothing processed
                    if self.queue.size() > 0:
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _calculate_uptime(self) -> Optional[str]:
        """Calculate engine uptime"""
        start_time = self.state.get('started_at')
        if start_time:
            uptime = datetime.now() - datetime.fromisoformat(start_time)
            return str(uptime).split('.')[0]  # Remove microseconds
        return None
    
    def _load_state(self) -> Dict:
        """Load engine state from disk"""
        default_state = {
            'started_at': datetime.now().isoformat(),
            'metrics': self.metrics,
            'version': '1.0'
        }
        
        return load_state(self.state_file, default=default_state)
    
    def _save_state(self):
        """Save engine state to disk"""
        save_state(self.state_file, self.state)


# Predefined workflow templates
WORKFLOW_TEMPLATES = {
    'analyze_new_content': {
        'description': 'Analyze new content and create connections',
        'agents': ['analyzer', 'connector'],
        'priority': 'medium',
        'timeout': 300
    },
    
    'update_style_profile': {
        'description': 'Update style profile from new great-writing',
        'agents': ['style-learner'],
        'priority': 'low',
        'timeout': 180
    },
    
    'update_worldview_index': {
        'description': 'Update worldview index from new bookmarks',
        'agents': ['connector'],
        'priority': 'low',
        'timeout': 120
    },
    
    'integrate_published_content': {
        'description': 'Integrate published content into knowledge base',
        'agents': ['analyzer', 'connector'],
        'priority': 'medium',
        'timeout': 240
    },
    
    'generate_weekly_draft': {
        'description': 'Generate weekly insight draft',
        'agents': ['analyzer', 'connector', 'style-learner', 'draftsmith'],
        'priority': 'high',
        'timeout': 600
    }
}


def main():
    """Test workflow engine functionality"""
    engine = WorkflowEngine()
    
    try:
        print("Workflow Engine Status:")
        status = engine.get_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Wait for user input
        input("\nPress Enter to stop the engine...")
        
    finally:
        engine.stop_processing()


if __name__ == "__main__":
    main()