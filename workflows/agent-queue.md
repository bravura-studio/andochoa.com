# Agent Queue Management

*This file manages the coordination and sequencing of agent tasks*

## Current Queue Status: EMPTY ✅
**Last Updated**: {current_date}  
**Queue Processing**: Ready  
**Failed Tasks**: None  

## Queue Management System

### **Queue Structure**
```yaml
queue_status: "ready"
active_tasks: []
pending_tasks: []
completed_tasks: []
failed_tasks: []

processing_rules:
  max_concurrent: 1  # Process one agent at a time
  retry_attempts: 3
  timeout_minutes: 10
  dependency_checking: true
```

## Agent Dependencies & Execution Order

### **Standard Workflow Dependencies**
1. **Style Learner** → Updates style-profile.md → Enables other agents
2. **Analyzer** → Creates YAML frontmatter → Enables Connector  
3. **Connector** → Creates wikilinks → Enriches graph for Draftsmith
4. **Draftsmith** → Uses all previous outputs → Generates final draft

### **Parallel Processing Capabilities**
- **Style Learner** can run independently (training data updates)
- **Analyzer** can process multiple files in batch
- **Connector** requires completed analysis before processing
- **Draftsmith** requires enriched content graph

## Task Templates

### **Task Template Structure**
```yaml
task_id: "unique_identifier"
agent_type: "analyzer|connector|style_learner|draftsmith"
priority: "high|medium|low"
status: "queued|processing|completed|failed"
created_at: "2025-09-17T10:00:00Z"
started_at: null
completed_at: null
dependencies: ["task_id_list"]
input_context: 
  files: ["file1.md", "file2.md"]
  parameters: {}
output_location: "path/to/output"
notes: "additional context"
```

---

## Pre-Defined Workflow Queues

### **Queue 1: Weekly Draft Generation**
```yaml
workflow_name: "weekly_draft_generation"
description: "Complete end-to-end weekly insight generation"

tasks:
  - task_id: "style_check_001"
    agent_type: "style_learner"
    priority: "high"
    action: "verify_style_profile_current"
    dependencies: []

  - task_id: "content_analysis_001"  
    agent_type: "analyzer"
    priority: "high"
    action: "analyze_recent_activity"
    dependencies: []

  - task_id: "connection_update_001"
    agent_type: "connector" 
    priority: "high"
    action: "create_connections_recent_content"
    dependencies: ["content_analysis_001"]

  - task_id: "draft_generation_001"
    agent_type: "draftsmith"
    priority: "high" 
    action: "generate_weekly_draft"
    dependencies: ["style_check_001", "connection_update_001"]

estimated_duration: "5-8 minutes"
success_criteria: "Publication-ready draft with <15min editing needed"
```

### **Queue 2: New Content Processing**
```yaml
workflow_name: "new_content_processing"
description: "Background analysis and connection of new content"

tasks:
  - task_id: "batch_analysis_001"
    agent_type: "analyzer"
    priority: "medium"
    action: "analyze_new_files"
    dependencies: []

  - task_id: "batch_connection_001"
    agent_type: "connector"
    priority: "medium" 
    action: "create_connections_new_content"
    dependencies: ["batch_analysis_001"]

estimated_duration: "3-5 minutes per file"
success_criteria: "All new content analyzed and connected"
```

### **Queue 3: Training Data Integration**
```yaml
workflow_name: "training_data_integration"
description: "Integrate new training data and update system knowledge"

tasks:
  - task_id: "style_update_001"
    agent_type: "style_learner"
    priority: "medium"
    action: "analyze_new_great_writing"
    dependencies: []

  - task_id: "worldview_index_001"
    agent_type: "connector"
    priority: "low"
    action: "update_worldview_index"
    dependencies: []

estimated_duration: "2-4 minutes"
success_criteria: "Training data integrated, style profile updated"
```

---

## Queue Processing Logic

### **Execution Rules**
1. **Check Dependencies**: Ensure all prerequisite tasks completed successfully
2. **Priority Ordering**: Process high → medium → low priority tasks
3. **Resource Management**: One agent active at a time (prevents conflicts)
4. **Error Handling**: Retry failed tasks with exponential backoff
5. **Progress Tracking**: Update status and timestamps throughout execution

### **Quality Gates**
- **Input Validation**: Verify required files and context exist
- **Output Verification**: Confirm agent produced expected results
- **Dependency Check**: Ensure downstream tasks can proceed
- **Performance Monitoring**: Track execution times and success rates

## Queue Operations

### **Add Task to Queue**
```yaml
action: "queue_task"
agent_type: "analyzer"
files: ["new-content.md"]
priority: "medium"
context: "Background processing of user content"
```

### **Process Queue**  
```yaml
action: "process_queue"
max_tasks: 5
timeout_minutes: 30
priority_filter: "high,medium"
```

### **Queue Status Check**
```yaml
action: "queue_status"
include_history: true  
include_performance: true
```

---

## Performance Tracking

### **Queue Metrics**
- **Average Processing Time**: Track per agent and per workflow
- **Success Rate**: Percentage of tasks completed without error
- **Queue Throughput**: Tasks processed per hour/day
- **Dependency Efficiency**: Time spent waiting for prerequisites

### **Optimization Opportunities**  
- **Batch Processing**: Group similar tasks for efficiency
- **Parallel Execution**: Identify safe concurrent operations
- **Caching**: Reuse analysis results when appropriate
- **Resource Allocation**: Optimize agent execution order

---

## Future Queue Sessions

*Queue processing activities will be logged here*

### Session Template:
```
## Queue Session: [Date/Time]
### Workflow: [Name]
### Tasks Processed: [Count] 
### Duration: [Total time]
### Success Rate: [Percentage]
### Issues: [Problems encountered]
### Optimizations: [Improvements identified]
```