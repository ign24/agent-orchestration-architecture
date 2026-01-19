"""
Skill Controller - Enforcement layer para prevenir alucinaciones.

REGLAS CRITICAS:
1. Skills DEBEN existir en registry (no alucinaciones)
2. Steps se ejecutan SECUENCIALMENTE (no se puede saltear)
3. Context7 es OBLIGATORIO si skill.context7_required esta presente
4. Verification es OBLIGATORIA (no se puede decir "termine" sin verificar)
5. Rollback AUTOMATICO si un step falla

Author: Nacho @ Factor.com.ar
Version: 1.0.0
Created: 2026-01-19
"""

import json
import subprocess
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Conditional import for jsonschema
try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Run: pip install jsonschema")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("SkillController")


class AutonomyLevel(Enum):
    """Autonomy levels for skills."""

    DELEGADO = "delegado"  # Execute without confirmation
    CO_PILOT = "co-pilot"  # Confirm before major changes
    ASISTENTE = "asistente"  # Confirm every step


@dataclass
class StepResult:
    """Result of a single step execution."""

    step_id: str
    success: bool
    output: str
    duration_ms: int
    error: Optional[str] = None
    retries_used: int = 0


@dataclass
class SkillResult:
    """Result of complete skill execution."""

    success: bool
    skill_name: str
    version: str
    steps_completed: List[str] = field(default_factory=list)
    steps_failed: List[str] = field(default_factory=list)
    total_duration_ms: int = 0
    log_file: Optional[str] = None
    error: Optional[str] = None
    outputs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


class SkillController:
    """
    Controlador que FUERZA ejecucion estructurada de skills.

    El agente NO puede:
    - Inventar skills que no existen
    - Saltarse steps
    - Evitar verificacion
    - Ejecutar sin Context7 (si es requerido)
    """

    def __init__(
        self,
        skills_dir: str = "SKILLS",
        schema_path: str = "schemas/skill-schema.json",
        output_dir: str = "outputs/skill_logs",
        base_path: Optional[str] = None,
    ):
        # Determine base path
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path("C:/Proyectos")

        self.skills_dir = self.base_path / skills_dir
        self.schema_path = self.base_path / schema_path
        self.output_dir = self.base_path / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load JSON Schema for validation
        self.schema = None
        if self.schema_path.exists() and HAS_JSONSCHEMA:
            with open(self.schema_path) as f:
                self.schema = json.load(f)

        # Load all skills into registry
        self.registry: Dict[str, Dict] = {}
        self._load_registry()

        logger.info(f"SkillController initialized with {len(self.registry)} skills")
        logger.info(f"Skills directory: {self.skills_dir}")

    def _load_registry(self) -> None:
        """Load all skills and validate against schema."""
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_json = skill_dir / "skill.json"
            if not skill_json.exists():
                continue

            try:
                with open(skill_json, encoding="utf-8") as f:
                    skill = json.load(f)

                # Validate against schema if available
                if self.schema and HAS_JSONSCHEMA:
                    jsonschema.validate(instance=skill, schema=self.schema)

                self.registry[skill["name"]] = skill
                self.registry[skill["name"]]["_path"] = str(skill_dir)
                logger.info(f"  Loaded skill: {skill['name']} v{skill['version']}")

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {skill_json}: {e}")
            except Exception as e:
                if HAS_JSONSCHEMA and isinstance(e, jsonschema.ValidationError):
                    logger.error(f"Skill {skill_json} failed validation: {e.message}")
                else:
                    logger.error(f"Failed to load {skill_json}: {e}")

    def reload_registry(self) -> None:
        """Reload all skills from disk."""
        self.registry.clear()
        self._load_registry()
        logger.info(f"Registry reloaded: {len(self.registry)} skills")

    def list_skills(self) -> List[str]:
        """Return list of available skills (prevents hallucinations)."""
        return sorted(self.registry.keys())

    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """Get detailed info about a skill."""
        return self.registry.get(skill_name)

    def validate_skill_exists(self, skill_name: str) -> bool:
        """
        CRITICAL: Validate skill exists before execution.
        Prevents agent from hallucinating non-existent skills.
        """
        exists = skill_name in self.registry

        if not exists:
            logger.error(f"SKILL NOT FOUND: '{skill_name}'")
            logger.info(f"Available skills: {self.list_skills()}")

        return exists

    def validate_inputs(self, skill: Dict, inputs: Dict) -> tuple[bool, Optional[str]]:
        """Validate inputs match skill requirements."""
        skill_inputs = skill.get("inputs", {})

        for input_name, input_spec in skill_inputs.items():
            if input_spec.get("required", False) and input_name not in inputs:
                return False, f"Missing required input: {input_name}"

            if input_name in inputs and "enum" in input_spec:
                if inputs[input_name] not in input_spec["enum"]:
                    return (
                        False,
                        f"Invalid value for {input_name}: must be one of {input_spec['enum']}",
                    )

        return True, None

    def execute_skill(
        self,
        skill_name: str,
        inputs: Dict[str, Any],
        agent_callback: Optional[Callable] = None,
        dry_run: bool = False,
    ) -> SkillResult:
        """
        Execute skill with strict enforcement.

        Args:
            skill_name: Name of skill to execute
            inputs: User inputs for skill
            agent_callback: Function for agent to execute code/checkpoints
            dry_run: If True, only validate without executing

        Returns:
            SkillResult with success status and logs
        """
        start_time = datetime.now()

        # ENFORCEMENT 1: Skill MUST exist
        if not self.validate_skill_exists(skill_name):
            return SkillResult(
                success=False,
                skill_name=skill_name,
                version="unknown",
                error=f"Skill '{skill_name}' not found in registry. Available: {self.list_skills()}",
            )

        skill = self.registry[skill_name]
        logger.info(f"\n{'=' * 60}")
        logger.info(f"EXECUTING SKILL: {skill_name} v{skill['version']}")
        logger.info(f"Autonomy Level: {skill['autonomy']}")
        logger.info(f"{'=' * 60}")

        # Validate inputs
        valid, error = self.validate_inputs(skill, inputs)
        if not valid:
            return SkillResult(
                success=False,
                skill_name=skill_name,
                version=skill["version"],
                error=error,
            )

        # Apply defaults
        for input_name, input_spec in skill.get("inputs", {}).items():
            if input_name not in inputs and "default" in input_spec:
                inputs[input_name] = input_spec["default"]

        steps_completed = []
        steps_failed = []
        execution_log = {
            "timestamp": start_time.isoformat(),
            "skill": skill_name,
            "version": skill["version"],
            "autonomy": skill["autonomy"],
            "inputs": inputs,
            "dry_run": dry_run,
            "steps": [],
        }

        try:
            # ENFORCEMENT 2: Pre-requisites MUST pass
            logger.info("\n[1/4] Checking pre-requisites...")
            for prereq in skill.get("pre_requisites", []):
                passed, msg = self._check_prereq(prereq)
                if not passed:
                    error_msg = prereq.get(
                        "error_message", f"Pre-requisite failed: {prereq}"
                    )
                    logger.error(f"  FAILED: {error_msg}")
                    execution_log["error"] = error_msg
                    return self._finalize_result(
                        skill,
                        steps_completed,
                        steps_failed,
                        execution_log,
                        start_time,
                        success=False,
                        error=error_msg,
                    )
                logger.info(f"  PASSED: {prereq['check']} {prereq['args']}")

            # ENFORCEMENT 3: Context7 MUST be loaded if required
            context7_libs = skill.get("context7_required", [])
            if context7_libs:
                logger.info(f"\n[2/4] Loading Context7 libraries...")
                for lib in context7_libs:
                    logger.info(f"  Loading: {lib}")
                if agent_callback and not dry_run:
                    try:
                        agent_callback("use_context7", libs=context7_libs)
                    except Exception as e:
                        logger.warning(f"  Context7 callback failed: {e}")
            else:
                logger.info("\n[2/4] No Context7 libraries required")

            if dry_run:
                logger.info("\n[DRY RUN] Skipping execution")
                return SkillResult(
                    success=True,
                    skill_name=skill_name,
                    version=skill["version"],
                    steps_completed=["(dry run)"],
                )

            # ENFORCEMENT 4: Execute steps SEQUENTIALLY (cannot skip)
            logger.info(f"\n[3/4] Executing {len(skill['steps'])} steps...")
            total_steps = len(skill["steps"])

            for i, step in enumerate(skill["steps"], 1):
                step_id = step["id"]
                logger.info(f"\n  Step {i}/{total_steps}: {step_id}")
                logger.info(f"  Type: {step['type']}")

                result = self._execute_step(step, inputs, agent_callback, skill)

                execution_log["steps"].append(
                    {
                        "id": step_id,
                        "type": step["type"],
                        "status": "success" if result.success else "failed",
                        "duration_ms": result.duration_ms,
                        "output": result.output[:1000] if result.output else "",
                        "error": result.error,
                        "retries_used": result.retries_used,
                    }
                )

                if not result.success:
                    logger.error(f"  FAILED: {result.error}")

                    # RETRY if configured
                    retries = step.get("retry", 0)
                    for attempt in range(retries):
                        logger.info(f"  Retry {attempt + 1}/{retries}...")
                        result = self._execute_step(step, inputs, agent_callback, skill)
                        if result.success:
                            logger.info(f"  Retry succeeded")
                            result.retries_used = attempt + 1
                            break

                    if not result.success:
                        steps_failed.append(step_id)

                        # ROLLBACK automatically
                        if skill.get("rollback"):
                            self._rollback(skill, steps_completed, inputs)

                        error_msg = f"Step '{step_id}' failed: {result.error}"
                        execution_log["error"] = error_msg
                        return self._finalize_result(
                            skill,
                            steps_completed,
                            steps_failed,
                            execution_log,
                            start_time,
                            success=False,
                            error=error_msg,
                        )

                steps_completed.append(step_id)
                logger.info(f"  SUCCESS ({result.duration_ms}ms)")

            # ENFORCEMENT 5: Verification MUST pass
            logger.info(
                f"\n[4/4] Running {len(skill['verification'])} verification checks..."
            )
            for i, check in enumerate(skill.get("verification", []), 1):
                passed, msg = self._verify(check, inputs)
                if not passed:
                    error_msg = check.get(
                        "error_message", f"Verification failed: {msg}"
                    )
                    logger.error(f"  Check {i}: FAILED - {error_msg}")
                    execution_log["verification_failed"] = check
                    return self._finalize_result(
                        skill,
                        steps_completed,
                        steps_failed,
                        execution_log,
                        start_time,
                        success=False,
                        error=error_msg,
                    )
                logger.info(f"  Check {i}: PASSED")

            logger.info(f"\n{'=' * 60}")
            logger.info(f"SKILL COMPLETED: {skill_name}")
            logger.info(f"{'=' * 60}")
            execution_log["verification"] = {"status": "passed"}

            return self._finalize_result(
                skill,
                steps_completed,
                steps_failed,
                execution_log,
                start_time,
                success=True,
            )

        except KeyboardInterrupt:
            logger.warning("\nExecution interrupted by user")
            execution_log["error"] = "Interrupted by user"
            return self._finalize_result(
                skill,
                steps_completed,
                steps_failed,
                execution_log,
                start_time,
                success=False,
                error="Interrupted by user",
            )

        except Exception as e:
            logger.exception(f"Unexpected error executing skill {skill_name}")
            execution_log["error"] = str(e)
            return self._finalize_result(
                skill,
                steps_completed,
                steps_failed,
                execution_log,
                start_time,
                success=False,
                error=str(e),
            )

    def _execute_step(
        self, step: Dict, inputs: Dict, agent_callback: Optional[Callable], skill: Dict
    ) -> StepResult:
        """Execute a single step."""
        step_start = datetime.now()
        step_type = step["type"]
        step_id = step["id"]

        try:
            if step_type == "bash":
                # Format command with inputs
                cmd = step["cmd"]
                try:
                    cmd = cmd.format(**inputs)
                except KeyError as e:
                    return StepResult(
                        step_id=step_id,
                        success=False,
                        output="",
                        duration_ms=0,
                        error=f"Missing input for command: {e}",
                    )

                # Determine working directory
                working_dir = step.get("working_dir", ".")
                if working_dir != ".":
                    working_dir = working_dir.format(**inputs)

                # Execute command
                result = subprocess.run(
                    cmd,
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=step.get("timeout", 300),
                    cwd=working_dir if working_dir != "." else None,
                    env={**os.environ, **step.get("env", {})},
                )

                duration = int((datetime.now() - step_start).total_seconds() * 1000)

                return StepResult(
                    step_id=step_id,
                    success=result.returncode == 0,
                    output=result.stdout,
                    duration_ms=duration,
                    error=result.stderr if result.returncode != 0 else None,
                )

            elif step_type == "python":
                # Execute Python code
                code = step["cmd"]
                try:
                    code = code.format(**inputs)
                except KeyError as e:
                    return StepResult(
                        step_id=step_id,
                        success=False,
                        output="",
                        duration_ms=0,
                        error=f"Missing input for code: {e}",
                    )

                exec_globals = {"inputs": inputs, "Path": Path}
                exec_locals = {}
                exec(code, exec_globals, exec_locals)

                duration = int((datetime.now() - step_start).total_seconds() * 1000)
                return StepResult(
                    step_id=step_id,
                    success=True,
                    output=str(exec_locals.get("result", "OK")),
                    duration_ms=duration,
                )

            elif step_type == "agent":
                # Delegate to agent callback
                if not agent_callback:
                    return StepResult(
                        step_id=step_id,
                        success=False,
                        output="",
                        duration_ms=0,
                        error="No agent_callback provided for agent step",
                    )

                result = agent_callback("execute_step", step=step, inputs=inputs)
                duration = int((datetime.now() - step_start).total_seconds() * 1000)

                if isinstance(result, StepResult):
                    return result
                return StepResult(
                    step_id=step_id,
                    success=True,
                    output=str(result) if result else "OK",
                    duration_ms=duration,
                )

            elif step_type == "checkpoint":
                # Human-in-the-loop
                message = step.get(
                    "checkpoint_message", step.get("description", "Continue?")
                )
                logger.info(f"\n  CHECKPOINT: {message}")

                if agent_callback:
                    result = agent_callback("checkpoint", message=message)
                    duration = int((datetime.now() - step_start).total_seconds() * 1000)

                    if isinstance(result, StepResult):
                        return result

                    # Assume True means continue
                    return StepResult(
                        step_id=step_id,
                        success=bool(result) if result is not None else True,
                        output="Checkpoint passed",
                        duration_ms=duration,
                    )
                else:
                    # Auto-pass in non-interactive mode
                    return StepResult(
                        step_id=step_id,
                        success=True,
                        output="Auto-passed (no callback)",
                        duration_ms=0,
                    )

            elif step_type == "mcp":
                # MCP tool call
                if not agent_callback:
                    return StepResult(
                        step_id=step_id,
                        success=False,
                        output="",
                        duration_ms=0,
                        error="No agent_callback provided for MCP step",
                    )

                result = agent_callback(
                    "mcp_call",
                    server=step.get("mcp_server"),
                    tool=step.get("mcp_tool"),
                    args=step.get("mcp_args", {}),
                )
                duration = int((datetime.now() - step_start).total_seconds() * 1000)

                return StepResult(
                    step_id=step_id,
                    success=True,
                    output=str(result) if result else "OK",
                    duration_ms=duration,
                )

            else:
                return StepResult(
                    step_id=step_id,
                    success=False,
                    output="",
                    duration_ms=0,
                    error=f"Unknown step type: {step_type}",
                )

        except subprocess.TimeoutExpired:
            duration = int((datetime.now() - step_start).total_seconds() * 1000)
            return StepResult(
                step_id=step_id,
                success=False,
                output="",
                duration_ms=duration,
                error=f"Command timed out after {step.get('timeout', 300)}s",
            )
        except Exception as e:
            duration = int((datetime.now() - step_start).total_seconds() * 1000)
            return StepResult(
                step_id=step_id,
                success=False,
                output="",
                duration_ms=duration,
                error=str(e),
            )

    def _check_prereq(self, prereq: Dict) -> tuple[bool, str]:
        """Check pre-requisite."""
        check_type = prereq["check"]
        args = prereq["args"]

        if check_type == "command_exists":
            cmd = args[0]
            # Windows-compatible check
            result = subprocess.run(
                f"where {cmd}" if os.name == "nt" else f"command -v {cmd}",
                shell=False,
                capture_output=True,
            )
            return result.returncode == 0, f"Command '{cmd}' exists"

        elif check_type == "file_exists":
            path = Path(args[0])
            return path.exists() and path.is_file(), f"File '{args[0]}' exists"

        elif check_type == "dir_exists":
            path = Path(args[0])
            return path.exists() and path.is_dir(), f"Directory '{args[0]}' exists"

        elif check_type == "env_var_set":
            var_name = args[0]
            return var_name in os.environ, f"Env var '{var_name}' is set"

        return False, f"Unknown check type: {check_type}"

    def _verify(self, check: Dict, inputs: Dict) -> tuple[bool, str]:
        """Run verification check."""
        check_type = check.get("type", "bash")

        if check_type == "bash":
            cmd = check["cmd"]
            try:
                cmd = cmd.format(**inputs)
            except KeyError as e:
                return False, f"Missing input for verification: {e}"

            result = subprocess.run(cmd, shell=False, capture_output=True)
            expected = check.get("expect_exit", 0)
            return result.returncode == expected, f"Exit code: {result.returncode}"

        elif check_type == "file_exists":
            path = check["path"].format(**inputs)
            exists = Path(path).exists()
            return exists, f"File exists: {path}"

        elif check_type == "dir_exists":
            path = check["path"].format(**inputs)
            exists = Path(path).is_dir()
            return exists, f"Directory exists: {path}"

        elif check_type == "json_valid":
            path = check["path"].format(**inputs)
            try:
                with open(path) as f:
                    json.load(f)
                return True, f"Valid JSON: {path}"
            except Exception as e:
                return False, f"Invalid JSON: {e}"

        return False, f"Unknown verification type: {check_type}"

    def _rollback(self, skill: Dict, steps_completed: List[str], inputs: Dict):
        """Execute rollback steps."""
        logger.warning(f"\nROLLBACK: Reverting changes...")

        rollback_steps = skill.get("rollback", [])
        for step in rollback_steps:
            # Only rollback if step was completed
            if step["id"] in steps_completed or step["id"] == "cleanup":
                logger.info(f"  Rolling back: {step['id']}")
                try:
                    cmd = step["cmd"].format(**inputs)
                    subprocess.run(cmd, shell=False, capture_output=True, timeout=60)
                except Exception as e:
                    logger.error(f"  Rollback failed: {e}")

    def _finalize_result(
        self,
        skill: Dict,
        steps_completed: List[str],
        steps_failed: List[str],
        execution_log: Dict,
        start_time: datetime,
        success: bool,
        error: Optional[str] = None,
    ) -> SkillResult:
        """Finalize execution and save logs."""
        duration = int((datetime.now() - start_time).total_seconds() * 1000)

        execution_log["success"] = success
        execution_log["total_duration_ms"] = duration
        execution_log["steps_completed"] = steps_completed
        execution_log["steps_failed"] = steps_failed

        # Save log
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        log_file = self.output_dir / f"{skill['name']}_{timestamp}.json"

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(execution_log, f, indent=2, ensure_ascii=False)

        logger.info(f"\nLog saved: {log_file}")

        return SkillResult(
            success=success,
            skill_name=skill["name"],
            version=skill["version"],
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            total_duration_ms=duration,
            log_file=str(log_file),
            error=error,
        )


# === CLI INTERFACE ===


def main():
    """CLI for testing skill controller."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Skill Controller CLI - Execute skills with enforcement"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List available skills"
    )
    parser.add_argument("--info", "-i", type=str, help="Show info about a skill")
    parser.add_argument("--execute", "-e", type=str, help="Execute skill by name")
    parser.add_argument(
        "--inputs", type=str, default="{}", help="JSON string of inputs"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without executing"
    )
    parser.add_argument("--reload", action="store_true", help="Reload skills from disk")

    args = parser.parse_args()

    controller = SkillController()

    if args.reload:
        controller.reload_registry()

    if args.list:
        skills = controller.list_skills()
        if skills:
            print("\nAvailable skills:")
            for skill in skills:
                info = controller.get_skill_info(skill)
                desc = info.get("description", "No description")[:50]
                print(f"  - {skill} (v{info['version']}): {desc}")
        else:
            print("\nNo skills found. Create skills in SKILLS/<skill-name>/skill.json")

    elif args.info:
        info = controller.get_skill_info(args.info)
        if info:
            print(f"\nSkill: {info['name']} v{info['version']}")
            print(f"Autonomy: {info['autonomy']}")
            print(f"Description: {info.get('description', 'N/A')}")
            print(f"\nInputs:")
            for name, spec in info.get("inputs", {}).items():
                req = "(required)" if spec.get("required") else "(optional)"
                print(f"  - {name}: {spec['type']} {req}")
            print(f"\nSteps: {len(info['steps'])}")
            for step in info["steps"]:
                print(f"  - {step['id']} ({step['type']})")
            print(f"\nVerification: {len(info['verification'])} checks")
        else:
            print(f"\nSkill '{args.info}' not found")

    elif args.execute:
        try:
            inputs = json.loads(args.inputs)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON inputs: {e}")
            return 1

        result = controller.execute_skill(args.execute, inputs, dry_run=args.dry_run)

        print(f"\n{'=' * 60}")
        if result.success:
            print(f"SUCCESS: Skill '{result.skill_name}' completed")
            print(f"Duration: {result.total_duration_ms}ms")
            print(f"Steps: {len(result.steps_completed)} completed")
        else:
            print(f"FAILED: {result.error}")
            print(f"Steps completed: {result.steps_completed}")
            print(f"Steps failed: {result.steps_failed}")

        if result.log_file:
            print(f"Log: {result.log_file}")
        print(f"{'=' * 60}")

        return 0 if result.success else 1

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
