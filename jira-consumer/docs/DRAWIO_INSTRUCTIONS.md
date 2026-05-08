# How to Create the Architecture Diagram in Draw.io

This document provides instructions for creating the architecture diagram in Draw.io based on the Mermaid diagrams in [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md).

## Option 1: Import Mermaid Diagram (Easiest)

1. Open [Draw.io](https://app.diagrams.net/)
2. Click **File → Import from → Text**
3. Copy the Mermaid diagram from [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md)
4. Paste into the import dialog
5. Click **Import**
6. Draw.io will automatically convert the Mermaid diagram

## Option 2: Manual Creation

### Step 1: Create New Diagram

1. Go to https://app.diagrams.net/
2. Choose where to save (Device, Google Drive, OneDrive, etc.)
3. Create a new blank diagram
4. Name it: `jira-consumer-architecture`

### Step 2: Add Containers (Swimlanes)

Create 5 swimlanes for different system components:

1. **Jira Cloud** (Blue - #0052CC)
   - Add rectangle shape
   - Label: "Jira Cloud"
   - Background: Light blue

2. **Webhook Service** (Green - #00875A)
   - Add rectangle shape
   - Label: "Webhook Service"
   - Background: Light green

3. **Kafka Cluster** (Black - #231F20)
   - Add rectangle shape
   - Label: "Kafka Cluster"
   - Background: Light gray

4. **Consumer Service** (Red - #FF5630)
   - Add rectangle shape
   - Label: "Consumer Service"
   - Background: Light red

5. **External Services** (Purple - #6554C0)
   - Add rectangle shape
   - Label: "External Services"
   - Background: Light purple

### Step 3: Add Components

**In Jira Cloud:**
- Box: "Jira Issues"

**In Webhook Service:**
- Box: "FastAPI Webhook Endpoint"
- Box: "Kafka Producer"

**In Kafka Cluster:**
- Box: "jira-events Topic"

**In Consumer Service:**
- Box: "Kafka Consumer"
- Box: "Message Processor"
- Box: "Jira Client" (NEW - highlight this)
- Box: "LangGraph Client"

**In External Services:**
- Box: "LangGraph API / AI Orchestrator"

### Step 4: Add Connections (Arrows)

**Forward Flow (Jira → Consumer):**
1. Jira Issues → FastAPI Webhook
   - Label: "Webhook Event"
   
2. FastAPI Webhook → Kafka Producer
   - Label: "Validate & Transform"
   
3. Kafka Producer → jira-events Topic
   - Label: "Publish"
   
4. jira-events Topic → Kafka Consumer
   - Label: "Consume"
   
5. Kafka Consumer → Message Processor
   - Label: "Parse Event"

**Processing Flow:**
6. Message Processor → LangGraph Client
   - Label: "Send for AI Processing"
   
7. LangGraph Client → LangGraph API
   - Label: "AI Request"
   
8. LangGraph API → LangGraph Client
   - Label: "AI Response"
   - Style: Dashed line
   
9. LangGraph Client → Message Processor
   - Label: "Response"
   - Style: Dashed line

**Reverse Flow (Consumer → Jira) - NEW:**
10. Message Processor → Jira Client
    - Label: "Post Comment"
    - Style: Bold, highlighted
    
11. Jira Client → Jira Issues
    - Label: "REST API Call"
    - Style: Bold, highlighted, curved arrow back to start

### Step 5: Add Legend

Create a legend box in the bottom-right corner:

**Legend:**
- Solid Arrow: Data flow
- Dashed Arrow: Response flow
- Bold Arrow: NEW - Bidirectional integration
- Colors:
  - Blue: Jira
  - Green: Webhook Service
  - Gray: Kafka
  - Red: Consumer Service
  - Purple: External Services

### Step 6: Add Annotations

Add text boxes with notes:

1. Near Jira Client:
   ```
   NEW: Jira Client
   - Posts acknowledgment comments
   - Health checks
   - Retry logic (3 attempts)
   - Error handling
   ```

2. Near the reverse flow arrow:
   ```
   Bidirectional Integration
   Consumer can now post comments
   back to Jira issues
   ```

### Step 7: Style the Diagram

**Colors:**
- Jira Cloud: #0052CC (Blue)
- Webhook Service: #00875A (Green)
- Kafka Cluster: #231F20 (Black/Gray)
- Consumer Service: #FF5630 (Red)
- External Services: #6554C0 (Purple)

**Fonts:**
- Title: Arial, 16pt, Bold
- Component names: Arial, 12pt, Bold
- Labels: Arial, 10pt, Regular

**Shapes:**
- Containers: Rounded rectangles with shadow
- Components: Rectangles with rounded corners
- Arrows: Standard arrows, 2pt width
- NEW components: Add a "NEW" badge or star icon

### Step 8: Export

1. Click **File → Export as → PNG**
2. Settings:
   - Resolution: 300 DPI
   - Transparent background: No
   - Border width: 10px
3. Save as: `architecture-diagram.png`
4. Also export as SVG for scalability

## Sequence Diagram (Optional)

For the detailed sequence diagram, you can:

1. Use Draw.io's built-in sequence diagram shapes
2. Or use a dedicated tool like:
   - PlantUML
   - Mermaid Live Editor
   - SequenceDiagram.org

The sequence diagram from [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md) can be rendered directly in most markdown viewers that support Mermaid.

## Quick Reference: Component Layout

```
┌─────────────────────────────────────────────────────────────┐
│                         Jira Cloud                          │
│  ┌──────────────┐                                           │
│  │ Jira Issues  │◄──────────────────────┐                   │
│  └──────────────┘                       │                   │
└────────┬────────────────────────────────┼───────────────────┘
         │                                │
         │ Webhook Event                  │ REST API Call (NEW)
         │                                │
┌────────▼────────────────────────────────┼───────────────────┐
│                    Webhook Service      │                   │
│  ┌──────────────┐    ┌──────────────┐  │                   │
│  │   FastAPI    │───►│    Kafka     │  │                   │
│  │   Webhook    │    │   Producer   │  │                   │
│  └──────────────┘    └──────────────┘  │                   │
└─────────────────────────┬───────────────┘                   │
                          │                                   │
                          │ Publish                           │
                          │                                   │
┌─────────────────────────▼───────────────────────────────────┐
│                     Kafka Cluster                           │
│              ┌──────────────────────┐                       │
│              │  jira-events Topic   │                       │
│              └──────────────────────┘                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ Consume
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Consumer Service                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Kafka     │───►│   Message    │───►│    Jira      │──┤
│  │   Consumer   │    │  Processor   │    │   Client     │  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘  │
│                             │                               │
│                             │                               │
│                      ┌──────▼───────┐                       │
│                      │  LangGraph   │                       │
│                      │    Client    │                       │
│                      └──────┬───────┘                       │
└─────────────────────────────┼───────────────────────────────┘
                              │
                              │ AI Request
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                   External Services                         │
│              ┌──────────────────────┐                       │
│              │   LangGraph API      │                       │
│              │  AI Orchestrator     │                       │
│              └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Tips

1. **Use consistent spacing** between components (50-100px)
2. **Align components** horizontally and vertically
3. **Use color coding** to distinguish different system parts
4. **Add shadows** to make components stand out
5. **Highlight NEW features** with badges or different colors
6. **Keep labels concise** but descriptive
7. **Use curved arrows** for feedback loops
8. **Add a title** at the top: "Jira Integration - Bidirectional Architecture"

## File Locations

After creating the diagram, save it as:
- `jira-consumer/docs/images/architecture-diagram.png` (PNG export)
- `jira-consumer/docs/images/architecture-diagram.svg` (SVG export)
- `jira-consumer/docs/architecture-diagram.drawio` (Source file)

## Alternative: Use Mermaid Directly

Many documentation platforms (GitHub, GitLab, Notion, etc.) support Mermaid diagrams natively. You can simply use the Mermaid code from [`ARCHITECTURE_DIAGRAM.md`](ARCHITECTURE_DIAGRAM.md) directly in your markdown files.

The diagrams will render automatically without needing Draw.io!