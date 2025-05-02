from neo4j import GraphDatabase
from app.core.config import settings
from contextlib import contextmanager

class Neo4jDatabase:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self._driver = None

    def connect(self):
        if not self._driver:
            self._driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    @contextmanager
    def get_session(self):
        driver = self.connect()
        session = driver.session()
        try:
            yield session
        finally:
            session.close()
    
    def initialize_database(self):
        """Initialize the database with required constraints and indices"""
        with self.get_session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:RoadNode) REQUIRE n.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:ChargingStation) REQUIRE c.id IS UNIQUE")
            
            # Create indices for spatial queries
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:RoadNode) ON (n.latitude, n.longitude)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (c:ChargingStation) ON (c.latitude, c.longitude)")
            
            print("Neo4j database initialized with constraints and indices")

# Singleton instance
db = Neo4jDatabase()
