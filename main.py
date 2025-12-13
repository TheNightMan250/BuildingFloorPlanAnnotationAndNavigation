import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from models import DatabaseManager
from data.repositories.map_repo import MapRepository
from data.repositories.room_repo import RoomRepository
from data.repositories.user_repo import UserRepository
from domain.users.user_manager import UserManager
from domain.search_engine import SearchEngine
from domain.pathfinder.pathfinder import Pathfinder
from domain.pathfinder.algorithms.dijkstra import DijkstraPathfinder
from domain.maps.workflows.simple_map_workflow import SimpleMapWorkflow
from controllers.auth_controller import AuthController
from controllers.map_controller import MapController
from controllers.search_controller import SearchController
from controllers.navigation_controller import NavigationController
from data.repositories.stair_repo import StairRepository
from data.repositories.pathway_repo import PathwayRepository
from ui.user_interface import UserInterface
from ui.main_window import MainWindow

# Demo mode configuration
DEMO_MODE = True
print("[DEMO] ================================================")
print("[DEMO] Floor Plan Drawing App - AI Course Presentation")
print("[DEMO] ================================================")
print(f"[DEMO] Demo Mode: {'ACTIVE' if DEMO_MODE else 'INACTIVE'}")


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for demo visibility."""
    print("\n[DEMO] ================================================")
    print("[DEMO] UNHANDLED EXCEPTION OCCURRED:")
    print("[DEMO] ================================================")
    print(f"[DEMO] Exception Type: {exc_type.__name__}")
    print(f"[DEMO] Exception Value: {exc_value}")
    
    # Print full traceback for debugging
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    print("[DEMO] ================================================")
    print("[DEMO] Application will continue running...")
    print("[DEMO] ================================================")


def bootstrap_application():
    """Bootstrap the application with error handling."""
    try:
        print("[DEMO] Initializing application components...")
        
        # Database setup
        print("[DEMO] Setting up database...")
        db_manager = DatabaseManager()
        db_session = db_manager.get_session()
        print("[DEMO] Database initialized successfully")
        
        # Repositories
        print("[DEMO] Initializing repositories...")
        map_repo = MapRepository(db_session)
        room_repo = RoomRepository(db_session)
        user_repo = UserRepository()
        stair_repo = StairRepository(db_session, db_manager.engine)
        pathway_repo = PathwayRepository(db_session, db_manager.engine)
        print("[DEMO] Repositories initialized")
        
        # Domain components
        print("[DEMO] Initializing domain components...")
        user_manager = UserManager()
        search_engine = SearchEngine()
        pathfinder: Pathfinder = DijkstraPathfinder()
        workflow = SimpleMapWorkflow()
        print("[DEMO] Domain components initialized")
        
        # Controllers
        print("[DEMO] Initializing controllers...")
        auth_controller = AuthController(user_manager, user_repo)
        map_controller = MapController(map_repo, room_repo, pathfinder, workflow)
        search_controller = SearchController(search_engine, map_repo)
        navigation_controller = NavigationController(map_repo, room_repo, stair_repo, pathfinder, pathway_repo=pathway_repo)
        print("[DEMO] Controllers initialized")
        
        # UI
        print("[DEMO] Initializing user interface...")
        ui = UserInterface(auth_controller, map_controller, search_controller, navigation_controller)
        print("[DEMO] User interface initialized")
        
        # Qt Application
        print("[DEMO] Creating Qt application...")
        app = QApplication(sys.argv)
        app.setApplicationName("Floor Plan Drawing App - AI Demo")
        
        # Set up global exception handler
        sys.excepthook = handle_exception
        
        # Main Window
        print("[DEMO] Creating main window...")
        main_window = MainWindow(ui, map_controller, navigation_controller, room_repo, db_session, db_engine=db_manager.engine)
        ui.set_main_window(main_window)
        
        # Load demo data after window is shown
        def load_demo_data():
            """Load sample floor plan data for immediate demo."""
            try:
                print("[DEMO] Loading demo floor plan data...")
                # Load the first floor plan for immediate display
                floor_plans = map_repo.find_all()
                if floor_plans:
                    first_floor = floor_plans[0]
                    map_controller.load_map(first_floor.floor_id)
                    print(f"[DEMO] Loaded floor plan: {first_floor.name}")
                    print("[DEMO] Demo data ready for presentation!")
                else:
                    print("[DEMO] No floor plans found in database")
            except Exception as e:
                print(f"[DEMO] Error loading demo data: {e}")
        
        # Schedule demo data loading after window is shown
        QTimer.singleShot(100, load_demo_data)
        
        main_window.show()
        print("[DEMO] Main window displayed")
        print("[DEMO] Application bootstrap complete!")
        
        return app, db_manager
        
    except Exception as e:
        print(f"[DEMO] CRITICAL ERROR during bootstrap: {e}")
        traceback.print_exc()
        
        # Show error dialog if Qt is available
        try:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Demo Startup Error")
            msg.setText("Failed to initialize the Floor Plan Drawing Application")
            msg.setInformativeText(f"Error: {str(e)}\n\nCheck console for details.")
            msg.exec()
        except:
            pass
        
        return None, None


def main():
    """Main entry point with comprehensive error handling."""
    try:
        print("[DEMO] Starting Floor Plan Drawing Application...")
        
        app, db_manager = bootstrap_application()
        
        if app is None:
            print("[DEMO] Failed to initialize application")
            return 1
        
        print("[DEMO] Application ready - entering event loop...")
        print("[DEMO] Use Ctrl+C to exit the demo")
        
        # Run the application
        exit_code = app.exec()
        
        print(f"[DEMO] Application exited with code: {exit_code}")
        
        # Cleanup
        if db_manager:
            print("[DEMO] Closing database connection...")
            db_manager.close()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n[DEMO] Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"[DEMO] FATAL ERROR in main: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
