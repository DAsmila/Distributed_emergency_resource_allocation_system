"""
Fault Tolerance Module.

Provides:
  - NodeRegistry     : tracks health of distributed system nodes.
  - CircuitBreaker   : prevents cascading failures when a service is unhealthy.
  - ReplicationManager: replicates critical data across multiple nodes.
  - HealthMonitor    : periodic health checks with automatic failover logic.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional, Any


# ---------------------------------------------------------------------- #
# Node registry                                                           #
# ---------------------------------------------------------------------- #

class NodeStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"
    STANDBY = "standby"


@dataclass
class Node:
    """Represents a single node in the distributed system."""

    id: str
    host: str
    port: int
    role: str = "primary"  # primary | replica | standby
    status: NodeStatus = NodeStatus.HEALTHY
    district_id: Optional[str] = None
    last_heartbeat: float = field(default_factory=time.time)
    failed_checks: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def is_healthy(self) -> bool:
        return self.status == NodeStatus.HEALTHY

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "host": self.host,
            "port": self.port,
            "role": self.role,
            "status": self.status.value,
            "district_id": self.district_id,
            "last_heartbeat": datetime.fromtimestamp(
                self.last_heartbeat, tz=timezone.utc
            ).isoformat(),
            "failed_checks": self.failed_checks,
        }


class NodeRegistry:
    """Maintains the list of all nodes and their current health status."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}
        self._lock = threading.Lock()
        self._seed_default_nodes()

    def _seed_default_nodes(self) -> None:
        defaults = [
            Node(id="node-state-primary", host="10.0.0.1", port=5000,
                 role="primary", district_id=None),
            Node(id="node-state-replica", host="10.0.0.2", port=5000,
                 role="replica", district_id=None),
            Node(id="node-zone-north", host="10.0.1.1", port=5000,
                 role="primary", district_id="TN-CHE"),
            Node(id="node-zone-south", host="10.0.2.1", port=5000,
                 role="primary", district_id="TN-MDU"),
            Node(id="node-zone-west", host="10.0.3.1", port=5000,
                 role="primary", district_id="TN-CBE"),
        ]
        for node in defaults:
            self._nodes[node.id] = node

    def register(self, node: Node) -> Node:
        with self._lock:
            self._nodes[node.id] = node
        return node

    def deregister(self, node_id: str) -> bool:
        with self._lock:
            return bool(self._nodes.pop(node_id, None))

    def get(self, node_id: str) -> Optional[Node]:
        return self._nodes.get(node_id)

    def list_nodes(
        self,
        status: Optional[NodeStatus] = None,
        role: Optional[str] = None,
    ) -> List[Node]:
        with self._lock:
            nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        if role:
            nodes = [n for n in nodes if n.role == role]
        return nodes

    def record_heartbeat(self, node_id: str) -> bool:
        node = self._nodes.get(node_id)
        if node is None:
            return False
        node.last_heartbeat = time.time()
        node.failed_checks = 0
        node.status = NodeStatus.HEALTHY
        return True

    def mark_failed(self, node_id: str) -> None:
        node = self._nodes.get(node_id)
        if node:
            node.failed_checks += 1
            node.status = (
                NodeStatus.DEGRADED if node.failed_checks < 3
                else NodeStatus.UNREACHABLE
            )

    def get_healthy_nodes(self) -> List[Node]:
        return self.list_nodes(status=NodeStatus.HEALTHY)

    def failover_for(self, failed_node_id: str) -> Optional[Node]:
        """
        Return the best healthy replica/standby to take over for a failed node.
        Prefers same district, then any healthy node.
        """
        failed = self._nodes.get(failed_node_id)
        district = failed.district_id if failed else None

        healthy = self.get_healthy_nodes()
        healthy = [n for n in healthy if n.id != failed_node_id]

        if district:
            same_district = [n for n in healthy if n.district_id == district]
            if same_district:
                return same_district[0]

        replicas = [n for n in healthy if n.role == "replica"]
        if replicas:
            return replicas[0]

        return healthy[0] if healthy else None

    def to_dict(self) -> list:
        return [n.to_dict() for n in self._nodes.values()]


# ---------------------------------------------------------------------- #
# Circuit breaker                                                         #
# ---------------------------------------------------------------------- #

class CircuitState(str, Enum):
    CLOSED = "closed"      # normal operation
    OPEN = "open"          # blocking calls (service is failing)
    HALF_OPEN = "half_open"  # probing if service recovered


class CircuitBreaker:
    """
    Classic circuit-breaker pattern.

    * CLOSED  → calls pass through; failures increment a counter.
    * OPEN    → calls are rejected immediately; retried after *reset_timeout*.
    * HALF-OPEN → one probe call is allowed; success → CLOSED, failure → OPEN.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time: Optional[float] = None
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if (
                    self._last_failure_time is not None
                    and time.time() - self._last_failure_time > self.reset_timeout
                ):
                    self._state = CircuitState.HALF_OPEN
            return self._state

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute *func* through the circuit breaker."""
        current_state = self.state
        if current_state == CircuitState.OPEN:
            raise CircuitOpenError(f"Circuit '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure()
            raise exc

    def _on_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        with self._lock:
            self._failures += 1
            self._last_failure_time = time.time()
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN

    def reset(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = CircuitState.CLOSED
            self._last_failure_time = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self._failures,
            "failure_threshold": self.failure_threshold,
            "reset_timeout": self.reset_timeout,
        }


class CircuitOpenError(Exception):
    """Raised when a call is attempted against an open circuit."""


# ---------------------------------------------------------------------- #
# Replication manager                                                     #
# ---------------------------------------------------------------------- #

class ReplicationManager:
    """
    Manages in-memory replication of critical data snapshots across nodes.
    In a real deployment this would push to remote node endpoints; here it
    maintains a local replica log for fault-tolerance simulation.
    """

    def __init__(self, registry: NodeRegistry) -> None:
        self._registry = registry
        self._replicas: Dict[str, Dict[str, Any]] = {}  # node_id → data snapshot
        self._lock = threading.Lock()

    def replicate(self, key: str, data: Any) -> List[str]:
        """
        Store *data* under *key* on all healthy replica nodes.
        Returns list of node IDs that received the data.
        """
        replicas = self._registry.list_nodes(role="replica")
        succeeded: List[str] = []
        for node in replicas:
            if not node.is_healthy:
                continue
            with self._lock:
                if node.id not in self._replicas:
                    self._replicas[node.id] = {}
                self._replicas[node.id][key] = data
            succeeded.append(node.id)
        return succeeded

    def get_replica(self, node_id: str, key: str) -> Optional[Any]:
        with self._lock:
            return self._replicas.get(node_id, {}).get(key)

    def recover(self, node_id: str) -> Dict[str, Any]:
        """Return all data stored for *node_id* (used during node recovery)."""
        with self._lock:
            return dict(self._replicas.get(node_id, {}))


# ---------------------------------------------------------------------- #
# Health monitor                                                          #
# ---------------------------------------------------------------------- #

class HealthMonitor:
    """
    Background thread that periodically checks node health and triggers
    failover when nodes become unreachable.
    """

    HEARTBEAT_TIMEOUT = 60.0   # seconds before a node is considered stale
    CHECK_INTERVAL = 15.0      # seconds between health checks

    def __init__(
        self,
        registry: NodeRegistry,
        replication_manager: Optional[ReplicationManager] = None,
    ) -> None:
        self._registry = registry
        self._replication = replication_manager
        self._failover_callbacks: List[Callable[[str, Optional[Node]], None]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def add_failover_callback(
        self, cb: Callable[[str, Optional[Node]], None]
    ) -> None:
        """Register a callback invoked as ``cb(failed_node_id, replacement_node)``."""
        self._failover_callbacks.append(cb)

    def start(self) -> None:
        """Start the background monitoring thread (non-blocking)."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="health-monitor"
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._check_all()
            self._stop_event.wait(timeout=self.CHECK_INTERVAL)

    def _check_all(self) -> None:
        now = time.time()
        for node in self._registry.list_nodes():
            stale = now - node.last_heartbeat > self.HEARTBEAT_TIMEOUT
            if stale and node.is_healthy:
                self._registry.mark_failed(node.id)
                if self._registry.get(node.id).status == NodeStatus.UNREACHABLE:
                    replacement = self._registry.failover_for(node.id)
                    for cb in self._failover_callbacks:
                        cb(node.id, replacement)

    def run_check_once(self) -> Dict[str, str]:
        """Execute a single health-check pass and return a status report."""
        self._check_all()
        return {
            n.id: n.status.value for n in self._registry.list_nodes()
        }

    def status_report(self) -> dict:
        nodes = self._registry.list_nodes()
        healthy = sum(1 for n in nodes if n.is_healthy)
        return {
            "total_nodes": len(nodes),
            "healthy": healthy,
            "degraded": sum(
                1 for n in nodes if n.status == NodeStatus.DEGRADED
            ),
            "unreachable": sum(
                1 for n in nodes if n.status == NodeStatus.UNREACHABLE
            ),
            "nodes": [n.to_dict() for n in nodes],
        }


# ---------------------------------------------------------------------- #
# Module-level singletons                                                 #
# ---------------------------------------------------------------------- #

node_registry = NodeRegistry()
replication_manager = ReplicationManager(node_registry)
health_monitor = HealthMonitor(node_registry, replication_manager)
