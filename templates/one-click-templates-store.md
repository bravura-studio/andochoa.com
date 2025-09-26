# One-Click Workflow Templates

*Ready-to-use workflow commands for seamless system operation*

## 🚀 Available One-Click Operations

### **Primary Workflows** (Most Common)

#### 0. **Controlled Voice Capture** 🎤
**Command**: `controlled_voice_capture`  
**Description**: Intelligent voice recording with conversation control and workflow integration  
**Duration**: 3-8 minutes (user-controlled)  
**Output**: Structured voice note ready for weekly workflow integration

**What It Does**:
- Manages recording start/stop with user control
- Provides intelligent conversation management with focus maintenance
- Generates structured output compatible with Analyzer and Connector agents
- Creates action-oriented insights with clear connection hints
- Integrates seamlessly with weekly draft generation workflow

**Template to Use**:
```
I want to start a controlled voice capture session.

Use the Voice Recording Agent to orchestrate:
1. Start voice recording for [struggle/win/observation/brainstorm/metric] session
2. Provide clear recording control (I will say "stop recording" when ready)
3. After transcription, ask if I want to continue with AI conversation
4. If yes, manage focused conversation with checkpoints and user control
5. Generate structured output ready for Analyzer agent and weekly workflow

Please start the controlled voice workflow and give me recording control.
```

#### 1. **Generate Weekly Draft** ⚡
**Command**: `generate_weekly_draft`  
**Description**: Complete end-to-end weekly insight generation  
**Duration**: 5-8 minutes  
**Output**: Publication-ready weekly journal draft

**What It Does**:
- Analyzes last 7 days of activity
- Updates style profile if needed  
- Creates/updates content connections
- Generates complete weekly draft with training data integration
- Provides quality assessment and editing recommendations

**Template to Use**:
```
I want to generate my weekly draft.

Use the Orchestrator Agent to coordinate:
1. Check recent activity (last 7 days)
2. Update style profile if new training data exists
3. Ensure all content is analyzed and connected
4. Generate complete weekly draft using Draftsmith Agent
5. Provide quality assessment and editing time estimate

Please execute the complete workflow and provide the final draft.
```

#### 2. **Process New Content** 📝
**Command**: `process_new_content`  
**Description**: Background analysis and connection of all new files  
**Duration**: 3-5 minutes per file  
**Output**: Analyzed files with YAML frontmatter and wikilinks

**What It Does**:
- Identifies all new/modified files since last processing
- Runs Analyzer Agent to extract semantic metadata
- Runs Connector Agent to create intelligent wikilinks
- Updates system state and connection graph
- Notifies of new insights and connections discovered

**Template to Use**:
```
I want to process all new content in my vault.

Use the Orchestrator Agent to:
1. Identify new or modified files since last analysis
2. Run Analyzer Agent on all new content
3. Run Connector Agent to create connections
4. Update the content graph and system state
5. Provide summary of new insights and connections

Please execute the complete workflow and show me what was processed.
```

#### 3. **Update Training Data** 📚
**Command**: `update_training_data`  
**Description**: Integrate new great-writing or world-view content  
**Duration**: 2-4 minutes  
**Output**: Updated style profile and worldview index

**What It Does**:
- Analyzes new content in training-data folders
- Updates style profile with new great-writing patterns
- Refreshes worldview index for better cross-references
- Optimizes all agent contexts with new knowledge
- Reports on system improvements and new capabilities

**Template to Use**:
```
I want to update my training data and improve the system.

Use the Orchestrator Agent to:
1. Analyze new content in /training-data/great-writing/
2. Run Style Learner Agent to update style profile
3. Update worldview index for new /training-data/world-view/ content
4. Refresh all agent contexts with new training data
5. Report on improvements and new system capabilities

Please execute the training data integration workflow.
```

### **System Management** (Periodic)

#### 4. **System Health Check** 🔍
**Command**: `system_health_check`  
**Description**: Performance review and optimization recommendations  
**Duration**: 1-2 minutes  
**Output**: System health report and improvement suggestions

**Template to Use**:
```
I want a complete system health check and optimization review.

Use the Orchestrator Agent to:
1. Analyze recent workflow performance and success rates
2. Review agent output quality and processing times
3. Check training data utilization and effectiveness
4. Identify optimization opportunities
5. Provide recommendations for system improvements

Please generate a comprehensive system health report.
```

#### 5. **Reset System State** 🔄
**Command**: `reset_system_state`  
**Description**: Clear workflow state and start fresh  
**Duration**: <1 minute  
**Output**: Clean system state ready for new workflows

**Template to Use**:
```
I want to reset the system state and clear any stuck workflows.

Use the Orchestrator Agent to:
1. Clear all active and pending workflow states
2. Reset agent queue and task management
3. Verify all system files are accessible
4. Initialize fresh system state
5. Confirm system ready for new workflows

Please reset and confirm system status.
```

---

## 🎯 Custom Workflow Templates

### **Custom Weekly Draft** (Advanced)
**For specific date ranges or themes**

```
Generate weekly draft for [specific date range] focusing on [specific themes].

Use the Orchestrator Agent to:
1. Analyze content from [start date] to [end date]
2. Focus on themes: [list specific topics/areas]
3. Include connections to [specific content types]
4. Apply [specific style profile preferences]
5. Generate themed weekly insight draft

Context: [provide any specific context or requirements]
```

### **Batch Content Processing** (Advanced)
**For processing specific folders or content types**

```
Process all content in [specific folder/category] for [specific purpose].

Use the Orchestrator Agent to:
1. Target files in [specific location or matching criteria]
2. Apply [specific analysis parameters]
3. Create connections focusing on [specific relationship types]
4. Generate summary of [specific insights or patterns]
5. Prepare for [specific next step or use case]

Parameters: [any specific settings or preferences]
```

---

## 📋 Workflow Execution Checklist

### **Before Running Workflows**
- [ ] Verify vault contains content to process
- [ ] Check that training data folders are populated
- [ ] Confirm all agent templates are available
- [ ] Review current system state for conflicts

### **During Workflow Execution**
- [ ] Monitor progress and agent handoffs
- [ ] Verify each agent completes successfully  
- [ ] Check output quality meets standards
- [ ] Note any errors or optimization opportunities

### **After Workflow Completion**
- [ ] Review final output and quality
- [ ] Update system state and workflow history
- [ ] Log performance metrics and success indicators
- [ ] Plan next workflows or system improvements

---

## 🔧 Troubleshooting Common Issues

### **Workflow Stuck or Not Starting**
1. Check current-workflow-status.md for active workflows
2. Reset system state if needed
3. Verify all required files and contexts exist
4. Try individual agent execution to isolate issues

### **Poor Quality Output**
1. Review style profile currency and accuracy
2. Check training data quality and relevance
3. Verify content connections are meaningful
4. Adjust agent parameters based on feedback

### **Performance Issues**
1. Monitor processing times per agent
2. Check for large files causing delays
3. Optimize batch processing parameters
4. Review queue management efficiency

---

## 📈 Success Metrics

### **Workflow Effectiveness**
- **Completion Rate**: >95% successful workflow completion
- **Processing Time**: Meet target durations consistently
- **Quality Scores**: Maintain or improve output quality
- **User Satisfaction**: Reduced manual work, increased system usage

### **System Performance**
- **Agent Coordination**: Smooth handoffs without data loss
- **Error Recovery**: <5% workflows require manual intervention
- **Learning Speed**: Visible improvements within 2-4 weeks
- **Integration**: Seamless fit with user's weekly routine

The one-click workflows transform complex multi-agent coordination into simple, reliable commands that deliver professional results with minimal effort.