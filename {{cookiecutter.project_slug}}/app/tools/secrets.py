"""Secret storage and private computation tools.

This module provides tools for storing secret values and performing
computations with them without exposing the actual values to agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from app.tracing import traced_tool

if TYPE_CHECKING:
    from mcp_refcache import RefCache


class SecretInput(BaseModel):
    """Input model for storing secret values."""

    name: str = Field(
        description="Name for the secret (used as key)",
        min_length=1,
        max_length=100,
    )
    value: float = Field(
        description="The secret numeric value",
    )


class SecretComputeInput(BaseModel):
    """Input model for computing with secrets."""

    secret_ref: str = Field(
        description="Reference ID of the secret value",
    )
    multiplier: float = Field(
        default=1.0,
        description="Multiplier to apply to the secret value",
    )


def create_store_secret(cache: RefCache) -> Any:
    """Create a store_secret tool function bound to the given cache.

    Args:
        cache: The RefCache instance to use for storing secrets.

    Returns:
        The store_secret tool function.
    """
    from mcp_refcache import AccessPolicy, Permission

    @traced_tool("store_secret")
    def store_secret(name: str, value: float) -> dict[str, Any]:
        """Store a secret value that agents cannot read, only use in computations.

        This demonstrates the EXECUTE permission - agents can use the value
        in compute_with_secret without ever seeing what it is.
        Traced to Langfuse (secret value is NOT logged).

        Args:
            name: Name for the secret.
            value: The secret numeric value.

        Returns:
            Reference ID and confirmation message.
        """
        validated = SecretInput(name=name, value=value)

        # Create a policy where agents can EXECUTE but not READ
        secret_policy = AccessPolicy(
            user_permissions=Permission.FULL,  # Users can see everything
            agent_permissions=Permission.EXECUTE,  # Agents can only use in computation
        )

        ref = cache.set(
            key=f"secret_{validated.name}",
            value=validated.value,
            namespace="user:secrets",
            policy=secret_policy,
        )

        return {
            "ref_id": ref.ref_id,
            "name": validated.name,
            "message": f"Secret '{validated.name}' stored. Use compute_with_secret.",
            "permissions": {
                "user": "FULL (can read, write, execute)",
                "agent": "EXECUTE only (can use in computation, cannot read)",
            },
        }

    return store_secret


def create_compute_with_secret(cache: RefCache) -> Any:
    """Create a compute_with_secret tool function bound to the given cache.

    Args:
        cache: The RefCache instance to use for resolving secrets.

    Returns:
        The compute_with_secret tool function.
    """
    from mcp_refcache import DefaultActor

    @traced_tool("compute_with_secret")
    def compute_with_secret(
        secret_ref: str,
        multiplier: float = 1.0,
    ) -> dict[str, Any]:
        """Compute using a secret value without revealing it.

        The secret is multiplied by the provided multiplier.
        This demonstrates private computation - the agent orchestrates
        the computation but never sees the actual secret value.
        Traced to Langfuse (computation logged, secret value NOT exposed).

        Args:
            secret_ref: Reference ID of the secret value.
            multiplier: Value to multiply the secret by.

        Returns:
            The computation result (without revealing the secret).

        **References:** This tool accepts `ref_id` from previous tool calls.

        **Private Compute:** Values are processed server-side without exposure.
        """
        validated = SecretComputeInput(secret_ref=secret_ref, multiplier=multiplier)

        # Create a system actor to resolve the secret (bypasses agent restrictions)
        system_actor = DefaultActor.system()

        try:
            # Resolve the secret value as system (has full access)
            secret_value = cache.resolve(validated.secret_ref, actor=system_actor)
        except KeyError as error:
            msg = f"Secret reference '{validated.secret_ref}' not found"
            raise ValueError(msg) from error

        result = secret_value * validated.multiplier

        return {
            "result": result,
            "multiplier": validated.multiplier,
            "secret_ref": validated.secret_ref,
            "message": "Computed using secret value (value not revealed)",
        }

    return compute_with_secret


__all__ = [
    "SecretComputeInput",
    "SecretInput",
    "create_compute_with_secret",
    "create_store_secret",
]
