# We Built a Warehouse That Learns. Here's Why That Was Hard.

India processes over 10 million e-commerce orders every single day.
Behind every delivery is a warehouse — and inside that warehouse,
robots are making split-second decisions that most people never 
think about.

Which package is most urgent? Which path avoids a collision?
When does a robot stop to recharge before it dies mid-task?

We thought we could simulate all of that. We were wrong about how
hard it would be. And that's exactly what made this interesting.

---

## The Problem Isn't Movement. It's Judgment.

When we started building this, we made the classic mistake — we
focused on getting robots to move. BFS pathfinding, obstacle grids,
collision detection. That all came together quickly.

But then we ran the simulation and watched something frustrating 
happen.

The robots were moving perfectly. And still failing.

A HIGH priority task would expire while a robot was busy finishing
a LOW priority one nearby. Two robots would race toward the same
pickup point. One would run out of battery three steps from the
charging station.

The movement was fine. The judgment was broken.

That's when we understood the real problem: this isn't a navigation
challenge. It's a decision-making under pressure challenge. And that
required a completely different solution.

---

## Building the Environment

We designed a 5×5 warehouse grid — deliberately compact, because
tight spaces force harder decisions. Every cell matters. Every step
has a cost.

The environment has:
- 2 autonomous robots operating simultaneously
- Tasks with HIGH / NORMAL / LOW priorities
- Real-time deadline countdowns that penalize failure hard (-25)
- Charging stations robots must find before battery hits zero
- Static obstacles representing warehouse shelves
- Emergency task injection — sudden urgent deliveries mid-simulation
- Peak load simulation — stress testing under festival-level demand

The reward signal was designed to punish bad judgment, not just
bad movement:

| Event | Reward |
|---|---|
| All tasks complete | +150 |
| Task delivered | +60 |
| Item picked up | +15 |
| Recharged / HIGH priority bonus | +10 |
| Deadline missed | -25 |
| Collision | -20 |
| Obstacle hit | -10 |
| Movement cost | -1 |

This created an environment where a "smart" rule-based robot could
still fail — because rules don't handle pressure. Learning does.

---

## The PyTorch Brain

We replaced our initial heuristic logic with a proper Deep Q-Network
built in PyTorch.

3-layer MLP. Input: [pending tasks, max priority level, min deadline
remaining]. Output: which strategy the fleet should run —
Priority-First, Nearest-First, or Deadline-First.

Adam optimizer. MSE loss. Experience replay buffer. Epsilon-greedy
exploration. Trained across 150 episodes using HuggingFace TRL
for experiment configuration and tracking.

The key insight was treating strategy selection as the RL problem,
not low-level movement. The DQN acts as a high-level commander —
it reads the warehouse state and decides the operational mode.
BFS handles the actual navigation underneath.

This two-level architecture (neural commander + deterministic
pathfinder) is actually how real warehouse systems like Amazon
Robotics think about the problem.

The trained weights are saved as model.pth and loaded at runtime
— the dashboard shows "PYTORCH NEURAL POLICY ENGINE: ACTIVE"
every time the DQN is driving decisions.

---

## What the Training Showed

The results were cleaner than we expected.

Random baseline agent: ~400 average reward per episode.
PyTorch DQN after 150 episodes: ~950 average reward.

That's a +137% improvement — and the curve tells a story. Early
episodes are chaotic. The agent tries random strategies, fails,
gets penalized. Around episode 40-50, it starts learning that
deadline pressure beats proximity. By episode 100, it consistently
switches to Deadline-First mode under stress.

Final evaluation scores: 0.97 across Easy, Medium, and Hard
difficulty. The agent doesn't just perform well on easy cases —
it maintains performance when deadlines tighten and tasks pile up.

---

## Making It Observable — The Reward Feed

One thing we wanted judges and users to actually see was the
reward signal in real time — not just as a number, but as a
live feed of every decision the agent makes.

We built a Reward Feed into the dashboard:

+150  All tasks complete!
+60   Task delivered
+15   Item picked up
-25   Deadline missed
-20   Collision
-10   Obstacle hit
-1    Movement

Every step the agent takes shows up as a colored entry — green
for good decisions, red for penalties. You can watch the agent
learn in real time, see when it makes mistakes, and understand
exactly why it gets the reward it gets.

![Dashboard Preview](images/dashboard_preview.png)
*Live reward feed showing agent decisions in real time*

---

## Peak Load — Stress Testing the System

![Peak Load Grid](images/performance_metrics.png)
*Tactical Operations Grid under festival-level peak demand*

Warehouses don't fail during normal hours. They fail during
Black Friday. Festival sales. Flash delivery days.

We built Peak Load Simulation to stress test exactly this — 
injecting 5–8 urgent tasks simultaneously with tight deadlines.
The grid fills up. Robots must reorganize instantly.

This is where the DQN's strategy switching shows its value:
under peak load, it consistently shifts to Deadline-First mode
and saves tasks that a rule-based system would miss.

---

## System Architecture

![Architecture Diagram](images/architecture_diagram.png)

The full stack:
- Streamlit dashboard with live reward feed and robot telemetry
- FastAPI backend managing all simulation state
- PyTorch DQN neural policy engine (model.pth)
- HuggingFace TRL for training configuration
- Docker containerized deployment
- HuggingFace Spaces for live hosting

---

## What We Learned

The hardest part wasn't the code. It was designing a reward
function that couldn't be gamed.

Early versions produced agents that hovered near charging stations
for easy recharge bonuses while ignoring deliveries. Classic
reward hacking.

We fixed it by making the completion reward (+60) dwarf everything
else, and making deadline failures expensive enough that ignoring
tasks was never the optimal strategy.

Good RL environments aren't just simulations. They're arguments —
about what behavior you actually want, expressed in numbers.

---

## Try It

Live Dashboard:
https://huggingface.co/spaces/kottakur/warehouse-priority-env

Training Notebook (HuggingFace TRL + PyTorch DQN):
https://colab.research.google.com/drive/1yAKAoVT_yDQAVVhbNvQhS7oqloQkm9nI#scrollTo=V7SB1zRTgyY7

GitHub:
https://github.com/Narendra02053/meta_hack

Built for the Meta × PyTorch × HuggingFace OpenEnv Hackathon.
By Narendra — AMC Engineering College, Bengaluru.
