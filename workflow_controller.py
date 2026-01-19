"""
Workflow Controller - Orchestrates multi-skill workflows with state persistence.

REGLAS CRITICAS:
1. Workflows DEBEN existir en registry
2. Cada phase ejecuta UN skill via SkillController
3. Checkpoints permiten human-in-the-loop
4. Estado se persiste para resume despues de fallas
5. PROJECT_CONTEXT.md se actualiza automaticamente

Author: Nacho @ Factor.com.ar
Version: 1.0.0
Created: 2026-01-19
"""

import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Import SkillController
from skill_controller import SkillController, SkillResult

# Conditional import for jsonschema
try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None  # type: ignore
    HAS_JSONSCHEMA = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("WorkflowController")


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"  # At checkpoint
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PhaseResult:
    """Result of a single phase execution."""

    phase_name: str
    skill_name: str
    success: bool
    skill_result: Optional[SkillResult] = None
    skipped: bool = False
    skip_reason: Optional[str] = None
    duration_ms: int = 0


@dataclass
class WorkflowResult:
    """Result of complete workflow execution."""

    success: bool
    workflow_name: str
    version: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    phases_completed: List[str] = field(default_factory=list)
    phases_failed: List[str] = field(default_factory=list)
    phases_skipped: List[str] = field(default_factory=list)
    current_phase: Optional[str] = None
    total_duration_ms: int = 0
    state_file: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass
class WorkflowState:
    """Persistent state for workflow resume."""

    workflow_name: str
    version: str
    status: str
    current_phase_index: int
    inputs: Dict[str, Any]
    phases_completed: List[str]
    phases_failed: List[str]
    phase_outputs: Dict[str, Any]  # Outputs from each phase
    started_at: str
    updated_at: str
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "WorkflowState":
        return cls(**data)


class WorkflowController:
    """
    Controlador que orquesta workflows multi-skill.

    Features:
    - Ejecuta skills en secuencia via SkillController
    - Soporta checkpoints para human-in-the-loop
    - Persiste estado para resume
    - Evalua condiciones para skip phases
    - Actualiza PROJECT_CONTEXT.md automaticamente
    """

    def __init__(
        self,
        workflows_dir: str = "WORKFLOWS",
        schema_path: str = "schemas/workflow-schema.json",
        state_dir: str = "outputs/workflow_state",
        base_path: Optional[str] = None,
    ):
        # Determine base path (priority: explicit param > env var > cwd)
        if base_path:
            self.base_path = Path(base_path)
        elif os.environ.get("AGENT_WORKSPACE"):
            self.base_path = Path(os.environ["AGENT_WORKSPACE"])
        else:
            self.base_path = Path.cwd()

        self.workflows_dir = self.base_path / workflows_dir
        self.schema_path = self.base_path / schema_path
        self.state_dir = self.base_path / state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Load JSON Schema for validation
        # IMPORTANT: Load schema regardless of jsonschema availability
        self.schema = None
        if self.schema_path.exists():
            with open(self.schema_path) as f:
                self.schema = json.load(f)
            if not HAS_JSONSCHEMA:
                logger.warning(
                    "Schema loaded but jsonschema not installed. "
                    "Validation will be enforced - install jsonschema or remove schema file."
                )

        # Initialize SkillController
        self.skill_controller = SkillController(base_path=str(self.base_path))

        # Load all workflows into registry
        self.registry: Dict[str, Dict] = {}
        self._load_registry()

        logger.info(
            f"WorkflowController initialized with {len(self.registry)} workflows"
        )

    def _load_registry(self) -> None:
        """Load all workflows and validate against schema."""
        if not self.workflows_dir.exists():
            logger.warning(f"Workflows directory not found: {self.workflows_dir}")
            return

        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, encoding="utf-8") as f:
                    workflow = json.load(f)

                # Validate against schema - ENFORCED if schema exists
                if self.schema:
                    if not HAS_JSONSCHEMA:
                        raise RuntimeError(
                            "Schema validation required but jsonschema not installed. "
                            "Run: pip install jsonschema"
                        )
                    jsonschema.validate(instance=workflow, schema=self.schema)  # type: ignore[union-attr]

                # Validate all skills exist
                for phase in workflow.get("phases", []):
                    skill_name = phase.get("skill")
                    if not self.skill_controller.validate_skill_exists(skill_name):
                        logger.warning(
                            f"Workflow {workflow['name']}: skill '{skill_name}' not found"
                        )

                self.registry[workflow["name"]] = workflow
                self.registry[workflow["name"]]["_path"] = str(workflow_file)
                logger.info(
                    f"  Loaded workflow: {workflow['name']} v{workflow['version']}"
                )

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {workflow_file}: {e}")
            except RuntimeError as e:
                logger.error(str(e))
            except Exception as e:
                if HAS_JSONSCHEMA and jsonschema is not None:
                    if isinstance(e, jsonschema.ValidationError):
                        logger.error(
                            f"Workflow {workflow_file} failed validation: {e.message}"
                        )
                        continue
                logger.error(f"Failed to load {workflow_file}: {e}")

    def list_workflows(self) -> List[str]:
        """Return list of available workflows."""
        return sorted(self.registry.keys())

    def get_workflow_info(self, workflow_name: str) -> Optional[Dict]:
        """Get detailed info about a workflow."""
        return self.registry.get(workflow_name)

    def validate_workflow_exists(self, workflow_name: str) -> bool:
        """Validate workflow exists before execution."""
        exists = workflow_name in self.registry
        if not exists:
            logger.error(f"WORKFLOW NOT FOUND: '{workflow_name}'")
            logger.info(f"Available workflows: {self.list_workflows()}")
        return exists

    def _check_condition(
        self, condition: Dict, inputs: Dict, phase_outputs: Dict
    ) -> bool:
        """Evaluate phase condition."""
        cond_type = condition.get("type")
        key = condition.get("key")
        value = condition.get("value")
        path = condition.get("path")

        if cond_type == "input_equals":
            return inputs.get(key) == value

        elif cond_type == "input_truthy":
            return bool(inputs.get(key))

        elif cond_type == "previous_success":
            # Check if previous phase succeeded
            return key in phase_outputs and phase_outputs[key].get("success", False)

        elif cond_type == "file_exists":
            if path is None:
                return False
            formatted_path = path.format(**inputs)
            return Path(formatted_path).exists()

        return True  # Default: execute

    def _save_state(self, state: WorkflowState) -> str:
        """Save workflow state for resume."""
        state.updated_at = datetime.now().isoformat()
        state_file = self.state_dir / f"{state.workflow_name}_state.json"

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)

        return str(state_file)

    def _load_state(self, workflow_name: str) -> Optional[WorkflowState]:
        """Load workflow state for resume."""
        state_file = self.state_dir / f"{workflow_name}_state.json"

        if not state_file.exists():
            return None

        try:
            with open(state_file, encoding="utf-8") as f:
                data = json.load(f)
            return WorkflowState.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None

    def _clear_state(self, workflow_name: str) -> None:
        """Clear workflow state after completion."""
        state_file = self.state_dir / f"{workflow_name}_state.json"
        if state_file.exists():
            state_file.unlink()

    def _update_project_context(
        self, workflow: Dict, inputs: Dict, result: WorkflowResult
    ) -> None:
        """Update PROJECT_CONTEXT.md with workflow results."""
        on_complete = workflow.get("on_complete", {})
        if not on_complete.get("update_context", True):
            return

        # Determine project path
        project_path = inputs.get("target_dir", inputs.get("project_path", "."))
        if "{project_name}" in str(project_path):
            project_path = project_path.format(**inputs)

        context_file = Path(project_path) / "PROJECT_CONTEXT.md"

        if not context_file.exists():
            logger.warning(f"PROJECT_CONTEXT.md not found at {context_file}")
            return

        try:
            content = context_file.read_text(encoding="utf-8")

            # Append workflow execution log
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            status = "SUCCESS" if result.success else "FAILED"

            log_entry = f"""
---

## Workflow Execution: {workflow["name"]} ({timestamp})

**Status:** {status}
**Phases Completed:** {", ".join(result.phases_completed) or "None"}
**Phases Failed:** {", ".join(result.phases_failed) or "None"}
**Duration:** {result.total_duration_ms}ms
"""

            # Insert before last section or append
            if "## Next Steps" in content:
                content = content.replace(
                    "## Next Steps", f"{log_entry}\n## Next Steps"
                )
            else:
                content += log_entry

            context_file.write_text(content, encoding="utf-8")
            logger.info(f"Updated PROJECT_CONTEXT.md")

        except Exception as e:
            logger.warning(f"Failed to update PROJECT_CONTEXT.md: {e}")

    def execute_workflow(
        self,
        workflow_name: str,
        inputs: Dict[str, Any],
        agent_callback: Optional[Callable] = None,
        dry_run: bool = False,
        resume: bool = False,
    ) -> WorkflowResult:
        """
        Execute workflow with state persistence and checkpoints.

        Args:
            workflow_name: Name of workflow to execute
            inputs: Global inputs for the workflow
            agent_callback: Function for agent to execute code/checkpoints
            dry_run: If True, only validate without executing
            resume: If True, resume from saved state

        Returns:
            WorkflowResult with success status and phase details
        """
        start_time = datetime.now()

        # ENFORCEMENT: Workflow MUST exist
        if not self.validate_workflow_exists(workflow_name):
            return WorkflowResult(
                success=False,
                workflow_name=workflow_name,
                version="unknown",
                status=WorkflowStatus.FAILED,
                error=f"Workflow '{workflow_name}' not found. Available: {self.list_workflows()}",
            )

        workflow = self.registry[workflow_name]
        phases = workflow.get("phases", [])

        logger.info(f"\n{'=' * 60}")
        logger.info(f"EXECUTING WORKFLOW: {workflow_name} v{workflow['version']}")
        logger.info(f"Phases: {len(phases)}")
        logger.info(f"{'=' * 60}")

        # Apply input defaults
        for input_name, input_spec in workflow.get("inputs", {}).items():
            if input_name not in inputs and "default" in input_spec:
                inputs[input_name] = input_spec["default"]

        # Initialize or load state
        start_phase = 0
        phase_outputs: Dict[str, Any] = {}

        if resume:
            saved_state = self._load_state(workflow_name)
            if saved_state and saved_state.status == WorkflowStatus.PAUSED.value:
                logger.info(f"Resuming from phase {saved_state.current_phase_index}")
                start_phase = saved_state.current_phase_index
                phase_outputs = saved_state.phase_outputs
                inputs = {**saved_state.inputs, **inputs}  # Merge with new inputs

        state = WorkflowState(
            workflow_name=workflow_name,
            version=workflow["version"],
            status=WorkflowStatus.IN_PROGRESS.value,
            current_phase_index=start_phase,
            inputs=inputs,
            phases_completed=[],
            phases_failed=[],
            phase_outputs=phase_outputs,
            started_at=start_time.isoformat(),
            updated_at=start_time.isoformat(),
        )

        if dry_run:
            logger.info("\n[DRY RUN] Validating workflow...")
            for i, phase in enumerate(phases):
                logger.info(
                    f"  Phase {i + 1}: {phase['name']} -> skill: {phase['skill']}"
                )
            return WorkflowResult(
                success=True,
                workflow_name=workflow_name,
                version=workflow["version"],
                status=WorkflowStatus.COMPLETED,
                phases_completed=["(dry run)"],
            )

        phases_completed = []
        phases_failed = []
        phases_skipped = []

        try:
            for i, phase in enumerate(phases[start_phase:], start=start_phase):
                phase_name = phase["name"]
                skill_name = phase["skill"]
                state.current_phase_index = i

                logger.info(f"\n--- Phase {i + 1}/{len(phases)}: {phase_name} ---")
                logger.info(f"Skill: {skill_name}")

                # Check condition
                condition = phase.get("condition")
                if condition and not self._check_condition(
                    condition, inputs, phase_outputs
                ):
                    logger.info(f"  Skipping: condition not met")
                    phases_skipped.append(phase_name)
                    continue

                # Merge inputs
                phase_inputs = {**inputs, **phase.get("inputs", {})}

                # Execute skill
                phase_start = datetime.now()
                skill_result = self.skill_controller.execute_skill(
                    skill_name=skill_name,
                    inputs=phase_inputs,
                    agent_callback=agent_callback,
                    dry_run=False,
                )
                phase_duration = int(
                    (datetime.now() - phase_start).total_seconds() * 1000
                )

                # Store result
                phase_outputs[phase_name] = {
                    "success": skill_result.success,
                    "outputs": skill_result.outputs,
                }

                if skill_result.success:
                    phases_completed.append(phase_name)
                    state.phases_completed.append(phase_name)
                    logger.info(f"  Phase completed in {phase_duration}ms")
                else:
                    phases_failed.append(phase_name)
                    state.phases_failed.append(phase_name)
                    logger.error(f"  Phase failed: {skill_result.error}")

                    # Handle failure
                    on_failure = phase.get("on_failure", "stop")
                    if on_failure == "stop":
                        state.status = WorkflowStatus.FAILED.value
                        state.error = (
                            f"Phase '{phase_name}' failed: {skill_result.error}"
                        )
                        self._save_state(state)

                        return WorkflowResult(
                            success=False,
                            workflow_name=workflow_name,
                            version=workflow["version"],
                            status=WorkflowStatus.FAILED,
                            phases_completed=phases_completed,
                            phases_failed=phases_failed,
                            phases_skipped=phases_skipped,
                            current_phase=phase_name,
                            total_duration_ms=int(
                                (datetime.now() - start_time).total_seconds() * 1000
                            ),
                            error=f"Phase '{phase_name}' failed",
                        )
                    elif on_failure == "skip_remaining":
                        logger.warning("  Skipping remaining phases")
                        break

                # Checkpoint
                if phase.get("checkpoint", False):
                    checkpoint_msg = phase.get(
                        "checkpoint_message",
                        f"Phase '{phase_name}' completed. Continue?",
                    )
                    logger.info(f"\n  CHECKPOINT: {checkpoint_msg}")

                    # Save state before checkpoint
                    state.status = WorkflowStatus.PAUSED.value
                    state.current_phase_index = i + 1
                    state.phase_outputs = phase_outputs
                    state_file = self._save_state(state)
                    logger.info(f"  State saved: {state_file}")

                    if agent_callback:
                        result = agent_callback("checkpoint", message=checkpoint_msg)
                        if not result:
                            return WorkflowResult(
                                success=False,
                                workflow_name=workflow_name,
                                version=workflow["version"],
                                status=WorkflowStatus.PAUSED,
                                phases_completed=phases_completed,
                                phases_failed=phases_failed,
                                current_phase=phase_name,
                                state_file=state_file,
                                error="Paused at checkpoint",
                            )

            # Workflow completed
            total_duration = int((datetime.now() - start_time).total_seconds() * 1000)

            result = WorkflowResult(
                success=len(phases_failed) == 0,
                workflow_name=workflow_name,
                version=workflow["version"],
                status=WorkflowStatus.COMPLETED,
                phases_completed=phases_completed,
                phases_failed=phases_failed,
                phases_skipped=phases_skipped,
                total_duration_ms=total_duration,
            )

            # Update PROJECT_CONTEXT.md
            self._update_project_context(workflow, inputs, result)

            # Clear state on success
            if result.success:
                self._clear_state(workflow_name)

            logger.info(f"\n{'=' * 60}")
            logger.info(
                f"WORKFLOW {'COMPLETED' if result.success else 'FINISHED WITH ERRORS'}"
            )
            logger.info(f"Duration: {total_duration}ms")
            logger.info(f"{'=' * 60}")

            return result

        except KeyboardInterrupt:
            state.status = WorkflowStatus.CANCELLED.value
            self._save_state(state)
            return WorkflowResult(
                success=False,
                workflow_name=workflow_name,
                version=workflow["version"],
                status=WorkflowStatus.CANCELLED,
                phases_completed=phases_completed,
                phases_failed=phases_failed,
                error="Cancelled by user",
            )

        except Exception as e:
            logger.exception(f"Unexpected error in workflow {workflow_name}")
            state.status = WorkflowStatus.FAILED.value
            state.error = str(e)
            self._save_state(state)

            return WorkflowResult(
                success=False,
                workflow_name=workflow_name,
                version=workflow["version"],
                status=WorkflowStatus.FAILED,
                phases_completed=phases_completed,
                phases_failed=phases_failed,
                error=str(e),
            )


# === CLI INTERFACE ===


def main():
    """CLI for workflow controller."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow Controller CLI - Orchestrate multi-skill workflows"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available workflows"
    )
    parser.add_argument("--info", "-i", type=str, help="Show info about a workflow")
    parser.add_argument("--execute", "-e", type=str, help="Execute workflow by name")
    parser.add_argument(
        "--inputs", type=str, default="{}", help="JSON string of inputs"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without executing"
    )
    parser.add_argument("--resume", action="store_true", help="Resume from saved state")
    parser.add_argument("--status", type=str, help="Check status of a workflow")

    args = parser.parse_args()

    controller = WorkflowController()

    if args.list:
        workflows = controller.list_workflows()
        if workflows:
            print("\nAvailable workflows:")
            for wf in workflows:
                info = controller.get_workflow_info(wf)
                if info:
                    desc = info.get("description", "No description")[:50]
                    phases = len(info.get("phases", []))
                    print(f"  - {wf} (v{info['version']}): {desc} [{phases} phases]")
        else:
            print("\nNo workflows found. Create workflows in WORKFLOWS/*.json")

    elif args.info:
        info = controller.get_workflow_info(args.info)
        if info:
            print(f"\nWorkflow: {info['name']} v{info['version']}")
            print(f"Description: {info.get('description', 'N/A')}")
            print(f"\nInputs:")
            for name, spec in info.get("inputs", {}).items():
                req = "(required)" if spec.get("required") else "(optional)"
                print(f"  - {name}: {spec.get('type', 'any')} {req}")
            print(f"\nPhases: {len(info['phases'])}")
            for i, phase in enumerate(info["phases"], 1):
                checkpoint = " [CHECKPOINT]" if phase.get("checkpoint") else ""
                print(f"  {i}. {phase['name']} -> {phase['skill']}{checkpoint}")
        else:
            print(f"\nWorkflow '{args.info}' not found")

    elif args.status:
        state = controller._load_state(args.status)
        if state:
            print(f"\nWorkflow: {state.workflow_name}")
            print(f"Status: {state.status}")
            print(f"Current Phase: {state.current_phase_index}")
            print(f"Completed: {state.phases_completed}")
            print(f"Failed: {state.phases_failed}")
            print(f"Started: {state.started_at}")
            print(f"Updated: {state.updated_at}")
            if state.error:
                print(f"Error: {state.error}")
        else:
            print(f"\nNo saved state for workflow '{args.status}'")

    elif args.execute:
        try:
            inputs = json.loads(args.inputs)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON inputs: {e}")
            return 1

        result = controller.execute_workflow(
            args.execute,
            inputs,
            dry_run=args.dry_run,
            resume=args.resume,
        )

        print(f"\n{'=' * 60}")
        if result.success:
            print(f"SUCCESS: Workflow '{result.workflow_name}' completed")
        else:
            print(f"FAILED: {result.error}")
        print(f"Status: {result.status.value}")
        print(f"Phases completed: {result.phases_completed}")
        print(f"Phases failed: {result.phases_failed}")
        print(f"Duration: {result.total_duration_ms}ms")
        if result.state_file:
            print(f"State file: {result.state_file}")
        print(f"{'=' * 60}")

        return 0 if result.success else 1

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
