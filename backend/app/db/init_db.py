import logging
from app.db.neo4j import db
from app.models.location import Location

logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with sample data for testing"""
    logger.info("Initializing database with sample data")

    try:
        # Initialize constraints and indices
        db.initialize_database()
        
        # Add sample charging stations
        with db.get_session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create road network nodes
            create_road_network(session)
            
            # Create charging stations
            create_charging_stations(session)
            
        logger.info("Sample data initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def create_road_network(session):
    """Create a simple road network for testing"""
    # Create major cities as road nodes
    cities = [
        ("NYC", 40.7128, -74.0060, "New York City"),
        ("PHL", 39.9526, -75.1652, "Philadelphia"),
        ("DC", 38.9072, -77.0369, "Washington DC"),
        ("BOS", 42.3601, -71.0589, "Boston"),
        ("CHI", 41.8781, -87.6298, "Chicago"),
        ("DET", 42.3314, -83.0458, "Detroit"),
        ("CLE", 41.4993, -81.6944, "Cleveland"),
        ("PIT", 40.4406, -79.9959, "Pittsburgh"),
        ("IND", 39.7684, -86.1581, "Indianapolis"),
        ("CIN", 39.1031, -84.5120, "Cincinnati")
    ]
    
    # Create city nodes
    for city_id, lat, lng, name in cities:
        session.run("""
            CREATE (n:RoadNode {
                id: $id,
                latitude: $lat,
                longitude: $lng,
                name: $name
            })
        """, id=city_id, lat=lat, lng=lng, name=name)
    
    # Create road connections
    connections = [
        ("NYC", "PHL", 150),  # New York to Philadelphia
        ("PHL", "DC", 220),   # Philadelphia to Washington DC
        ("NYC", "BOS", 330),  # New York to Boston
        ("PHL", "PIT", 400),  # Philadelphia to Pittsburgh
        ("DC", "PIT", 320),   # Washington DC to Pittsburgh
        ("BOS", "CLE", 890),  # Boston to Cleveland
        ("PIT", "CLE", 210),  # Pittsburgh to Cleveland
        ("CLE", "DET", 270),  # Cleveland to Detroit
        ("DET", "CHI", 450),  # Detroit to Chicago
        ("CLE", "CIN", 380),  # Cleveland to Cincinnati
        ("CIN", "IND", 170),  # Cincinnati to Indianapolis
        ("CHI", "IND", 290)   # Chicago to Indianapolis
    ]
    
    # Create road connections
    for city1, city2, distance in connections:
        # Create bidirectional relationships for roads
        session.run("""
            MATCH (a:RoadNode {id: $city1}), (b:RoadNode {id: $city2})
            CREATE (a)-[:CONNECTS_TO {distance: $distance}]->(b),
                   (b)-[:CONNECTS_TO {distance: $distance}]->(a)
        """, city1=city1, city2=city2, distance=distance)

def create_charging_stations(session):
    """Create charging stations near major cities"""
    # Define charging stations with coordinates near major cities
    charging_stations = [
        # Near New York
        ("CS1", 40.7000, -74.0200, "Manhattan Supercharger", "NYC"),
        ("CS2", 40.6892, -73.9800, "Brooklyn Charging Hub", "NYC"),
        
        # Near Philadelphia
        ("CS3", 39.9400, -75.1700, "Philly Central Charging", "PHL"),
        
        # Near Washington DC
        ("CS4", 38.9000, -77.0300, "DC Fast Charge", "DC"),
        
        # Between New York and Philadelphia
        ("CS5", 40.2200, -74.7600, "NJ Turnpike Charging", None),
        
        # Between Philadelphia and Washington DC
        ("CS6", 39.5800, -76.0700, "Maryland Charging Station", None),
        
        # Near Boston
        ("CS7", 42.3500, -71.0700, "Boston Power Hub", "BOS"),
        
        # Near Chicago
        ("CS8", 41.8700, -87.6400, "Chicago Loop Chargers", "CHI"),
        
        # Near Cleveland
        ("CS9", 41.4900, -81.7000, "Cleveland Energy Center", "CLE"),
        
        # Between Cleveland and Detroit
        ("CS10", 41.7900, -82.8000, "Lake Erie Charging Point", None)
    ]
    
    # Create charging station nodes
    for cs_id, lat, lng, name, near_city in charging_stations:
        # Create the charging station
        session.run("""
            CREATE (c:ChargingStation {
                id: $id,
                latitude: $lat,
                longitude: $lng,
                name: $name,
                connectors: $connectors,
                power: $power,
                available: true
            })
        """, 
            id=cs_id, 
            lat=lat, 
            lng=lng, 
            name=name,
            connectors=["CCS", "CHAdeMO", "Type2"],
            power=150.0
        )
        
        # If the station is near a city, create a relationship
        if near_city:
            session.run("""
                MATCH (c:ChargingStation {id: $cs_id}), (n:RoadNode {id: $city_id})
                CREATE (c)-[:NEAR {distance: 5.0}]->(n)
            """, cs_id=cs_id, city_id=near_city)
