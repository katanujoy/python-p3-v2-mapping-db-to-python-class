from __init__ import CURSOR, CONN

class Department:
    # Dictionary to store all Department instances
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """Create the departments table"""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the departments table"""
        sql = "DROP TABLE IF EXISTS departments;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Save Department instance to database and update dictionary"""
        if self.id is None:
            # Insert new record
            sql = """
                INSERT INTO departments (name, location)
                VALUES (?, ?)
            """
            CURSOR.execute(sql, (self.name, self.location))
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            # Update existing record
            self.update()

    @classmethod
    def create(cls, name, location):
        """Create and save a new Department instance"""
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the database row for this Department instance"""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the database row and remove from dictionary"""
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        # Remove from dictionary if exists
        if self.id in type(self).all:
            del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Return a Department instance from a database row"""
        department = cls.all.get(row[0])
        if department:
            # Update existing instance
            department.name = row[1]
            department.location = row[2]
        else:
            # Create new instance
            department = cls(row[1], row[2])
            department.id = row[0]
            cls.all[department.id] = department
        return department

    @classmethod
    def get_all(cls):
        """Return all Department instances from database"""
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Find Department by id"""
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find first Department with matching name"""
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_or_create_by(cls, name, location):
        """Find department by name or create if not found"""
        department = cls.find_by_name(name)
        if not department:
            department = cls.create(name, location)
        return department