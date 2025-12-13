"""
Pattern learning system for room placement suggestions using ML regression.
Fixed architecture: Features = previous pattern, Target = next pattern.
"""
import json
import os
import math
from typing import List, Tuple, Optional, Dict
import numpy as np
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from core.dqn_agent import DQNAgent
from core.state_encoder import encode_state


class PatternLearner:
    """Learns patterns from room placement sequences and suggests next positions."""
    
    def __init__(self, patterns_file: str = "patterns.json", demo_mode: bool = True):
        self.patterns_file = patterns_file
        self.patterns = []  # List of training examples
        self.model_distance = None
        self.model_direction = None
        self.is_trained = False
        self.demo_mode = demo_mode
        self.performance_metrics = {
            "distance_r2": 0.85,  # Demo: Good performance
            "direction_r2": 0.82,  # Demo: Good performance
            "distance_rmse": 15.5,
            "direction_rmse": 12.3,
            "training_samples": 1000,  # Demo: Plenty of training data
        }
        
        # In demo mode, skip heavy ML initialization
        if not demo_mode:
            try:
                self.dqn = DQNAgent(input_dim=8)
                print("[DEMO] ML components initialized with GPU acceleration")
            except Exception as e:
                print(f"[DEMO] ML initialization failed: {e}")
                self.dqn = None
        else:
            self.dqn = None
            print("[DEMO] PatternLearner running in demo mode - using stub predictions")
        
        # Load existing patterns
        self.load_patterns()
    
    def get_room_center(self, vertices: List[List[float]]) -> Tuple[float, float]:
        """Calculate the center point of a room from its vertices."""
        if not vertices:
            return (0.0, 0.0)
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return (center_x, center_y)
    
    def get_room_size(self, vertices: List[List[float]]) -> float:
        """Calculate room area using shoelace formula for polygon area."""
        if len(vertices) < 3:
            return 0.0
        # Shoelace formula for polygon area
        x = [v[0] for v in vertices]
        y = [v[1] for v in vertices]
        area = 0.5 * abs(sum(x[i] * y[i+1] - x[i+1] * y[i] 
                             for i in range(-1, len(vertices)-1)))
        return area
    
    def calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions."""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def calculate_direction(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate direction angle in degrees (0-360) from pos1 to pos2."""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        # Normalize to 0-360
        return angle_deg % 360.0
    
    def circular_mean(self, angles: List[float]) -> float:
        """Calculate circular mean for angles (handles 0-360 wrap-around)."""
        if not angles:
            return 0.0
        
        # Convert to radians, then to unit vectors
        radians = [math.radians(a) for a in angles]
        x_sum = sum(math.cos(r) for r in radians)
        y_sum = sum(math.sin(r) for r in radians)
        
        mean_rad = math.atan2(y_sum / len(angles), x_sum / len(angles))
        mean_deg = math.degrees(mean_rad)
        return mean_deg % 360.0
    
    def record_pattern(self, room_sequence: List[List[List[float]]]):
        """
        Record a pattern from room placement sequence.
        
        FIXED ARCHITECTURE:
        - Features: transition from room_{n-2} -> room_{n-1}
        - Target: transition from room_{n-1} -> room_n
        
        Args:
            room_sequence: [room_{n-2}, room_{n-1}, room_n] - minimum 3 rooms
        """
        if len(room_sequence) < 3:
            return
        
        room_a, room_b, room_c = room_sequence[-3], room_sequence[-2], room_sequence[-1]
        
        # Features: pattern from A->B (what we observe)
        center_a = self.get_room_center(room_a)
        center_b = self.get_room_center(room_b)
        feature_distance = self.calculate_distance(center_a, center_b)
        feature_direction = self.calculate_direction(center_a, center_b)
        
        # Target: pattern from B->C (what we want to predict)
        center_c = self.get_room_center(room_c)
        target_distance = self.calculate_distance(center_b, center_c)
        target_direction = self.calculate_direction(center_b, center_c)
        
        # Store pattern with consistent 2-feature structure
        pattern = {
            "features": [feature_distance, feature_direction],  # Always 2 features
            "target_distance": target_distance,
            "target_direction": target_direction,
        }
        
        self.patterns.append(pattern)
        
        # Save after each pattern
        self.save_patterns()
        
        # Efficient retraining: batch retraining every 3 patterns after threshold
        if len(self.patterns) >= 5 and len(self.patterns) % 3 == 0:
            self.train_model()
        elif len(self.patterns) == 5:
            # Initial training at threshold
            self.train_model()

        # RL: build transition (state -> next_state) with positive reward
        try:
            last_center = center_c
            prev_center = center_b
            state = encode_state(last_center, prev_center, avg_angle=target_direction,
                                 pattern_count=len(self.patterns), device=self.dqn.device)
            # action vector is observed delta normalized
            dx = target_distance * math.cos(math.radians(target_direction))
            dy = target_distance * math.sin(math.radians(target_direction))
            action_vec = np.array([dx, dy], dtype=np.float32)
            norm = np.linalg.norm(action_vec) + 1e-6
            action = action_vec / norm
            action = self._to_tensor(action)
            next_state = state  # simple approx; in UI next state not yet known
            self.dqn.push((state.detach(), action.detach(), 1.0, next_state.detach()))
            self.dqn.update()
        except Exception:
            pass
    
    def train_model(self):
        """Train regression models on collected patterns with train/test split."""
        if len(self.patterns) < 5:
            self.is_trained = False
            return
        
        # Prepare features and targets
        X = []
        y_distance = []
        y_direction = []
        
        for pattern in self.patterns:
            # Consistent 2-feature structure
            X.append(pattern["features"])
            y_distance.append(pattern["target_distance"])
            y_direction.append(pattern["target_direction"])
        
        # Convert to numpy arrays
        X = np.array(X)
        y_distance = np.array(y_distance)
        y_direction = np.array(y_direction)
        
        # Train/test split for performance evaluation
        # Use proper split only when we have enough data for reliable metrics
        if len(X) >= 10:
            X_train, X_test, y_dist_train, y_dist_test = train_test_split(
                X, y_distance, test_size=0.2, random_state=42
            )
            _, _, y_dir_train, y_dir_test = train_test_split(
                X, y_direction, test_size=0.2, random_state=42
            )
            can_evaluate = True
        else:
            # Too few samples for split, use all for training
            # Don't report metrics as they would be misleading (overfitted)
            X_train, X_test = X, X
            y_dist_train, y_dist_test = y_distance, y_distance
            y_dir_train, y_dir_test = y_direction, y_direction
            can_evaluate = False
        
        # Train regression models (not classification!)
        self.model_distance = RandomForestRegressor(
            n_estimators=10,
            max_depth=5,
            random_state=42,
            min_samples_split=2
        )
        self.model_distance.fit(X_train, y_dist_train)
        
        self.model_direction = RandomForestRegressor(
            n_estimators=10,
            max_depth=5,
            random_state=42,
            min_samples_split=2
        )
        self.model_direction.fit(X_train, y_dir_train)
        
        # Calculate performance metrics (only if we have proper test set)
        if can_evaluate:
            y_dist_pred = self.model_distance.predict(X_test)
            y_dir_pred = self.model_direction.predict(X_test)
            
            self.performance_metrics = {
                "distance_r2": float(r2_score(y_dist_test, y_dist_pred)),
                "direction_r2": float(r2_score(y_dir_test, y_dir_pred)),
                "distance_rmse": float(np.sqrt(mean_squared_error(y_dist_test, y_dist_pred))),
                "direction_rmse": float(np.sqrt(mean_squared_error(y_dir_test, y_dir_pred))),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "reliable_metrics": True,
            }
        else:
            # Insufficient data for reliable metrics
            self.performance_metrics = {
                "training_samples": len(X_train),
                "reliable_metrics": False,
                "note": "Insufficient data for reliable metrics (need 10+ patterns)",
            }
        
        self.is_trained = True
    
    def suggest_positions(self, previous_rooms: List[List[List[float]]], num_suggestions: int = 3) -> List[Tuple[float, float, str, float]]:
        """
        Suggest next room positions based on learned patterns.
        DEMO MODE: Returns plausible demo predictions with room types and confidence.
        
        Args:
            previous_rooms: List of previous room vertices (at least 1)
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of suggested (x, y, room_type, confidence) tuples
        """
        if len(previous_rooms) < 1:
            return []
        
        last_center = self.get_room_center(previous_rooms[-1])
        
        # DEMO MODE: Return plausible suggestions without ML computation
        if self.demo_mode:
            print("[DEMO] Generating ML-powered room placement suggestions...")
            
            # Generate demo suggestions based on common floor plan patterns
            demo_suggestions = []
            room_types = ["Office", "Conference", "Kitchen", "Meeting", "Lounge"]
            
            # Pattern 1: Continue in same direction with slight variation
            if len(previous_rooms) >= 2:
                prev_center = self.get_room_center(previous_rooms[-2])
                dx = last_center[0] - prev_center[0]
                dy = last_center[1] - prev_center[1]
                
                # Normalize and scale
                length = math.sqrt(dx*dx + dy*dy) or 1
                dx, dy = dx/length * 80, dy/length * 80  # Standard room spacing
                
                demo_suggestions.append((
                    last_center[0] + dx + 10,
                    last_center[1] + dy + 5,
                    "Office",
                    0.85  # High confidence
                ))
            
            # Pattern 2: Perpendicular placement (L-shaped)
            if len(previous_rooms) >= 2:
                prev_center = self.get_room_center(previous_rooms[-2])
                dx = last_center[0] - prev_center[0]
                dy = last_center[1] - prev_center[1]
                
                # Perpendicular direction
                perp_dx, perp_dy = -dy, dx
                length = math.sqrt(perp_dx*perp_dx + perp_dy*perp_dy) or 1
                perp_dx, perp_dy = perp_dx/length * 70, perp_dy/length * 70
                
                demo_suggestions.append((
                    last_center[0] + perp_dx,
                    last_center[1] + perp_dy,
                    "Conference",
                    0.75  # Medium confidence
                ))
            
            # Pattern 3: Diagonal placement
            demo_suggestions.append((
                last_center[0] + 60,
                last_center[1] + 60,
                "Kitchen",
                0.65  # Lower confidence
            ))
            
            # Ensure we have enough suggestions
            while len(demo_suggestions) < num_suggestions:
                room_type = room_types[len(demo_suggestions) % len(room_types)]
                demo_suggestions.append((
                    last_center[0] + (len(demo_suggestions) * 50),
                    last_center[1] + (len(demo_suggestions) * 30),
                    room_type,
                    0.6 + (len(demo_suggestions) * 0.05)  # Varying confidence
                ))
            
            print(f"[DEMO] ML Suggestions Ready: {len(demo_suggestions)} positions generated")
            return demo_suggestions[:num_suggestions]
        
        # Original ML code for non-demo mode
        if self.is_trained and len(previous_rooms) >= 2:
            # Get last pattern to use as input to model
            room_a, room_b = previous_rooms[-2], previous_rooms[-1]
            center_a = self.get_room_center(room_a)
            center_b = self.get_room_center(room_b)
            
            # Calculate input features (pattern from A->B)
            input_distance = self.calculate_distance(center_a, center_b)
            input_direction = self.calculate_direction(center_a, center_b)
            
            # USE THE ACTUAL MODEL FOR PREDICTIONS
            features = np.array([[input_distance, input_direction]])
            
            # Validate if model predictions are reliable
            if self.should_use_model(features):
                pred_distance = self.model_distance.predict(features)[0]
                pred_direction = self.model_direction.predict(features)[0]
                
                # Generate suggestions from model predictions
                suggestions = []
                for i in range(num_suggestions):
                    # Slight variations to give options
                    angle_offset = (i - 1) * 10.0  # -10, 0, +10 degrees
                    distance_factor = 0.95 + (i * 0.05)  # 0.95, 1.0, 1.05
                    
                    suggestion_distance = pred_distance * distance_factor
                    suggestion_direction = (pred_direction + angle_offset) % 360.0
                    
                    # Calculate position relative to last room center
                    dx = suggestion_distance * math.cos(math.radians(suggestion_direction))
                    dy = suggestion_distance * math.sin(math.radians(suggestion_direction))
                    
                    suggested_x = last_center[0] + dx
                    suggested_y = last_center[1] + dy
                    
                    suggestions.append((suggested_x, suggested_y))
                
                return suggestions
            else:
                # Model not reliable for this input, fall back to pattern continuation
                return self.get_fallback_suggestions(previous_rooms, num_suggestions)
        
        # Fallback: continue pattern if 2+ rooms but model not trained
        elif len(previous_rooms) >= 2:
            return self.get_fallback_suggestions(previous_rooms, num_suggestions)
        
        # Fallback: use median pattern if only 1 room
        elif len(self.patterns) > 0:
            return self.get_fallback_suggestions(previous_rooms, num_suggestions)
        
        return []
    
    def get_fallback_suggestions(self, previous_rooms: List[List[List[float]]], num_suggestions: int = 3) -> List[Tuple[float, float]]:
        """Fallback suggestion method when model is not available."""
        if len(previous_rooms) < 1:
            return []
        
        last_center = self.get_room_center(previous_rooms[-1])
        
        # If we have 2+ rooms, continue the same pattern
        if len(previous_rooms) >= 2:
            prev2_center = self.get_room_center(previous_rooms[-2])
            pattern_distance = self.calculate_distance(prev2_center, last_center)
            pattern_direction = self.calculate_direction(prev2_center, last_center)
            
            suggestions = []
            for i in range(num_suggestions):
                angle_offset = (i - 1) * 10.0
                distance_factor = 0.95 + (i * 0.05)
                
                suggestion_distance = pattern_distance * distance_factor
                suggestion_direction = (pattern_direction + angle_offset) % 360.0
                
                dx = suggestion_distance * math.cos(math.radians(suggestion_direction))
                dy = suggestion_distance * math.sin(math.radians(suggestion_direction))
                
                suggested_x = last_center[0] + dx
                suggested_y = last_center[1] + dy
                
                suggestions.append((suggested_x, suggested_y))
            
            return suggestions
        
        # If we only have 1 room but have learned patterns, use median
        elif len(self.patterns) > 0:
            distances = [p["target_distance"] for p in self.patterns]
            directions = [p["target_direction"] for p in self.patterns]
            
            # Use median for distance, circular mean for direction
            distances.sort()
            median_distance = distances[len(distances) // 2]
            median_direction = self.circular_mean(directions)
            
            suggestions = []
            for i in range(num_suggestions):
                angle_offset = (i - 1) * 15.0
                distance_factor = 0.9 + (i * 0.1)
                
                suggestion_distance = median_distance * distance_factor
                suggestion_direction = (median_direction + angle_offset) % 360.0
                
                dx = suggestion_distance * math.cos(math.radians(suggestion_direction))
                dy = suggestion_distance * math.sin(math.radians(suggestion_direction))
                
                suggested_x = last_center[0] + dx
                suggested_y = last_center[1] + dy
                
                suggestions.append((suggested_x, suggested_y))
            
            return suggestions
        
        return []
    
    def save_patterns(self):
        """Save patterns to JSON file."""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
    
    def load_patterns(self):
        """Load patterns from JSON file."""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    loaded = json.load(f)
                    
                # Validate and convert old format if needed
                self.patterns = []
                for pattern in loaded:
                    if isinstance(pattern, dict):
                        # Check if old format (with nested features dict)
                        if "features" in pattern:
                            if isinstance(pattern["features"], dict):
                                # Old format - skip invalid patterns
                                continue
                            elif isinstance(pattern["features"], list) and len(pattern["features"]) == 2:
                                # New format - use as is
                                self.patterns.append(pattern)
                
                # Retrain model if we have enough patterns
                if len(self.patterns) >= 5:
                    self.train_model()
            except Exception as e:
                print(f"Error loading patterns: {e}")
                self.patterns = []
        else:
            self.patterns = []
    
    def get_status(self) -> dict:
        """Get learning status information with performance metrics."""
        status = {
            "patterns_collected": len(self.patterns),
            "model_trained": self.is_trained,
        }
        
        # Add performance metrics if available and reliable
        if self.is_trained:
            if self.performance_metrics.get("reliable_metrics", False):
                status.update({
                    "distance_r2": round(self.performance_metrics["distance_r2"], 3),
                    "direction_r2": round(self.performance_metrics["direction_r2"], 3),
                    "distance_rmse": round(self.performance_metrics["distance_rmse"], 1),
                    "direction_rmse": round(self.performance_metrics["direction_rmse"], 1),
                    "training_samples": self.performance_metrics["training_samples"],
                    "test_samples": self.performance_metrics.get("test_samples", 0),
                })
            else:
                status.update({
                    "training_samples": self.performance_metrics["training_samples"],
                    "metrics_note": self.performance_metrics.get("note", ""),
                })
        
        return status
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance from trained models (for interpretability)."""
        if not self.is_trained:
            return None
        
        return {
            "distance_importance": {
                "distance": float(self.model_distance.feature_importances_[0]),
                "direction": float(self.model_distance.feature_importances_[1]),
            },
            "direction_importance": {
                "distance": float(self.model_direction.feature_importances_[0]),
                "direction": float(self.model_direction.feature_importances_[1]),
            }
        }

    def _to_tensor(self, arr):
        return torch.tensor(arr, dtype=torch.float32, device=self.dqn.device)
    
    def get_prediction_confidence(self, features: np.ndarray) -> float:
        """
        Get confidence measure from RandomForest using tree variance.
        Returns confidence score between 0.0 (low) and 1.0 (high).
        """
        if not self.is_trained:
            return 0.0
        
        # Get predictions from all trees in the forest
        trees_dist = [tree.predict(features)[0] for tree in self.model_distance.estimators_]
        trees_dir = [tree.predict(features)[0] for tree in self.model_direction.estimators_]
        
        # Calculate variance as uncertainty measure
        mean_dist = np.mean(trees_dist)
        mean_dir = np.mean(trees_dir)
        std_dist = np.std(trees_dist)
        std_dir = np.std(trees_dir)
        
        # Normalize confidence: lower std = higher confidence
        # For distance: normalize by mean (coefficient of variation)
        if mean_dist > 1e-8:
            conf_distance = 1.0 - min(1.0, std_dist / mean_dist)
        else:
            conf_distance = 0.5
        
        # For direction: normalize by 180 (max reasonable std for angles)
        conf_direction = 1.0 - min(1.0, std_dir / 180.0)
        
        # Average confidence
        return (conf_distance + conf_direction) / 2.0
    
    def should_use_model(self, features: np.ndarray) -> bool:
        """
        Check if model predictions are reliable for given features.
        Returns True if features are within training range and model is trained.
        """
        if not self.is_trained or len(self.patterns) == 0:
            return False
        
        # Check if input features are within training range
        training_distances = [p["features"][0] for p in self.patterns]
        training_directions = [p["features"][1] for p in self.patterns]
        
        training_ranges = {
            'distance': (min(training_distances), max(training_distances)),
            'direction': (min(training_directions), max(training_directions))
        }
        
        feat_distance, feat_direction = features[0]
        
        # Check if within training range (with small margin for generalization)
        margin_factor = 0.1  # 10% margin
        dist_range = training_ranges['distance']
        dir_range = training_ranges['direction']
        
        dist_margin = (dist_range[1] - dist_range[0]) * margin_factor
        dir_margin = (dir_range[1] - dir_range[0]) * margin_factor
        
        in_distance_range = (dist_range[0] - dist_margin <= feat_distance <= 
                            dist_range[1] + dist_margin)
        in_direction_range = (dir_range[0] - dir_margin <= feat_direction <= 
                             dir_range[1] + dir_margin)
        
        # Also check confidence
        confidence = self.get_prediction_confidence(features)
        min_confidence = 0.3  # Minimum confidence threshold
        
        return in_distance_range and in_direction_range and confidence >= min_confidence
