# Image Capture Instructions for Experiment Alpha

## 📸 Required Screenshots for Experiment_Alpha_EmailManagementAgent.md

Save all images as PNG files in: `/Users/fabswill/ReposClaudeCode/braintrustdevdeepdive/images/`

### Image 1: Timeline Overview
**Filename**: `alpha_timeline_overview.png`
**Location**: Braintrust UI → Your Project → Logs → Click on trace ID → Timeline tab
**What to Capture**:
- Full timeline view showing the complete multi-step workflow
- Should show decision_step, tool_execution_step, judgment_step, composition_step
- Include timing information and token counts
- Make sure the workflow pattern is clearly visible

### Image 2: Span Details
**Filename**: `alpha_span_details.png`
**Location**: Timeline view → Click on any individual span (preferably decision_step)
**What to Capture**:
- Detailed span information panel
- Input/output data
- Metadata fields (model, temperature, etc.)
- Custom attributes if visible
- Make sure span name and duration are visible

### Image 3: Token Usage Chart
**Filename**: `alpha_token_usage.png`
**Location**: Logs view → Click on experiment or trace with metrics
**What to Capture**:
- Token consumption visualization
- Completion tokens vs total tokens
- Any charts showing token usage breakdown
- Performance metrics if available

### Image 4: Evaluation Summary
**Filename**: `alpha_eval_summary.png`
**Location**: Projects → Experiments → Your email management experiment
**What to Capture**:
- Experiment results table
- Scores and metrics
- Any comparison data between runs
- Success/failure indicators
- Overall evaluation summary

### Image 5: Zero Inbox Results
**Filename**: `alpha_zero_inbox_results.png`
**Location**: Logs → Find trace for "Get all my inboxes to zero" query → Output section
**What to Capture**:
- Agent's response showing email processing results
- Account-by-account breakdown
- Email counts and categorization
- The formatted table showing results per account

### Image 6: Trace Tree Structure
**Filename**: `alpha_trace_tree.png`
**Location**: Timeline view → Thread tab (or Tree view if available)
**What to Capture**:
- Hierarchical view of spans
- Parent-child relationships
- Span names and structure
- Duration information
- Clear hierarchy visualization

### Image 7: Custom Attributes
**Filename**: `alpha_custom_attributes.png`
**Location**: Span details → Metadata or Attributes section
**What to Capture**:
- Email-specific attributes (email.operation.type, agent.step, etc.)
- Custom semantic conventions
- Attribute values and types
- Any email domain-specific metadata

## 🎯 Screenshot Tips

1. **Use Full Browser Window**: Maximize Braintrust UI for clear visibility
2. **Hide Sensitive Data**: Blur any API keys or sensitive information
3. **High Resolution**: Use high DPI settings for crisp images
4. **Consistent Theme**: Use same Braintrust UI theme for all screenshots
5. **Focus Areas**: Crop to relevant sections, avoid excessive whitespace
6. **Readable Text**: Ensure all text is legible at document viewing size

## 📂 File Organization

After capturing, your images folder should contain:
```
images/
├── alpha_timeline_overview.png
├── alpha_span_details.png
├── alpha_token_usage.png
├── alpha_eval_summary.png
├── alpha_zero_inbox_results.png
├── alpha_trace_tree.png
└── alpha_custom_attributes.png
```

## 🔄 Future Experiments

For subsequent experiments, use this naming pattern:
- **Experiment Bravo**: `bravo_*.png`
- **Experiment Charlie**: `charlie_*.png`
- **Experiment Delta**: `delta_*.png`

Or date-based:
- **2025-09-28**: `20250928_*.png`
- **2025-09-29**: `20250929_*.png`

This ensures clean organization and prevents filename conflicts across experiments.

## ✅ Verification

After capturing all images:
1. Check that all 7 files exist in the images folder
2. Verify each image clearly shows the described content
3. Confirm images display properly when viewing the markdown file
4. Ensure file sizes are reasonable (< 2MB each typically)

These images will complete the documentation and provide visual evidence of the experiment's success!