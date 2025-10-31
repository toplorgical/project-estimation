import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to PostgreSQL with the postgres user
    print("Connecting to PostgreSQL...")
    # Try different password options
    passwords = ['postgres', '', 'admin', 'password', '123456']
    conn = None
    
    for pwd in passwords:
        try:
            print(f"  Trying password: '{pwd if pwd else '(empty)'}'...")
            conn = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password=pwd,
                host='localhost',
                port=5432
            )
            print(f"  ✓ Connected with password: '{pwd if pwd else '(empty)'}'")
            break
        except psycopg2.OperationalError:
            continue
    
    if conn is None:
        print("\n❌ Could not connect with any common password.")
        print("\nPlease manually create the database by running:")
        print("  1. Open pgAdmin or SQL Shell (psql)")
        print("  2. Connect as postgres user")
        print("  3. Run these commands:")
        print("     CREATE DATABASE toplorgical;")
        print("     CREATE USER toplorgical WITH PASSWORD 'toplorgical123';")
        print("     GRANT ALL PRIVILEGES ON DATABASE toplorgical TO toplorgical;")
        exit(1)
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Create database
    print("Creating database 'toplorgical'...")
    try:
        cur.execute("CREATE DATABASE toplorgical;")
        print("✓ Database created successfully!")
    except psycopg2.errors.DuplicateDatabase:
        print("! Database 'toplorgical' already exists")
    
    # Create user
    print("Creating user 'toplorgical'...")
    try:
        cur.execute("CREATE USER toplorgical WITH PASSWORD 'toplorgical123';")
        print("✓ User created successfully!")
    except psycopg2.errors.DuplicateObject:
        print("! User 'toplorgical' already exists")
    
    # Grant privileges
    print("Granting privileges...")
    cur.execute("GRANT ALL PRIVILEGES ON DATABASE toplorgical TO toplorgical;")
    print("✓ Privileges granted!")
    
    cur.close()
    conn.close()
    
    print("\n✅ Database setup complete!")
    print("Database: toplorgical")
    print("User: toplorgical")
    print("Password: toplorgical123")
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Error connecting to PostgreSQL: {e}")
    print("\nPlease ensure:")
    print("1. PostgreSQL is running")
    print("2. The postgres user password is correct (default: 'postgres')")
    print("3. PostgreSQL is listening on localhost:5432")
except Exception as e:
    print(f"\n❌ Error: {e}")
