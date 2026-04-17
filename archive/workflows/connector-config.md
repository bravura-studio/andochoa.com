# Connector Agent Configuration

This file defines the rules and thresholds used by the Connector Agent for creating wikilinks.

## Confidence Thresholds

### Current Settings
- **High Confidence (Auto-Create)**: ≥8/10
- **Medium Confidence (Auto-Create)**: ≥7/10  
- **Low Confidence (Skip)**: <7/10

### Confidence Calculation Rules

#### Topic Overlap Scoring
- **3+ shared topics**: +3 points
- **2 shared topics**: +2 points
- **1 shared topic**: +1 point

#### Entity Matching Scoring
- **Same high-confidence entity (≥0.8)**: +2 points
- **Same medium-confidence entity (0.7-0.8)**: +1 point
- **Multiple entity matches**: +1 additional point

#### Content Type Synergy
- **Perfect pairs** (struggle↔solution, theory↔example): +2 points
- **Learning pairs** (struggle↔win, theory↔observation): +1 point
- **Related types** (metric↔solution, win↔theory): +1 point

#### Quality Alignment
- **Similar quality scores (within 1 point)**: +1 point
- **Same quality tier (both 7-10 or both 4-6)**: +0.5 points

#### Training Data Support
- **World-view connection exists**: +1 point
- **Great-writing style match**: +0.5 points

## Link Creation Limits

### Per-File Limits
- **Maximum internal links**: 5 per file
- **Maximum training data references**: 3 per file
- **Total links per file**: 8 maximum

### Quality Controls
- **Minimum topic overlap**: 1 shared topic required
- **Entity confidence threshold**: 0.7 minimum for entity-based links
- **Bidirectional linking**: Consider reverse links for 8+ confidence scores

## Link Placement Rules

### Preferred Insertion Points
1. First mention of related concept in content
2. Natural context where link adds value  
3. End of relevant paragraphs
4. Key insights or conclusions sections

### Avoid Placement In
- YAML frontmatter blocks
- Code blocks or technical syntax
- Already dense link areas (>2 links per paragraph)
- Mid-sentence unless very natural

## Training Data Integration

### World-View References
- **Format**: `See also: [[training-data/world-view/filename|Display Name]]`
- **Placement**: End of relevant sections
- **Trigger**: Topic overlap + quality alignment

### Great-Writing References  
- **Format**: `Writing inspiration: [[training-data/great-writing/filename|Example]]`
- **Placement**: Comments or meta-sections
- **Trigger**: Style similarity score ≥0.7

## Customization Guidelines

### Increasing Link Sensitivity
- Lower confidence thresholds (≥6/10 for medium confidence)
- Reduce topic overlap requirements
- Increase per-file link limits

### Decreasing Link Sensitivity  
- Raise confidence thresholds (≥8/10 for medium confidence)
- Require more topic overlap (≥2 topics for any link)
- Decrease per-file link limits

### Focus Areas
- **Topic-focused**: Weight topic overlap scoring higher
- **Entity-focused**: Weight entity matching higher
- **Quality-focused**: Require similar quality scores
- **Training-focused**: Emphasize world-view connections

## Testing & Iteration

### After Each Test Session
1. Review link quality and relevance
2. Adjust thresholds based on results
3. Update this configuration file
4. Test with new settings

### Success Indicators
- **Relevance**: >85% of created links feel valuable
- **Natural flow**: Links don't disrupt reading
- **Discovery**: Links help find related insights
- **Balance**: Not too many or too few connections

## Version History

### v1.0 - Initial Configuration
- High confidence: ≥8/10
- Medium confidence: ≥7/10
- Max internal links: 5 per file
- Max training data refs: 3 per file

### Future Versions
*Track changes to thresholds and rules based on testing results*