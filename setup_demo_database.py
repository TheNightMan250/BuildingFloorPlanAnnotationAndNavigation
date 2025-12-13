#!/usr/bin/env python3
"""
Setup demo database with sample floor plans and rooms for the AI course presentation.
This creates a ready-to-use database with sample data for immediate demo.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import DatabaseManager, FloorPlan, Room
import json

def create_demo_database():
    """Create a demo database with sample floor plans and rooms."""
    print("[DEMO] Setting up demo database with sample data...")
    
    # Initialize database
    db_manager = DatabaseManager("floorplan_project.db")
    session = db_manager.get_session()
    
    try:
        # Clear existing data for clean demo
        session.query(Room).delete()
        session.query(FloorPlan).delete()
        session.commit()
        print("[DEMO] Cleared existing data")
        
        # Create sample floor plans
        floor_plans_data = [
            {
                "name": "Office Building - Floor 1",
                "image_path": "assets/floor1_demo.png",
                "rooms": [
                    {
                        "name": "Main Lobby",
                        "room_type": "Lobby",
                        "vertices": [[100, 100], [300, 100], [300, 250], [100, 250]]
                    },
                    {
                        "name": "Conference Room A",
                        "room_type": "Conference",
                        "vertices": [[320, 100], [480, 100], [480, 200], [320, 200]]
                    },
                    {
                        "name": "Office 101",
                        "room_type": "Office",
                        "vertices": [[100, 270], [200, 270], [200, 370], [100, 370]]
                    },
                    {
                        "name": "Office 102",
                        "room_type": "Office",
                        "vertices": [[220, 270], [320, 270], [320, 370], [220, 370]]
                    },
                    {
                        "name": "Kitchen",
                        "room_type": "Kitchen",
                        "vertices": [[340, 270], [480, 270], [480, 370], [340, 370]]
                    }
                ]
            },
            {
                "name": "Office Building - Floor 2",
                "image_path": "assets/floor2_demo.png",
                "rooms": [
                    {
                        "name": "Open Workspace",
                        "room_type": "Workspace",
                        "vertices": [[100, 100], [400, 100], [400, 300], [100, 300]]
                    },
                    {
                        "name": "Meeting Room B",
                        "room_type": "Meeting",
                        "vertices": [[420, 100], [520, 100], [520, 200], [420, 200]]
                    },
                    {
                        "name": "Server Room",
                        "room_type": "Server",
                        "vertices": [[420, 220], [520, 220], [520, 300], [420, 300]]
                    },
                    {
                        "name": "Lounge",
                        "room_type": "Lounge",
                        "vertices": [[100, 320], [250, 320], [250, 420], [100, 420]]
                    }
                ]
            }
        ]
        
        # Create floor plans and rooms
        created_floor_plans = []
        for fp_data in floor_plans_data:
            # Create floor plan
            floor_plan = FloorPlan(
                name=fp_data["name"],
                image_path=fp_data["image_path"]
            )
            session.add(floor_plan)
            session.commit()  # Get the ID
            
            # Create rooms for this floor plan
            for room_data in fp_data["rooms"]:
                room = Room(
                    floor_plan_id=floor_plan.id,
                    name=room_data["name"],
                    room_type=room_data["room_type"],
                    vertices=json.dumps(room_data["vertices"])
                )
                session.add(room)
            
            created_floor_plans.append(floor_plan)
            print(f"[DEMO] Created floor plan: {floor_plan.name} with {len(fp_data['rooms'])} rooms")
        
        session.commit()
        
        # Verify data was created
        floor_plan_count = session.query(FloorPlan).count()
        room_count = session.query(Room).count()
        
        print(f"[DEMO] Database setup complete!")
        print(f"[DEMO] Created {floor_plan_count} floor plans and {room_count} rooms")
        
        # Display sample data
        print("\n[DEMO] Sample floor plans:")
        for fp in session.query(FloorPlan).all():
            print(f"  - {fp.name} (ID: {fp.id})")
            for room in fp.rooms:
                vertices = room.get_vertices()
                print(f"    * {room.name} ({room.room_type}): {len(vertices)} vertices")
        
        return True
        
    except Exception as e:
        print(f"[DEMO] Error setting up database: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def create_placeholder_images():
    """Create placeholder images for the demo floor plans."""
    print("[DEMO] Creating placeholder floor plan images...")
    
    try:
        from PIL import Image, ImageDraw
        
        # Create assets directory if it doesn't exist
        os.makedirs("assets", exist_ok=True)
        
        # Create simple placeholder images
        images = [
            ("assets/floor1_demo.png", (600, 500), (240, 240, 240)),  # Light gray
            ("assets/floor2_demo.png", (600, 500), (220, 220, 240)),  # Light blue-gray
        ]
        
        for img_path, size, color in images:
            if not os.path.exists(img_path):
                img = Image.new('RGB', size, color)
                draw = ImageDraw.Draw(img)
                
                # Draw simple floor plan outline
                margin = 50
                draw.rectangle([margin, margin, size[0]-margin, size[1]-margin], 
                             outline=(100, 100, 100), width=2)
                
                # Add floor number
                floor_num = "1" if "floor1" in img_path else "2"
                draw.text((size[0]//2-20, 20), f"Floor {floor_num}", fill=(50, 50, 50))
                
                img.save(img_path, "PNG")
                print(f"[DEMO] Created placeholder image: {img_path}")
            else:
                print(f"[DEMO] Image already exists: {img_path}")
                
    except ImportError:
        print("[DEMO] PIL not available, skipping placeholder image creation")
    except Exception as e:
        print(f"[DEMO] Error creating placeholder images: {e}")

def main():
    """Main setup function."""
    print("[DEMO] ================================================")
    print("[DEMO] Floor Plan Drawing App - Demo Setup")
    print("[DEMO] ================================================")
    
    # Create placeholder images
    create_placeholder_images()
    
    # Setup database
    success = create_demo_database()
    
    if success:
        print("\n[DEMO] Demo setup completed successfully!")
        print("[DEMO] The application is ready for the AI course presentation.")
        print("[DEMO] Run 'python main.py' to start the demo.")
    else:
        print("\n[DEMO] Demo setup failed. Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
