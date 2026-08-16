"""Database models and operations."""

import json


class ProjectModel:
    """Handle project-related database operations."""

    def __init__(self, database):
        self.database = database

    def create(self, name, description=""):
        """Create a new project."""

        query = """
            INSERT INTO projects (name, description)
            VALUES (?, ?)
        """

        cursor = self.database.execute(
            query,
            (name, description),
        )

        return cursor.lastrowid

    def get_all(self):
        """Return all projects."""

        query = """
            SELECT
                id,
                name,
                description,
                created_at,
                updated_at
            FROM projects
            ORDER BY created_at DESC
        """

        return self.database.fetch_all(query)

    def get_by_id(self, project_id):
        """Return one project."""

        query = """
            SELECT
                id,
                name,
                description,
                created_at,
                updated_at
            FROM projects
            WHERE id = ?
        """

        return self.database.fetch_one(
            query,
            (project_id,),
        )

    def delete(self, project_id):
        """Delete a project."""

        query = """
            DELETE FROM projects
            WHERE id = ?
        """

        self.database.execute(
            query,
            (project_id,),
        )


class CalculationModel:
    """Handle calculation history."""

    def __init__(self, database):
        self.database = database

    def save(
        self,
        calculation_type,
        input_data,
        result_data,
        project_id=None,
    ):
        """Save a calculation."""

        query = """
            INSERT INTO calculations (
                project_id,
                calculation_type,
                input_data,
                result_data
            )
            VALUES (?, ?, ?, ?)
        """

        cursor = self.database.execute(
            query,
            (
                project_id,
                calculation_type,
                json.dumps(input_data),
                json.dumps(result_data),
            ),
        )

        return cursor.lastrowid

    def get_all(self):
        """Return calculation history."""

        query = """
            SELECT
                id,
                project_id,
                calculation_type,
                input_data,
                result_data,
                created_at
            FROM calculations
            ORDER BY created_at DESC
        """

        return self.database.fetch_all(query)