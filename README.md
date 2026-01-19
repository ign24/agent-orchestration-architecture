# Agent Orchestration System

> A structured skill-based system for AI agent orchestration with JSON Schema validation, execution enforcement, and comprehensive logging.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This system provides a framework for orchestrating AI agents through **Skills** (atomic tasks) and **Workflows** (multi-skill pipelines). Key features:

- **JSON Schema Validation**: All skills validated against strict schemas
- **Execution Enforcement**: Prevents agent hallucination with structured steps
- **Context7 Integration**: MCP support for up-to-date documentation
- **Comprehensive Logging**: Full execution history with rollback support
- **Multi-Level Autonomy**: `delegado`, `co-pilot`, `asistente` modes

## Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/agent-orchestration-system.git
cd agent-orchestration-system

# List available skills
python skill_controller.py --list

# Get skill info
python skill_controller.py --info yolo26-detection

# Execute skill (dry-run)
python skill_controller.py --execute yolo26-detection --inputs '{"model_size": "n"}' --dry-run

# Execute skill (real)
python skill_controller.py --execute yolo26-detection --inputs '{"model_size": "n"}'
```

## Structure

```
agent-orchestration-system/
├── skill_controller.py      # Main skill execution engine
├── workflow_controller.py   # Multi-skill workflow orchestrator
├── schemas/
│   ├── skill-schema.json    # JSON Schema for skills
│   └── workflow-schema.json # JSON Schema for workflows
├── SKILLS/                  # Skill definitions (19 skills)
│   ├── yolo26-detection/
│   ├── sam3-segmentation/
│   ├── mvp-nextjs/
│   └── ...
├── WORKFLOWS/               # Multi-skill workflows
│   ├── new-project-web.json
│   └── ml-experiment.md
├── TEMPLATES/               # Project templates
├── AGENTS.md                # Global agent configuration
└── PATTERNS.md              # Coding patterns reference
```

## Available Skills (19)

### Computer Vision / ML
| Skill | Version | Description |
|-------|---------|-------------|
| `yolo26-detection` | 1.0.0 | YOLO26 with NMS-Free, MuSGD, +43% CPU speed |
| `yolo26-segmentation` | 1.0.0 | Instance segmentation with semantic seg loss |
| `yoloe-open-vocabulary` | 1.0.0 | Open-vocabulary detection (4,585 classes) |
| `sam3-segmentation` | 2.0.0 | SAM3 via Ultralytics with text prompts |
| `fvm-fine-tuning` | 1.0.0 | PEFT with LoRA, DoRA, GaLore |
| `training-pipeline` | 1.0.0 | Complete training pipeline |
| `dataset-prep` | 1.0.0 | Dataset preparation for YOLO |
| `model-evaluation` | 1.0.0 | Model evaluation and metrics |
| `video-tracking` | 1.0.0 | Multi-object tracking (BYTETrack, StrongSORT) |
| `data-augmentation-advanced` | 1.0.0 | Advanced augmentation 2026 |
| `hyperparameter-tuning` | 1.0.0 | Auto-tuning with genetic algorithms |
| `edge-deployment-optimized` | 1.0.0 | Edge deployment (TensorRT, INT8/FP16) |
| `cv-mlops-setup` | 1.0.0 | MLOps pipeline (MLflow, DVC, Evidently) |

### Development
| Skill | Version | Description |
|-------|---------|-------------|
| `mvp-nextjs` | 1.0.0 | Next.js 15 + shadcn/ui scaffold |
| `mvp-fastapi` | 1.0.0 | FastAPI backend scaffold |
| `feature-auth` | 1.0.0 | Supabase authentication |

### Operations
| Skill | Version | Description |
|-------|---------|-------------|
| `deploy-vercel` | 1.0.0 | Vercel deployment |
| `debug-systematic` | 1.0.0 | Systematic debugging workflow |

## Skill Anatomy

Each skill is defined in `SKILLS/<skill-name>/skill.json`:

```json
{
  "name": "yolo26-detection",
  "version": "1.0.0",
  "description": "YOLO26 object detection with NMS-Free architecture",
  "autonomy": "delegado",
  "context7_required": ["/ultralytics/ultralytics", "/pytorch/pytorch"],
  "pre_requisites": [
    {"check": "command_exists", "args": ["python"]}
  ],
  "inputs": {
    "model_size": {
      "type": "string",
      "required": false,
      "default": "n",
      "enum": ["n", "s", "m", "l", "x"]
    }
  },
  "steps": [
    {
      "id": "install_ultralytics",
      "type": "bash",
      "cmd": "pip install ultralytics>=8.4.0",
      "timeout": 120
    }
  ],
  "verification": [
    {"type": "bash", "cmd": "python -c 'import ultralytics'", "expect_exit": 0}
  ],
  "rollback": [
    {"id": "cleanup", "cmd": "rm -rf runs/", "description": "Remove training artifacts"}
  ]
}
```

## Autonomy Levels

| Level | Confirmations | Use Case |
|-------|---------------|----------|
| `delegado` | Only on errors | Well-defined tasks, low risk |
| `co-pilot` | Before major changes | Complex tasks, significant changes |
| `asistente` | Every step | Critical operations (deploy, delete) |

## Workflows

Workflows chain multiple skills together:

```bash
# Execute workflow
python workflow_controller.py --execute new-project-web --inputs '{"project_name": "my-app"}'
```

## Context7 Integration

Skills can require Context7 libraries for up-to-date documentation:

```json
{
  "context7_required": ["/ultralytics/ultralytics", "/pytorch/pytorch"]
}
```

The controller automatically loads documentation via MCP before execution.

## Logging

All executions are logged to `outputs/skill_logs/`:

```json
{
  "timestamp": "2026-01-19T10:19:48",
  "skill": "sam3-segmentation",
  "version": "2.0.0",
  "inputs": {"source": "video.mp4", "prompts": ["person"]},
  "steps": [
    {"id": "verify_ultralytics", "status": "completed", "duration_ms": 150}
  ],
  "success": true,
  "total_duration_ms": 1234
}
```

## Creating New Skills

1. Create directory: `mkdir SKILLS/my-new-skill`
2. Create `skill.json` following the schema
3. Validate: `python skill_controller.py --info my-new-skill`
4. Test: `python skill_controller.py --execute my-new-skill --dry-run`

## Tech Stack (January 2026)

| Layer | Technologies |
|-------|--------------|
| Frontend | Next.js 15, React 19, Tailwind 4, shadcn/ui |
| Backend | FastAPI, Pydantic v2, Supabase |
| ML/CV | PyTorch 2.5+, Ultralytics 8.4+, YOLO26, SAM3 |
| MLOps | MLflow, DVC, Evidently AI, Kubeflow |

## References

- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [Context7 Documentation](https://context7.com)
- [Ultralytics YOLO26](https://docs.ultralytics.com)

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Built with Claude Code by Nacho @ [Factor.com.ar](https://factor.com.ar)
