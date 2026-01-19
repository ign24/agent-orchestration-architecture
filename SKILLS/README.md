# Skills Directory

This directory contains all available skills for the Agent Orchestration System.

## Structure

Each skill is defined in its own directory with a `skill.json` file:

```
SKILLS/
├── yolo26-detection/
│   └── skill.json
├── sam3-segmentation/
│   └── skill.json
├── mvp-nextjs/
│   ├── skill.json
│   └── SKILL.md (optional human-readable docs)
└── ...
```

## Available Skills by Category

### Computer Vision / ML (13 skills)

| Skill | Description | Autonomy |
|-------|-------------|----------|
| `yolo26-detection` | YOLO26 NMS-Free detection | delegado |
| `yolo26-segmentation` | YOLO26 instance segmentation | delegado |
| `yoloe-open-vocabulary` | Open-vocabulary detection (4,585 classes) | co-pilot |
| `sam3-segmentation` | SAM3 text-prompted segmentation | co-pilot |
| `fvm-fine-tuning` | Foundation model fine-tuning (LoRA, DoRA) | co-pilot |
| `training-pipeline` | Complete training pipeline | delegado |
| `dataset-prep` | Dataset preparation for YOLO format | delegado |
| `model-evaluation` | Model evaluation and metrics | delegado |
| `video-tracking` | Multi-object tracking (BYTETrack, StrongSORT) | delegado |
| `data-augmentation-advanced` | Advanced augmentation 2026 | delegado |
| `hyperparameter-tuning` | Auto-tuning with genetic algorithms | co-pilot |
| `edge-deployment-optimized` | Edge deployment optimization | co-pilot |
| `cv-mlops-setup` | MLOps pipeline setup | co-pilot |

### Development (3 skills)

| Skill | Description | Autonomy |
|-------|-------------|----------|
| `mvp-nextjs` | Next.js 15 + shadcn/ui scaffold | delegado |
| `mvp-fastapi` | FastAPI backend scaffold | delegado |
| `feature-auth` | Supabase authentication | co-pilot |

### Operations (2 skills)

| Skill | Description | Autonomy |
|-------|-------------|----------|
| `deploy-vercel` | Vercel deployment | asistente |
| `debug-systematic` | Systematic debugging | co-pilot |

## Creating a New Skill

1. Create directory: `mkdir SKILLS/my-skill`
2. Create `skill.json` following the schema in `schemas/skill-schema.json`
3. Validate: `python skill_controller.py --info my-skill`
4. Test: `python skill_controller.py --execute my-skill --dry-run`

### Minimal skill.json Template

```json
{
  "name": "my-skill",
  "version": "1.0.0",
  "description": "Description of what this skill does",
  "autonomy": "delegado",
  "context7_required": [],
  "pre_requisites": [
    {"check": "command_exists", "args": ["python"]}
  ],
  "inputs": {
    "param1": {
      "type": "string",
      "required": true,
      "description": "First parameter"
    }
  },
  "steps": [
    {
      "id": "step_1",
      "type": "bash",
      "description": "First step",
      "cmd": "echo 'Hello {param1}'",
      "timeout": 30
    }
  ],
  "verification": [
    {"type": "bash", "cmd": "echo 'OK'", "expect_exit": 0}
  ],
  "metadata": {
    "author": "Your Name",
    "created": "2026-01-19",
    "tags": ["example"]
  }
}
```

## Schema Reference

See `schemas/skill-schema.json` for the complete schema definition.

### Step Types

| Type | Description | Required Fields |
|------|-------------|-----------------|
| `bash` | Execute shell command | `cmd` |
| `python` | Execute Python code | `cmd` |
| `agent` | Agent decision point | - |
| `checkpoint` | Human confirmation | `checkpoint_message` |
| `mcp` | MCP tool call | `mcp_server`, `mcp_tool`, `mcp_args` |

### Pre-requisite Checks

| Check | Description | Args |
|-------|-------------|------|
| `command_exists` | Verify command in PATH | `["command_name"]` |
| `file_exists` | Verify file exists | `["path/to/file"]` |
| `dir_exists` | Verify directory exists | `["path/to/dir"]` |
| `env_var_set` | Verify env var set | `["VAR_NAME"]` |

## Versioning

Skills use semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes to inputs/outputs
- MINOR: New features, backward compatible
- PATCH: Bug fixes
