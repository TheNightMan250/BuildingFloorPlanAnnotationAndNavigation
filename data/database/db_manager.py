from models import DatabaseManager


def get_db_manager(db_path="data/database/floorplan_project.db"):
    import os
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return DatabaseManager(db_path)


def get_session(db_manager):
    return db_manager.get_session()


def close_db(db_manager):
    db_manager.close()
