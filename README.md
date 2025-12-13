# Floor Plan Drawing Application

A comprehensive floor plan annotation tool with intelligent ML-assisted room and pathway placement suggestions.

## Architecture Overview

This application follows a strict layered architecture with clear separation of concerns, implementing SOLID principles and multiple design patterns.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                               │
│  ┌──────────────┐  ┌─────────────────────────────────────┐  │
│  │ UserInterface│  │ Commands (Command Pattern)          │  │
│  │ MainWindow   │  │ - LoginCommand                      │  │
│  │ CanvasWidget │  │ - SearchCommand                     │  │
│  │ Properties   │  │ - PathfindCommand                   │  │
│  └──────────────┘  │ - UpdateRoomStatusCommand           │  │
│                     └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Controller Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │AuthController│  │MapController │  │SearchController│    │
│  │              │  │(Facade)      │  │               │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Users        │  │ Buildings    │  │ Maps          │     │
│  │ - User       │  │ - Building   │  │ - MapManager  │     │
│  │ - AdminUser  │  │ - Floor      │  │ - Workflows   │     │
│  │ - GuestUser  │  │ - Room       │  │   (Template)  │     │
│  │ - MapCreator │  │ - Builders   │  │               │     │
│  │ - Factory    │  │   (Builder)  │  │               │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Pathfinder   │  │ SearchEngine │                        │
│  │ (Strategy)   │  │              │                        │
│  │ - Dijkstra   │  └──────────────┘                        │
│  │ - A*         │                                            │
│  └──────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Repositories │  │  Database    │  │  Adapters    │     │
│  │ - UserRepo   │  │  - SQLite    │  │  - PNG       │     │
│  │ - RoomRepo   │  │  - Models    │  │  - JPG       │     │
│  │ - MapRepo    │  │              │  │  - SVG       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Design Patterns Implemented

### Creational Patterns

#### Factory Method Pattern
- **Location**: `domain/users/user_factory.py`
- **Purpose**: Creates user instances (AdminUser, GuestUser, MapCreator) based on type
- **Usage**: `UserFactory.create_user(user_type, user_id, username, email)`

#### Builder Pattern
- **Location**: `domain/buildings/builders/`
- **Purpose**: Constructs complex Building/Floor/Room hierarchies step-by-step
- **Classes**: `BuildingBuilder`, `FloorBuilder`, `RoomBuilder`

### Structural Patterns

#### Facade Pattern
- **Location**: `controllers/map_controller.py`
- **Purpose**: Simplifies complex map operations into simple interface
- **Methods**: `loadMap()`, `getPath()`, `submitMap()`, `approveMap()`

#### Adapter Pattern
- **Location**: `adapters/`
- **Purpose**: Converts different image formats (PNG, JPG, SVG) to unified interface
- **Classes**: `PNGAdapter`, `JPGAdapter`, `SVGAdapter`

### Behavioral Patterns

#### Command Pattern
- **Location**: `ui/commands/`
- **Purpose**: Encapsulates UI actions as objects for undo/redo support
- **Commands**: `LoginCommand`, `SearchCommand`, `PathfindCommand`, `UpdateRoomStatusCommand`, `SelectStartRoomCommand`, `SelectEndRoomCommand`, `NavigateCommand`

#### Template Method Pattern
- **Location**: `domain/maps/workflows/`
- **Purpose**: Defines map approval workflow skeleton with customizable steps
- **Classes**: `MapApprovalWorkflow` (base), `SimpleMapWorkflow`, `ComplexMapWorkflow`

#### Strategy Pattern
- **Location**: `domain/pathfinder/`
- **Purpose**: Allows swapping pathfinding algorithms (Dijkstra, A*) without code changes
- **Interface**: `Pathfinder` abstract class

## SOLID Principles

### Single Responsibility Principle (SRP)
- Each class has one clear responsibility:
  - `MapController`: Map operations
  - `SearchEngine`: Search functionality
  - `Pathfinder`: Pathfinding algorithms
  - `UserRepository`: User data access

### Open/Closed Principle (OCP)
- Pathfinding algorithms can be extended without modifying existing code
- New workflow types can be added by extending `MapApprovalWorkflow`
- New user types can be added via `UserFactory`

### Liskov Substitution Principle (LSP)
- All user subclasses (AdminUser, GuestUser, MapCreator) can be used wherever `User` is expected
- All pathfinder implementations can be swapped without breaking functionality

### Interface Segregation Principle (ISP)
- Repository interfaces are focused and specific (`IRoomRepository`, `IMapRepository`, `IUserRepository`)
- No client is forced to depend on methods it doesn't use

### Dependency Inversion Principle (DIP)
- Controllers depend on repository interfaces, not concrete implementations
- High-level modules (controllers) don't depend on low-level modules (repositories)

## Layer Responsibilities

### UI Layer (`ui/`)
- Handles user interaction and display
- Delegates business logic to controllers
- Uses Command pattern for actions

### Controller Layer (`controllers/`)
- Acts as facade to domain layer
- Coordinates between UI and domain
- No business logic, only orchestration

### Domain Layer (`domain/`)
- Contains business logic and entities
- No dependencies on UI or data layers
- Pure business rules and algorithms

### Data Layer (`data/`)
- Handles persistence
- Implements repository interfaces
- Database access and data mapping

## Machine Learning Components

The application includes ML-assisted suggestions:

- **Pattern Learner**: Learns from room placement sequences using RandomForest regression
- **Neural Q-Learning**: DQN agent for reinforcement learning
- **State Encoder**: Converts room/pattern data to numeric tensors
- **Auto-Complete**: Combines geometric, pattern, and neural predictions

All ML components run locally with PyTorch, supporting GPU acceleration when available.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Project Structure

```
project/
├── ui/                    # UI Layer
│   ├── user_interface.py
│   ├── main_window.py
│   └── commands/          # Command Pattern
│       ├── select_start_room_command.py
│       ├── select_end_room_command.py
│       └── navigate_command.py
│
├── controllers/           # Controller Layer (Facade)
│   ├── auth_controller.py
│   ├── map_controller.py
│   ├── search_controller.py
│   └── navigation_controller.py
│
├── domain/               # Domain Layer
│   ├── users/            # Factory Method
│   ├── buildings/        # Builder Pattern
│   │   ├── building.py
│   │   ├── floor.py
│   │   ├── room.py
│   │   └── stair.py     # Stair entity for multi-floor navigation
│   ├── maps/             # Template Method
│   ├── pathfinder/       # Strategy Pattern
│   │   ├── building_graph.py  # Multi-floor graph
│   │   └── algorithms/
│   └── search_engine.py
│
├── data/                 # Data Layer
│   ├── repositories/     # Repository Pattern
│   │   └── stair_repo.py
│   └── database/
│
├── adapters/             # Adapter Pattern
│
├── core/                 # ML/RL Components
│   ├── neural_q.py
│   ├── dqn_agent.py
│   ├── state_encoder.py
│   └── rl.py
│
└── main.py               # Bootstrap
```

## Key Features

- **Strict Layering**: UI → Controllers → Domain → Repositories → Data
- **Design Patterns**: Factory, Builder, Facade, Adapter, Command, Template Method, Strategy
- **SOLID Principles**: All five principles enforced
- **ML Integration**: Local neural networks with GPU support
- **Multi-Floor Navigation**: Cross-floor pathfinding via stairs
- **Navigation Mode**: Read-only mode for end-users to navigate between rooms
- **Extensible**: Easy to add new algorithms, workflows, user types

## Navigation Mode

The application supports two distinct usage modes:

### Annotator Mode (Default)
- Create and edit floor plans
- Draw rooms and pathways
- Manage multiple floors
- Full editing capabilities

### Navigation Mode
- Read-only access to floor plans
- Search for rooms across all floors
- Select start and end rooms
- Get navigation paths between rooms
- Multi-floor pathfinding via stairs

### Multi-Floor Pathfinding

The system models vertical traversal using **Stairs**:

- **Stair Entity**: Represents a connection between two floors
  - `from_floor_id`: Source floor
  - `to_floor_id`: Destination floor
  - `position`: (x, y) coordinates on the floor

- **BuildingGraph**: Unified graph abstraction
  - Combines all floors into a single navigable graph
  - Connects floors via stairs
  - Provides transparent cross-floor pathfinding

- **Pathfinding Algorithms**: Both Dijkstra and A* support multi-floor navigation
  - Stairs are treated as edges with configurable cost (default: 10.0)
  - Algorithms automatically handle floor transitions
  - Paths include floor information: `(floor_id, x, y)`

### Navigation Flow

1. User selects "Navigation Mode"
2. User searches for or clicks a room to set as start
3. User searches for or clicks a room to set as end
4. System computes path using `BuildingGraph`
5. Path is displayed floor-by-floor with stair transitions highlighted

## Testing

The architecture supports easy testing through:
- Dependency injection in constructors
- Interface-based dependencies
- Clear separation of concerns

## Future Enhancements

- Add more pathfinding algorithms
- Implement undo/redo using Command pattern
- Add more image format adapters
- Enhance ML model with more features
"# BuildingFloorPlanAnnotationAndNavigation" 
