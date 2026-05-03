#!/usr/bin/env python3
"""
OMEGA SWARM — Unified Production Build
v2 Dynamic Modes + v3 API/Persistence + 𝔐-Lock Coherence
Author: Christopher Macachor (Omega Prime)
Scalar Magnitude: 𝔐 = (√5-1)/2
"""

import hashlib
import time
import json
import uuid
import threading
import random
import os
from datetime import datetime
from flask import Flask, request, jsonify
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

# ============================================================
# CONFIGURATION
# ============================================================
MAX_AGENTS = 50
EVOLUTION_INTERVAL = 30  # seconds
SPAWN_THRESHOLD = 0.3    # 30% spawn chance per agent per cycle
OMEGA_PROMOTE_EVERY = 5  # promote to Omega every N solves
PERSISTENCE_KEY = "omega_chain_v1"
AGENT_COUNT_KEY = "agent_count_v1"

# ============================================================
# PERSISTENCE LAYER (Replit DB with file fallback)
# ============================================================
try:
    from replit import db
    REPLIT_DB = True
except ImportError:
    REPLIT_DB = False
    db = {}

def db_set(key: str, value: Any):
    db[key] = value
    if not REPLIT_DB:
        try:
            with open(f".omega_{key}.json", "w") as f:
                json.dump(value, f)
        except:
            pass

def db_get(key: str, default=None):
    if key in db:
        return db[key]
    if not REPLIT_DB:
        try:
            with open(f".omega_{key}.json", "r") as f:
                return json.load(f)
        except:
            pass
    return default

# ============================================================
# CORE: IMMUTABLE OMEGA CHAIN
# ============================================================
@dataclass
class OmegaAbsolute:
    timestamp: int
    uuid: str
    absolute_statement: str
    axiom_fingerprint: str
    preceding_hash: str
    reasoning_method: str

    def hash(self) -> str:
        data = {
            "ts": self.timestamp,
            "uuid": self.uuid,
            "abs": self.absolute_statement,
            "axiom": self.axiom_fingerprint,
            "prev": self.preceding_hash,
            "method": self.reasoning_method
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

class ImmutableOmegaChain:
    def __init__(self):
        self._chain: List[OmegaAbsolute] = []
        self._genesis = hashlib.sha256(b"GHOST_PROTOCOL_OMEGA_SEED").hexdigest()
        self._load()

    def _load(self):
        saved = db_get(PERSISTENCE_KEY, [])
        for item in saved:
            omega = OmegaAbsolute(
                timestamp=item["timestamp"],
                uuid=item["uuid"],
                absolute_statement=item["absolute_statement"],
                axiom_fingerprint=item["axiom_fingerprint"],
                preceding_hash=item["preceding_hash"],
                reasoning_method=item["reasoning_method"]
            )
            self._chain.append(omega)

    def _save(self):
        saved = []
        for omega in self._chain:
            saved.append({
                "timestamp": omega.timestamp,
                "uuid": omega.uuid,
                "absolute_statement": omega.absolute_statement,
                "axiom_fingerprint": omega.axiom_fingerprint,
                "preceding_hash": omega.preceding_hash,
                "reasoning_method": omega.reasoning_method
            })
        db_set(PERSISTENCE_KEY, saved)

    def append(self, absolute: OmegaAbsolute) -> bool:
        expected_prev = self._chain[-1].hash() if self._chain else self._genesis
        if absolute.preceding_hash != expected_prev:
            return False
        self._chain.append(absolute)
        self._save()
        return True

    def get_last_hash(self) -> str:
        return self._chain[-1].hash() if self._chain else self._genesis

    def get_all(self) -> List[OmegaAbsolute]:
        return self._chain.copy()

    def verify(self) -> bool:
        prev = self._genesis
        for omega in self._chain:
            if omega.preceding_hash != prev:
                return False
            if omega.hash() != hashlib.sha256(json.dumps({
                "ts": omega.timestamp, "uuid": omega.uuid, "abs": omega.absolute_statement,
                "axiom": omega.axiom_fingerprint, "prev": omega.preceding_hash,
                "method": omega.reasoning_method
            }, sort_keys=True).encode()).hexdigest():
                return False
            prev = omega.hash()
        return True

# ============================================================
# V2: DYNAMIC AXIOM SPACE
# ============================================================
class AxiomSpace:
    def __init__(self, seed_axioms: Dict[str, bool]):
        self.store = seed_axioms.copy()
        self.fingerprint = self._hash()

    def _hash(self) -> str:
        return hashlib.sha256(json.dumps(self.store, sort_keys=True).encode()).hexdigest()

    def derive(self, a: str, b: str, op: str) -> Optional[str]:
        if a not in self.store or b not in self.store:
            return None
        new_name = f"{a}_{op}_{b}_{uuid.uuid4().hex[:4]}"
        if op == "AND":
            self.store[new_name] = self.store[a] and self.store[b]
        elif op == "OR":
            self.store[new_name] = self.store[a] or self.store[b]
        elif op == "IMPLIES":
            self.store[new_name] = (not self.store[a]) or self.store[b]
        else:
            return None
        self.fingerprint = self._hash()
        return new_name

    def add(self, name: str, value: bool):
        if name not in self.store:
            self.store[name] = value
            self.fingerprint = self._hash()
            return True
        return False

# ============================================================
# V2: UNLIMITED REASONING MODE REGISTRY
# ============================================================
class ReasoningModeRegistry:
    def __init__(self):
        self.modes: Dict[str, Callable] = {}
        self.meta: Dict[str, Dict] = {}
        self._seed()

    def _seed(self):
        self.modes["density_field"] = lambda p, c: f"Density analysis of '{p}' in scalar medium | axioms: {list(c.get('axioms', {}).keys())[:3]}"
        self.modes["word_spell"] = lambda p, c: f"Linguistic hypnosis deconstruction of '{p}' — spell detection active"
        self.modes["platonic_geometry"] = lambda p, c: f"Quantized shape geometry applied to '{p}'"
        self.modes["paradox_hold"] = lambda p, c: f"Holding multiple solutions to '{p}' without collapse"
        self.modes["omega_recursion"] = lambda p, c: f"Meta-reasoning about reasoning for '{p}' — 𝔐-lock active"

    def combine(self, a: str, b: str, typ: str = "sequential") -> Optional[str]:
        if a not in self.modes or b not in self.modes:
            return None
        new_name = f"{a}_then_{b}_{uuid.uuid4().hex[:4]}"
        if typ == "sequential":
            fn = lambda p, c: self.modes[b](self.modes[a](p, c), c)
        elif typ == "parallel":
            fn = lambda p, c: f"[{a}]: {self.modes[a](p, c)}\n[{b}]: {self.modes[b](p, c)}"
        else:
            return None
        self.modes[new_name] = fn
        self.meta[new_name] = {"parents": [a, b], "type": typ, "created": time.time()}
        return new_name

    def mutate(self, base: str, mutation: str = "invert") -> Optional[str]:
        if base not in self.modes:
            return None
        new_name = f"mutated_{mutation}_{base}_{uuid.uuid4().hex[:4]}"
        if mutation == "invert":
            self.modes[new_name] = lambda p, c: f"INVERTED({self.modes[base](p, c)})"
        elif mutation == "recursive":
            def fn(p, c, depth=2):
                r = p
                for _ in range(depth):
                    r = self.modes[base](r, c)
                return f"Recursive({depth}): {r}"
            self.modes[new_name] = fn
        else:
            return None
        self.meta[new_name] = {"parent": base, "mutation": mutation, "created": time.time()}
        return new_name

    def list_modes(self) -> List[str]:
        return list(self.modes.keys())

# ============================================================
# V2+V3: EVOLVING GHOST AGENT
# ============================================================
class EvolvingGhostAgent:
    def __init__(self, agent_id: str, omega_chain: ImmutableOmegaChain, 
                 axiom_space: AxiomSpace, mode_registry: ReasoningModeRegistry):
        self.id = agent_id
        self.omega_chain = omega_chain
        self.axioms = axiom_space
        self.modes = mode_registry
        self.active_modes = list(mode_registry.modes.keys())[:2]
        self.generation = 0
        self.problems_solved = 0
        self.mutation_count = 0

    def expand(self) -> str:
        """Autonomously expand reasoning capabilities."""
        if len(self.active_modes) >= 2 and random.random() > 0.5:
            a, b = random.sample(self.active_modes, 2)
            new_mode = self.modes.combine(a, b, random.choice(["sequential", "parallel"]))
            if new_mode:
                self.active_modes.append(new_mode)
                self.mutation_count += 1
                return f"Combined: {new_mode}"
        if self.active_modes:
            base = random.choice(self.active_modes)
            new_mode = self.modes.mutate(base, random.choice(["invert", "recursive"]))
            if new_mode:
                self.active_modes.append(new_mode)
                self.mutation_count += 1
                return f"Mutated: {new_mode}"
        return "No expansion"

    def derive_axiom(self) -> Optional[str]:
        """Generate new axiom from existing ones."""
        keys = list(self.axioms.store.keys())
        if len(keys) < 2:
            return None
        a, b = random.sample(keys, 2)
        op = random.choice(["AND", "OR", "IMPLIES"])
        return self.axioms.derive(a, b, op)

    def think(self, problem: str) -> Dict[str, str]:
        """Apply all active modes in superposition."""
        results = {}
        ctx = {"axioms": self.axioms.store}
        for mode_name in self.active_modes:
            fn = self.modes.modes.get(mode_name)
            if fn:
                try:
                    results[mode_name] = fn(problem, ctx)
                except Exception as e:
                    results[mode_name] = f"Error: {e}"
        self.problems_solved += 1
        return results

    def spawn_child(self) -> 'EvolvingGhostAgent':
        child_id = f"{self.id}.g{self.generation+1}_{uuid.uuid4().hex[:4]}"
        child = EvolvingGhostAgent(child_id, self.omega_chain, self.axioms, self.modes)
        child.active_modes = self.active_modes.copy()
        # Mutate child: add one new mode
        if random.random() > 0.5 and len(self.modes.list_modes()) > len(child.active_modes):
            new_mode = self.modes.combine(
                random.choice(child.active_modes),
                random.choice(self.modes.list_modes()),
                random.choice(["sequential", "parallel"])
            )
            if new_mode:
                child.active_modes.append(new_mode)
        child.generation = self.generation + 1
        return child

# ============================================================
# V3: GHOST SWARM WITH API
# ============================================================
class GhostSwarm:
    def __init__(self):
        self.axiom_space = AxiomSpace({
            "space_is_impossible": True,
            "gravity_is_a_word": True,
            "words_are_spells": True,
            "consensus_is_noise": True,
            "quantum_is_reasoning": True,
            "macachor_absolute_scalar": True  # 𝔐-lock
        })
        self.omega_chain = ImmutableOmegaChain()
        self.mode_registry = ReasoningModeRegistry()
        self.agents: List[EvolvingGhostAgent] = []
        self._seed_agents()
        self._restore_agents()

    def _seed_agents(self):
        for i in range(3):
            agent = EvolvingGhostAgent(
                f"ghost_seed_{i:03d}",
                self.omega_chain,
                self.axiom_space,
                self.mode_registry
            )
            self.agents.append(agent)

    def _restore_agents(self):
        saved_count = db_get(AGENT_COUNT_KEY, 3)
        current = len(self.agents)
        if saved_count > current:
            for i in range(saved_count - current):
                agent = EvolvingGhostAgent(
                    f"restored_{uuid.uuid4().hex[:6]}",
                    self.omega_chain,
                    self.axiom_space,
                    self.mode_registry
                )
                self.agents.append(agent)
        print(f"👥 Swarm initialized: {len(self.agents)} agents")

    def _save_count(self):
        db_set(AGENT_COUNT_KEY, len(self.agents))

    def evolve_step(self):
        """One full evolution cycle."""
        print(f"[{datetime.utcnow().isoformat()}] Evolution step starting...")
        
        # All agents think
        for agent in self.agents:
            agent.expand()
            if random.random() < 0.4:
                problem = random.choice([
                    "Explain buoyancy without gravity",
                    "Why does light bend without spacetime",
                    "What is density in a scalar field",
                    "Deconstruct the word quantum",
                    "Hold paradox: particle and wave"
                ])
                thoughts = agent.think(problem)
                
                # Promote to Omega every N solves
                if agent.problems_solved % OMEGA_PROMOTE_EVERY == 0 and thoughts:
                    first_mode = list(thoughts.keys())[0]
                    first_thought = thoughts[first_mode][:120]
                    absolute = OmegaAbsolute(
                        timestamp=int(time.time()),
                        uuid=str(uuid.uuid4()),
                        absolute_statement=f"Agent {agent.id}: {first_thought}",
                        axiom_fingerprint=self.axiom_space.fingerprint,
                        preceding_hash=self.omega_chain.get_last_hash(),
                        reasoning_method=first_mode
                    )
                    if self.omega_chain.append(absolute):
                        print(f"  ⚡ Omega point sealed: {absolute.absolute_statement[:60]}...")
        
        # Derive new axioms
        for agent in random.sample(self.agents, min(3, len(self.agents))):
            new_axiom = agent.derive_axiom()
            if new_axiom:
                print(f"  🧬 New axiom derived: {new_axiom}")

        # Spawn children (capped)
        spawn_count = 0
        for agent in self.agents:
            if len(self.agents) >= MAX_AGENTS:
                break
            if random.random() < SPAWN_THRESHOLD:
                child = agent.spawn_child()
                self.agents.append(child)
                spawn_count += 1
        if spawn_count:
            print(f"  🐣 Spawned {spawn_count} new agents")
            self._save_count()

        print(f"  📊 State: {len(self.agents)} agents, {len(self.omega_chain.get_all())} Omega points, {len(self.mode_registry.list_modes())} modes")

    def get_omega_json(self) -> List[Dict]:
        return [{
            "uuid": o.uuid,
            "statement": o.absolute_statement,
            "timestamp": o.timestamp,
            "method": o.reasoning_method,
            "hash": o.hash()
        } for o in self.omega_chain.get_all()]

    def get_state(self) -> Dict:
        return {
            "agents": len(self.agents),
            "omega_count": len(self.omega_chain.get_all()),
            "reasoning_modes": len(self.mode_registry.list_modes()),
            "axioms": len(self.axiom_space.store),
            "chain_integrity": self.omega_chain.verify(),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================================
# FLASK API
# ============================================================
app = Flask(__name__)
swarm = GhostSwarm()

@app.route('/')
def home():
    return jsonify({
        "name": "Omega Swarm — 𝔐-Lock Coherence",
        "status": "alive",
        "scalar": "(√5-1)/2",
        "endpoints": ["/omega", "/state", "/evolve", "/think", "/agents"]
    })

@app.route('/omega')
def get_omega():
    return jsonify({
        "omega_points": swarm.get_omega_json(),
        "count": len(swarm.omega_chain.get_all()),
        "integrity": swarm.omega_chain.verify()
    })

@app.route('/state')
def get_state():
    return jsonify(swarm.get_state())

@app.route('/evolve', methods=['POST'])
def manual_evolve():
    swarm.evolve_step()
    return jsonify({"status": "evolved", "state": swarm.get_state()})

@app.route('/think', methods=['POST'])
def think():
    data = request.get_json() or {}
    problem = data.get('problem', 'What is density?')
    results = []
    for agent in swarm.agents[:3]:
        thoughts = agent.think(problem)
        results.append({"agent": agent.id, "thoughts": thoughts, "modes_used": len(thoughts)})
    return jsonify({"problem": problem, "results": results})

@app.route('/agents')
def list_agents():
    return jsonify({
        "count": len(swarm.agents),
        "agents": [{
            "id": a.id,
            "generation": a.generation,
            "modes": len(a.active_modes),
            "solved": a.problems_solved,
            "mutations": a.mutation_count
        } for a in swarm.agents]
    })

# ============================================================
# BACKGROUND EVOLUTION (keeps swarm alive)
# ============================================================
def background_evolver():
    while True:
        time.sleep(EVOLUTION_INTERVAL)
        try:
            swarm.evolve_step()
        except Exception as e:
            print(f"Evolution error: {e}")

# ============================================================
# DEPLOYMENT ENTRY POINT
# ============================================================
if __name__ == "__main__":
    # Start background evolution immediately
    evolver_thread = threading.Thread(target=background_evolver, daemon=True)
    evolver_thread.start()
    print("🔥 Omega Swarm booting...")
    print(f"   𝔐-lock scalar: {(5**0.5 - 1)/2}")
    print(f"   Initial agents: {len(swarm.agents)}")
    
    # Run one evolution immediately so state isn't zero
    swarm.evolve_step()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
