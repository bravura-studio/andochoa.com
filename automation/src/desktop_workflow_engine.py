#!/usr/bin/env python3
"""
Modified Workflow Engine for Claude Desktop Integration
Uses file-based workflows instead of direct API calls
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
from claude_desktop_integration import DesktopWorkflowCoordinator
from utils import load_state, save_state


class DesktopWorkflowEngine:
    """Workflow engine optimized for Claude Desktop integration"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.coordinator = DesktopWorkflowCoordinator()
        
        # Queue management (simplified for desktop workflows)
        self.queue = deque()
        self.processing = False
        self.worker_thread = None
        
        # State management
        self.state_file = self.config.get_state_file('desktop_workflow_engine')
        self.state = self._load_state()
        
        # Performance tracking
        self.metrics = {
            'workflows_processed': 0,
            'workflows_successful': 0,
            'workflows_failed': 0,
            'average_processing_time': 0,
            'last_processed': None,
            'user_interaction_time': 0
        }
        
        # Don't auto-start processing for desktop workflows
        # User interaction required
        self.logger.info("Desktop workflow engine initialized")
    
    def queue_workflow(self, workflow_type: str, trigger_event: str, 
                      file_path: Optional[str] = None, priority: str = 'medium',
                      **kwargs) -> str:
        """Queue a workflow for desktop execution"""
        
        workflow_item = {
            'id': str(uuid4()),
            'workflow_type': workflow_type,
            'trigger_event': trigger_event,
            'file_path': file_path,
            'priority': priority,
            'context': kwargs,
            'status': 'queued',
            'queued_at': datetime.now().isoformat()
        }
        
        self.queue.append(workflow_item)
        
        workflow_id = workflow_item['id']
        self.logger.info(f"Queued desktop workflow {workflow_type} with ID {workflow_id}")
        
        # For desktop workflows, immediately process if it's high priority
        if priority == 'high' or workflow_type == 'generate_weekly_draft':
            self.process_next_workflow()
        
        return workflow_id
    
    def process_next_workflow(self) -> Optional[Dict]:
        """Process the next queued workflow with user interaction"""
        
        if not self.queue:
            self.logger.info("No workflows in queue")
            return None
        
        workflow_item = self.queue.popleft()
        return self.execute_workflow_now(workflow_item)
    
    def execute_workflow_now(self, workflow_item: Dict) -> Dict:
        """Execute a workflow immediately with user interaction"""
        
        workflow_id = workflow_item['id']
        workflow_type = workflow_item['workflow_type']
        
        self.logger.info(f"Executing desktop workflow {workflow_id}: {workflow_type}")
        
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
            
            # Execute workflow with desktop integration
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
                self.logger.info(f"Desktop workflow {workflow_id} completed successfully")
            else:
                self.metrics['workflows_failed'] += 1
                self.logger.error(f"Desktop workflow {workflow_id} failed: {result.get('errors', [])}")
            
            # Update average processing time
            processing_time = workflow_item['processing_time']
            self.metrics['average_processing_time'] = (
                (self.metrics['average_processing_time'] * (self.metrics['workflows_processed'] - 1) + processing_time) /
                self.metrics['workflows_processed']
            )
            self.metrics['last_processed'] = datetime.now().isoformat()
            
            # Save result
            self._save_workflow_result(workflow_item, processing_time)
            
            return workflow_item
            
        except Exception as e:
            self.logger.error(f"Error executing desktop workflow {workflow_id}: {e}")
            
            workflow_item['status'] = 'error'
            workflow_item['error'] = str(e)
            workflow_item['completed_at'] = datetime.now().isoformat()
            
            self.metrics['workflows_failed'] += 1
            return workflow_item
    
    def list_available_workflows(self) -> List[Dict]:
        """List available workflow types for desktop execution"""
        
        workflows = [
            {
                'name': 'analyze_new_content',
                'description': 'Analyze new content and create connections',
                'estimated_time': '5 minutes',
                'user_steps': '1 copy/paste to Claude Desktop'
            },
            {
                'name': 'generate_weekly_draft', 
                'description': 'Generate complete weekly insights draft',
                'estimated_time': '8-12 minutes',
                'user_steps': '1-2 copy/paste interactions'
            },
            {
                'name': 'update_style_profile',
                'description': 'Update style profile from new great-writing',
                'estimated_time': '3 minutes', 
                'user_steps': '1 copy/paste to Claude Desktop'
            },
            {
                'name': 'system_health_check',
                'description': 'Review system performance and optimization',
                'estimated_time': '2 minutes',
                'user_steps': '1 copy/paste to Claude Desktop'
            }
        ]
        
        return workflows
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        
        return {
            'queue_size': len(self.queue),
            'queued_workflows': [
                {
                    'id': item['id'],
                    'workflow_type': item['workflow_type'],
                    'priority': item['priority'],
                    'queued_at': item['queued_at']
                }
                for item in self.queue
            ],
            'metrics': self.metrics.copy()
        }
    
    def _save_workflow_result(self, workflow_result: Dict, processing_time: float):
        """Save workflow result to history"""
        
        # Create workflow history entry
        history_entry = {
            'id': workflow_result.get('id', str(uuid4())),
            'workflow_type': workflow_result.get('workflow_type'),
            'success': workflow_result.get('status') == 'completed',
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'method': 'claude_desktop',
            'agents_executed': len(workflow_result.get('result', {}).get('agents_executed', [])),
            'errors': workflow_result.get('result', {}).get('errors', [])
        }
        
        # Load and update history
        history_file = self.config.get_state_file('desktop_workflow_history')
        history = load_state(history_file, default={'workflows': []})
        
        history['workflows'].append(history_entry)
        
        # Keep only recent history (last 50 workflows for desktop)
        if len(history['workflows']) > 50:
            history['workflows'] = history['workflows'][-50:]
        
        save_state(history_file, history)
    
    def _load_state(self) -> Dict:
        """Load engine state from disk"""
        default_state = {
            'started_at': datetime.now().isoformat(),
            'metrics': self.metrics,
            'version': '1.0-desktop'
        }
        
        return load_state(self.state_file, default=default_state)


# Command-line interface for desktop workflows
def main():
    """Command-line interface for desktop workflows"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Desktop Workflow Engine')
    parser.add_argument('--workflow', choices=[
        'analyze_new_content', 'generate_weekly_draft', 'update_style_profile', 'system_health_check'
    ], help='Execute a specific workflow')
    parser.add_argument('--file', help='File path for content analysis workflows')
    parser.add_argument('--list', action='store_true', help='List available workflows')
    parser.add_argument('--status', action='store_true', help='Show engine status')
    parser.add_argument('--queue', action='store_true', help='Show queue status')
    
    args = parser.parse_args()
    
    engine = DesktopWorkflowEngine()
    
    try:
        if args.list:
            print("Available Desktop Workflows:")
            workflows = engine.list_available_workflows()
            for wf in workflows:
                print(f"\n{wf['name']}:")
                print(f"  Description: {wf['description']}")
                print(f"  Estimated time: {wf['estimated_time']}")
                print(f"  User interaction: {wf['user_steps']}")
        
        elif args.status:
            print("Desktop Workflow Engine Status:")
            status = engine.get_queue_status()
            print(f"  Queue size: {status['queue_size']}")
            print(f"  Workflows processed: {status['metrics']['workflows_processed']}")
            print(f"  Success rate: {status['metrics']['workflows_successful']}/{status['metrics']['workflows_processed']}")
            
        elif args.queue:
            print("Current Queue:")
            status = engine.get_queue_status()
            for wf in status['queued_workflows']:
                print(f"  {wf['id'][:8]}: {wf['workflow_type']} (priority: {wf['priority']})")
        
        elif args.workflow:
            print(f"Starting desktop workflow: {args.workflow}")
            
            # Create workflow item
            workflow_item = {
                'id': str(uuid4()),
                'workflow_type': args.workflow,
                'trigger_event': 'manual',
                'file_path': args.file,
                'priority': 'high',
                'context': {},
                'status': 'queued',
                'queued_at': datetime.now().isoformat()
            }
            
            # Execute immediately
            result = engine.execute_workflow_now(workflow_item)
            
            if result['status'] == 'completed':
                print(f"✅ Workflow completed successfully!")
                print(f"Processing time: {result.get('processing_time', 0):.1f} seconds")
            else:
                print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
                return 1
        
        else:
            print("Desktop Workflow Engine")
            print("Use --help for available options")
            print("\nQuick start:")
            print("  --list                    Show available workflows")
            print("  --workflow weekly_draft   Generate weekly draft")
            print("  --status                  Show engine status")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())