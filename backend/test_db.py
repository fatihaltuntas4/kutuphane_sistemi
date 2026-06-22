import models
from database import SessionLocal

db = SessionLocal()
try:
    new_user = models.User(
        full_name="Test",
        email="test999@test.com",
        hashed_password="123",
        role=models.RoleEnum.admin
    )
    db.add(new_user)
    db.commit()
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
