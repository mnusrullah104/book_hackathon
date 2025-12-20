# AI-Native Book with Embedded RAG Chatbot Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-20

## Active Technologies

- Markdown (MD) for documentation
- Docusaurus documentation framework
- NVIDIA Isaac ecosystem (Isaac Sim, Isaac ROS)
- ROS 2 navigation stack (Nav2)
- VSLAM (Visual Simultaneous Localization and Mapping)
- Photorealistic simulation
- Synthetic data generation
- Hardware-accelerated visual pipelines
- OpenAI Whisper for speech-to-text
- Large Language Models (LLMs) for cognitive planning
- Vision-Language-Action (VLA) integration

## Project Structure

```text
docs/
├── isaac-robot-brain/
│   ├── chapter-1-isaac-sim-fundamentals.md
│   ├── chapter-2-isaac-ros-perception-vslam.md
│   └── chapter-3-navigation-with-nav2-humanoids.md
├── vla-integration/
│   ├── chapter-1-voice-to-action-pipelines.md
│   ├── chapter-2-cognitive-planning-with-llms.md
│   └── chapter-3-capstone-autonomous-humanoid.md
specs/1-isaac-robot-brain/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── isaac-robot-brain-api.yaml
└── spec.md
specs/4-vla-integration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── vla-educational-api.yaml
└── spec.md
```

## Commands

- `sp.specify` - Create feature specifications
- `sp.plan` - Generate implementation plans
- `sp.tasks` - Generate development tasks
- `sp.clarify` - Clarify underspecified areas in specs
- `sp.analyze` - Analyze consistency across artifacts

## Code Style

- Documentation should be in Markdown format
- Technical explanations should be clear and accessible
- Content should build on existing ROS 2 knowledge
- Focus on conceptual understanding rather than implementation details
- Include practical examples only where necessary for clarity

## Recent Changes

- Isaac Robot Brain Module: Added educational content covering NVIDIA Isaac Sim, Isaac ROS perception and VSLAM, and Nav2 navigation for humanoid robots
- Isaac Sim Fundamentals: Documentation on photorealistic simulation and synthetic data generation
- Isaac ROS and Navigation: Content on perception systems and humanoid-specific navigation concepts
- VLA Integration Module: Added educational content covering voice-to-action pipelines, cognitive planning with LLMs, and autonomous humanoid systems
- Voice-to-Action Pipelines: Documentation on OpenAI Whisper integration and voice command mapping
- Cognitive Planning: Content on LLM-based planning for robotics and task decomposition

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->