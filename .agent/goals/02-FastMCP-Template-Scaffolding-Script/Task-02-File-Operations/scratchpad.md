# Task 02: File Operation Utilities

**Status:** 🟡 In Progress
**Created:** 2025-01-08
**Last Updated:** 2025-01-08

---

## Objective

Implement safe, atomic file operations with rollback support for the scaffolding tool. This provides the foundation for all file manipulations during project setup, ensuring data safety and the ability to recover from errors.

**Reference Example:** Building `optimization-mcp` - A mathematical optimization MCP server using CVXPY for convex optimization problems.

---

## Context & Research

### Why Optimization MCP as Reference?

Mathematical optimization servers are excellent reference examples because they:

1. **Rich Domain Model** - Clear problem types (LP, QP, SOCP, SDP), constraints, objectives
2. **Real-world Complexity** - Multiple file types (models, data, results), configuration, caching
3. **Data Variety** - Need to handle matrices, vectors, problem definitions, solver outputs
4. **Perfect for RefCache** - Large optimization results benefit from reference-based caching
5. **Well-defined Tools** - Solve problem, get status, retrieve results, list solvers, etc.

### Optimization Library Landscape (2025)

**CVXPY** (Recommended for reference example)
- Downloads: ~2.4M/month
- Current: Modern, actively maintained (v1.7.5)
- Best for: Convex optimization with intuitive DCP (Disciplined Convex Programming)
- Supports: OSQP, Clarabel, SCS, ECOS, Gurobi, MOSEK, CVXOPT, etc.
- Pros: Pythonic, excellent documentation, broad solver support
- Use case: Portfolio optimization, resource allocation, signal processing

**SciPy** (`scipy.optimize`)
- Part of scientific Python stack
- Good for: General-purpose optimization (unconstrained, constrained, nonlinear)
- Already in most environments
- Use case: Curve fitting, parameter estimation, minimization

**Pyomo**
- Algebraic modeling language (like GAMS/AMPL)
- Good for: Large-scale optimization, mixed-integer programming
- More verbose but very powerful
- Use case: Operations research, scheduling, network design

**Verdict:** Use **CVXPY** for the reference example - it's the modern de-facto standard for convex optimization in Python, has the right complexity level, and excellent documentation.

---

## Reference Example Structure

### optimization-mcp Project Layout

```
optimization-mcp/
├── app/
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── server.py             # MCP server with optimization tools
│   └── tools/
│       ├── __init__.py
│       ├── solvers.py        # List available solvers
│       ├── linear.py         # Linear programming (LP)
│       ├── quadratic.py      # Quadratic programming (QP)
│       ├── convex.py         # General convex problems
│       └── results.py        # Result retrieval and formatting
├── tests/
│   ├── conftest.py
│   ├── test_server.py
│   └── test_tools/
│       ├── test_linear.py
│       ├── test_quadratic.py
│       └── test_results.py
├── pyproject.toml            # Dependencies include cvxpy, numpy
├── README.md
└── docker/
    ├── Dockerfile.base
    └── Dockerfile
```

### Example Tools for optimization-mcp

```python
# app/tools/linear.py
from pydantic import BaseModel, Field
import cvxpy as cp
import numpy as np

class LinearProgramInput(BaseModel):
    """Linear programming problem: minimize c'x subject to Ax <= b, x >= 0"""
    c: list[float] = Field(description="Objective coefficients")
    A: list[list[float]] = Field(description="Constraint matrix")
    b: list[float] = Field(description="Constraint bounds")

async def solve_linear_program(
    c: list[float],
    A: list[list[float]],
    b: list[float],
    solver: str = "CLARABEL"
) -> dict:
    """Solve a linear programming problem using CVXPY."""
    # Convert to numpy arrays
    c_np = np.array(c)
    A_np = np.array(A)
    b_np = np.array(b)

    # Define optimization variables
    n = len(c)
    x = cp.Variable(n)

    # Define problem
    objective = cp.Minimize(c_np @ x)
    constraints = [A_np @ x <= b_np, x >= 0]
    problem = cp.Problem(objective, constraints)

    # Solve
    result = problem.solve(solver=solver)

    return {
        "status": problem.status,
        "optimal_value": float(problem.value) if problem.value else None,
        "optimal_solution": x.value.tolist() if x.value is not None else None,
        "solver_used": solver,
    }

# app/tools/solvers.py
async def list_available_solvers() -> dict:
    """List all optimization solvers installed and available."""
    import cvxpy as cp
    return {
        "installed_solvers": cp.installed_solvers(),
        "default_solver": "CLARABEL",
    }
```

### Example Tool Registration in server.py

```python
from app.tools.linear import solve_linear_program
from app.tools.solvers import list_available_solvers

mcp = FastMCP(
    name="Optimization MCP",
    instructions="Mathematical optimization server using CVXPY...",
)

# Simple tools (no caching needed)
mcp.tool(list_available_solvers)

# Cached tools (cache large results)
@mcp.tool
@cache.cached(namespace="problems")
async def solve_lp(c, A, b, solver="CLARABEL") -> dict:
    """Solve linear program with caching for large results."""
    return await solve_linear_program(c, A, b, solver)
```

---

## Scope

### Files to Create/Modify During Scaffolding

When scaffolding `optimization-mcp` from `fastmcp-template`, the script will:

1. **Create new project directory**
   - Copy entire template structure
   - Preserve `.git` directory structure (but re-init)

2. **Rename/Update files**
   - `pyproject.toml` → Update name, description, scripts
   - `app/server.py` → Update server name, instructions, remove demo tools
   - `README.md` → Replace template content with optimization-mcp content
   - `CHANGELOG.md` → Reset to 0.0.0
   - `docker-compose.yml` → Update service/image names
   - `docker/Dockerfile.base` → Update labels
   - `.github/workflows/*.yml` → Update image names

3. **Delete demo content**
   - Remove demo tool functions from `app/server.py`
   - Remove demo tests from `tests/test_server.py`
   - Clean up `app/tools/` if it has demo modules

4. **Add new dependencies**
   - `uv add cvxpy numpy` for optimization-mcp

---

## Implementation Plan

### Core File Operations Module

**Location:** `fastmcp_scaffold/file_ops.py`

```python
from pathlib import Path
from typing import Optional
import shutil
import tempfile
import json
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FileOperation:
    """Record of a file operation for rollback."""
    op_type: str  # "copy", "move", "delete", "create"
    src: Optional[str]
    dst: Optional[str]
    backup: Optional[str]
    timestamp: str

class TransactionLog:
    """Track all file operations for rollback support."""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.operations: list[FileOperation] = []
        self.log_file = log_dir / f"transaction_{datetime.now().isoformat()}.json"

    def record(self, operation: FileOperation) -> None:
        """Record an operation."""
        self.operations.append(operation)
        self._persist()

    def _persist(self) -> None:
        """Save transaction log to disk."""
        with open(self.log_file, 'w') as f:
            json.dump([asdict(op) for op in self.operations], f, indent=2)

    def rollback(self) -> None:
        """Rollback all operations in reverse order."""
        for op in reversed(self.operations):
            if op.op_type == "copy" and op.dst:
                Path(op.dst).unlink(missing_ok=True)
            elif op.op_type == "move" and op.backup:
                shutil.move(op.backup, op.src)
            elif op.op_type == "delete" and op.backup:
                shutil.copy2(op.backup, op.dst)

def validate_path(path: Path, base_dir: Path) -> Path:
    """Validate path is within base directory (prevent escapes)."""
    resolved = path.resolve()
    base_resolved = base_dir.resolve()

    if not str(resolved).startswith(str(base_resolved)):
        raise ValueError(f"Path {path} escapes base directory {base_dir}")

    return resolved

def safe_copy(
    src: Path,
    dst: Path,
    base_dir: Path,
    transaction_log: TransactionLog,
) -> None:
    """Safely copy a file with validation and logging."""
    src = validate_path(src, base_dir)
    dst = validate_path(dst, base_dir)

    # Create parent directory if needed
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Perform copy
    shutil.copy2(src, dst)

    # Log operation
    transaction_log.record(FileOperation(
        op_type="copy",
        src=str(src),
        dst=str(dst),
        backup=None,
        timestamp=datetime.now().isoformat(),
    ))

def safe_move(
    src: Path,
    dst: Path,
    base_dir: Path,
    transaction_log: TransactionLog,
) -> None:
    """Safely move a file with backup for rollback."""
    src = validate_path(src, base_dir)
    dst = validate_path(dst, base_dir)

    # Create backup of source
    backup_dir = Path(tempfile.gettempdir()) / "fastmcp_scaffold_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{src.name}_{datetime.now().timestamp()}"
    shutil.copy2(src, backup_path)

    # Create parent directory if needed
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Perform move
    shutil.move(src, dst)

    # Log operation
    transaction_log.record(FileOperation(
        op_type="move",
        src=str(src),
        dst=str(dst),
        backup=str(backup_path),
        timestamp=datetime.now().isoformat(),
    ))

def safe_delete(
    path: Path,
    base_dir: Path,
    transaction_log: TransactionLog,
) -> None:
    """Safely delete a file with backup for rollback."""
    path = validate_path(path, base_dir)

    if not path.exists():
        return  # Idempotent

    # Create backup
    backup_dir = Path(tempfile.gettempdir()) / "fastmcp_scaffold_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}_{datetime.now().timestamp()}"
    shutil.copy2(path, backup_path)

    # Perform delete
    path.unlink()

    # Log operation
    transaction_log.record(FileOperation(
        op_type="delete",
        src=None,
        dst=str(path),
        backup=str(backup_path),
        timestamp=datetime.now().isoformat(),
    ))

def backup_project(project_path: Path) -> Path:
    """Create full backup of project directory."""
    backup_dir = Path(tempfile.gettempdir()) / "fastmcp_scaffold_backup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{project_path.name}_{timestamp}"

    shutil.copytree(project_path, backup_path, symlinks=True)

    return backup_path

def restore_backup(backup_path: Path, project_path: Path) -> None:
    """Restore project from backup."""
    if project_path.exists():
        shutil.rmtree(project_path)

    shutil.copytree(backup_path, project_path, symlinks=True)
```

---

## Implementation Checklist

### Phase 1: Core Operations (2 hours)
- [ ] Create `fastmcp_scaffold/file_ops.py` module
- [ ] Implement `FileOperation` dataclass
- [ ] Implement `TransactionLog` class with persistence
- [ ] Implement `validate_path()` with security checks
- [ ] Implement `safe_copy()` with logging
- [ ] Implement `safe_move()` with backup
- [ ] Implement `safe_delete()` with backup
- [ ] Implement `backup_project()` full backup
- [ ] Implement `restore_backup()` full restore

### Phase 2: Testing (3 hours)
- [ ] Write tests for `validate_path()` (escape attempts, relative paths)
- [ ] Write tests for `safe_copy()` (success, conflicts, permissions)
- [ ] Write tests for `safe_move()` (success, rollback scenario)
- [ ] Write tests for `safe_delete()` (success, rollback scenario)
- [ ] Write tests for `TransactionLog` (persistence, rollback)
- [ ] Write tests for `backup_project()` and `restore_backup()`
- [ ] Test rollback with multiple operations
- [ ] Test cross-platform compatibility (Linux, macOS, Windows paths)
- [ ] Test error handling (disk full, permissions, etc.)

### Phase 3: Integration (1 hour)
- [ ] Integrate with CLI module (when ready)
- [ ] Test with optimization-mcp scaffolding flow
- [ ] Document usage examples in module docstrings
- [ ] Update goal scratchpad with completion notes

---

## Testing Strategy

### Unit Tests

```python
# tests/test_file_ops.py
import pytest
from pathlib import Path
import tempfile
from fastmcp_scaffold.file_ops import (
    validate_path,
    safe_copy,
    safe_move,
    safe_delete,
    TransactionLog,
    backup_project,
    restore_backup,
)

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    project = tmp_path / "test_project"
    project.mkdir()
    (project / "file1.txt").write_text("content1")
    (project / "subdir").mkdir()
    (project / "subdir" / "file2.txt").write_text("content2")
    return project

def test_validate_path_success(temp_project):
    """Test path validation within base directory."""
    path = temp_project / "file1.txt"
    validated = validate_path(path, temp_project)
    assert validated.exists()

def test_validate_path_escape_attempt(temp_project):
    """Test that path escapes are rejected."""
    with pytest.raises(ValueError, match="escapes base directory"):
        validate_path(Path("../../etc/passwd"), temp_project)

def test_safe_copy_creates_file(temp_project, tmp_path):
    """Test safe_copy creates destination file."""
    log = TransactionLog(tmp_path / "logs")
    src = temp_project / "file1.txt"
    dst = temp_project / "file1_copy.txt"

    safe_copy(src, dst, temp_project, log)

    assert dst.exists()
    assert dst.read_text() == "content1"
    assert len(log.operations) == 1

def test_safe_move_with_rollback(temp_project, tmp_path):
    """Test safe_move and rollback restores original."""
    log = TransactionLog(tmp_path / "logs")
    src = temp_project / "file1.txt"
    dst = temp_project / "moved.txt"

    safe_move(src, dst, temp_project, log)
    assert dst.exists()
    assert not src.exists()

    # Rollback
    log.rollback()
    assert src.exists()
    assert src.read_text() == "content1"

def test_safe_delete_with_rollback(temp_project, tmp_path):
    """Test safe_delete and rollback restores file."""
    log = TransactionLog(tmp_path / "logs")
    path = temp_project / "file1.txt"
    original_content = path.read_text()

    safe_delete(path, temp_project, log)
    assert not path.exists()

    # Rollback
    log.rollback()
    assert path.exists()
    assert path.read_text() == original_content

def test_backup_and_restore_project(temp_project):
    """Test full project backup and restore."""
    # Create backup
    backup = backup_project(temp_project)
    assert backup.exists()

    # Modify original
    (temp_project / "file1.txt").write_text("modified")

    # Restore
    restore_backup(backup, temp_project)
    assert (temp_project / "file1.txt").read_text() == "content1"
```

---

## Success Criteria

- [ ] All file operations are atomic (no partial states)
- [ ] Path validation prevents directory escapes
- [ ] Transaction log persists to disk
- [ ] Rollback successfully undoes all operations
- [ ] Cross-platform compatibility verified
- [ ] ≥90% test coverage for file_ops module
- [ ] No data loss in error scenarios
- [ ] Performance: <100ms per operation for typical files

---

## Next Steps

After completing Task-02:

1. Move to **Task-03: Demo Tool Cleanup Logic** - Use file operations to clean demo tools
2. Test integration: Scaffold `optimization-mcp` from template
3. Verify all demo tools removed, new structure created
4. Document any edge cases discovered

---

## Design Decisions

### Why Transaction Log vs Git Operations?

- **Transaction log** gives us fine-grained control and rollback
- Git is overkill for temporary scaffolding operations
- Transaction log is faster and simpler
- We can still use git for final project initialization

### Why Temp Directory for Backups?

- Keeps project directory clean during scaffolding
- System temp is automatically cleaned
- Easy to find for debugging (consistent location)
- Cross-platform temp directory handling via `tempfile`

### Why Not Use `shutil.copytree` Directly?

- Need transaction logging for rollback
- Need path validation for security
- Need to track individual operations for fine-grained rollback
- `shutil` operations wrapped in our safety layer

---

## Reference Implementation Timeline

**Estimated: 6-7 hours total**

- Core operations: 2 hours
- Testing: 3 hours
- Integration: 1 hour
- Documentation: 1 hour

---

## Notes

- Use `pathlib.Path` exclusively for cross-platform compatibility
- All operations should be idempotent where possible
- Transaction log should survive crashes (persist after each operation)
- Consider using `fcntl.flock()` on Unix for file locking in future
- Windows path length limits: use `\\?\` prefix if needed
- Symlinks: `shutil.copytree(symlinks=True)` preserves them
