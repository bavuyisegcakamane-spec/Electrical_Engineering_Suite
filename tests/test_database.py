from database.database import Database
from database.models import ProjectModel


database = Database()

database.initialize()

projects = ProjectModel(database)

project_id = projects.create(
    "Factory Electrical Project",
    "Initial electrical engineering project."
)

print(f"Created project ID: {project_id}")

all_projects = projects.get_all()

for project in all_projects:
    print(project)

database.close()