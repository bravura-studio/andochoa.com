# YAML Frontmatter Standard

This document defines the standardized frontmatter format used across the Insight Engine system.

## Standard Format

```yaml
---
claude_analysis:
  topics: ["topic1", "topic2", "topic3", "topic4", "topic5"]
  content_type: "struggle" | "win" | "metric" | "theory" | "solution" | "observation"
  entities: ["Entity Name (confidence: 0.9)", "Another Entity (confidence: 0.7)"]
  quality_score: 1-10
  analysis_date: "YYYY-MM-DD"
  key_insights: ["insight 1", "insight 2", "insight 3"]
  training_data_connections:
    great_writing_matches: ["filename1.md", "filename2.md"]
    worldview_matches: ["filename1.md", "filename2.md"]
    style_similarity_score: 0.0-1.0
---
```

## Field Specifications

### Topics (Required)
- **Type**: Array of strings
- **Count**: 3-5 topics recommended
- **Format**: Use clear, business-friendly terms
- **Examples**: ["user onboarding", "pricing strategy", "team management"]

### Content Type (Required)  
- **Type**: String (one of 6 values)
- **Values**: 
  - `struggle`: Problems, challenges, obstacles
  - `win`: Successes, breakthroughs, achievements
  - `metric`: Data, numbers, KPIs, measurements
  - `theory`: Frameworks, concepts, mental models  
  - `solution`: Fixes, approaches, methodologies
  - `observation`: Insights, patterns, reflections

### Entities (Optional)
- **Type**: Array of strings with confidence scores
- **Format**: "Entity Name (confidence: 0.X)"
- **Confidence**: 0.7-1.0 (only include high-confidence entities)
- **Types**: People, companies, tools, frameworks

### Quality Score (Required)
- **Type**: Integer 1-10
- **Criteria**: Based on insight density, clarity, actionability, specificity
- **Scale**: 
  - 1-3: Low quality, vague, limited value
  - 4-6: Moderate quality, some insights
  - 7-8: High quality, valuable insights
  - 9-10: Exceptional quality, breakthrough thinking

### Analysis Date (Required)
- **Type**: String in ISO date format
- **Format**: "YYYY-MM-DD"
- **Purpose**: Track when analysis was performed

### Key Insights (Required)
- **Type**: Array of strings
- **Count**: 2-3 insights recommended
- **Content**: Most valuable takeaways from the content

### Training Data Connections (Optional)
- **great_writing_matches**: Filenames of similar great-writing examples
- **worldview_matches**: Filenames of relevant world-view content
- **style_similarity_score**: 0.0-1.0 similarity to learned style profile

## Usage Notes

### File Integration
- Add this YAML block at the very top of Markdown files
- Preserve existing content below the frontmatter
- Don't modify existing frontmatter fields outside claude_analysis

### Agent Workflow
1. **Analyzer Agent** writes the complete claude_analysis block
2. **Connector Agent** reads this data to create wikilinks
3. **Draftsmith Agent** uses this data to find related content

### Quality Control
- Review generated analysis for accuracy
- Update topics if they're too vague or broad
- Verify entity confidence scores are realistic
- Ensure quality scores reflect actual content value