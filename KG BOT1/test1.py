from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "password123"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

with driver.session() as session:
    result = session.run('RETURN "Python connected to Neo4j" AS msg')
    print(result.single()["msg"])

driver.close()
