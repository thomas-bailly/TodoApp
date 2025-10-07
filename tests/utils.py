from sqlalchemy.orm import DeclarativeBase

def model_to_dict(model_instance: DeclarativeBase, exclude: set[str] | None = None) -> dict:
    """Converts a SQLAlchemy model instance into a dictionary containing its column data.

    Args:
        model_instance: The SQLAlchemy model instance to convert.
        exclude: A set of column names (strings) to exclude from the resulting dictionary 
                 (e.g., {'hashed_password'}).
    
    Returns:
        dict: A dictionary mapping column names to their values.
    """
    if exclude is None:
        exclude = set()
        
    data = {}
    
    for column in model_instance.__table__.columns:
        if column.name not in exclude:
            data[column.name] = getattr(model_instance, column.name)
            
    return data