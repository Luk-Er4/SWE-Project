def init_db(db):
    cursor = db.cursor()

    # Create schema
    cursor.execute("""
    CREATE SCHEMA IF NOT EXISTS healthsys;
    """)

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS healthsys.login_attempts (
        la_uuid varchar(36) primary key,
        datetime_sent datetime,
        typed_id varchar(30),
        typed_pw varchar(30),
        status varchar(100)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS healthsys.user_priv_info (
        u_uuid varchar(36) primary key,
        first_name varchar(30),
        last_name varchar(30),
        user_id varchar(30),
        user_pw varchar(100),
        created_at datetime
    );
    """)

    # Insert seed data
    cursor.executemany("""
    INSERT IGNORE INTO healthsys.user_priv_info (
        u_uuid,
        first_name,
        last_name,
        user_id,
        user_pw,
        created_at
    )
    VALUES (%s, %s, %s, %s, %s, %s);
    """, [

        ("1e4486e0-19f8-4856-a2e3-c91e98925b37","Mario","Jerry","eightnine10","$2b$12$SrOHANY1QfFY7ZIr9JSVPeAwmrLAQtRPOfmzLA9EEnJMDNJ0mEXTy","2026-02-16 23:05:00"), # !111r8oX9t
        ("1c503e22-b2c3-4989-9c76-8d1afa36693e","Eliza","Villegas","cherydght77778","$2b$12$ZieEg4fIxFOVlVFC3a1gL.TVnHUSZ4yqZqY2jK0hrb4lF7.xCrXje","2026-02-14 23:05:00"), # p@as$vv0rD
        ("9198d2a0-ec23-42c2-9105-51fe8e53bb04","Alta","Cuevas","alcuev314","$2b$12$nVUWkS7YBjiORc2Sus6lrO9Sy86LLCO4KVCMKJrZUL45odP/U5jdC","2025-02-16 23:05:00") # 93GkPMnGb6{

    ])

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS healthsys.user_health_info
    (
        user_uuid varchar(36) primary key,
        age int,
        gender varchar(20),
        smoking varchar(20),
        activity float,
        sleep float,
        bmi float,
        stress_level float,
        profession varchar(20),
        education varchar(20) ,
        diet int,
        diseases int,
        country varchar(20)
    )
    """)


    cursor.execute("""
    INSERT IGNORE INTO healthsys.user_health_info (user_uuid, age, gender, smoking, activity, sleep, bmi, stress_level, profession, education, diet, diseases, country)
    VALUES 
        ("0a82c07a-cc6b-471d-bf30-564193b1020b", 73, "Female", "Never",  2,   9,   27,   1,    "Doctor",      "Master's Degree",   3462,  11, "Indonesia"),
        ("130ef649-51f0-4586-8832-e3842eff4a2f", 24, "Male",   "High",   12,  9,   15,   0.5,  "Farmer",      "High School",       3000,  5,  "China"),
        ("134695be-c6e4-482e-929d-d40fd522a0b1", 60, "Male",   "High",   10,  7,   19,   0.31, "Shop Keeper", "Some College",      2361,  11, "Canada"),
        ("14882cf4-b3e4-4560-bf9a-f50b9e8f62ba", 14, "Female", "High",   3.7, 8.7, 22.1, 0.73, "Scholar",     "Middle School",     2895,  10, "Pakistan"),
        ("19fac969-d5a2-4ad0-a971-7c6f7a5a674f", 21, "Female", "Medium", 5.7, 6.1, 20.6, 0.58, "Doctor",      "Bachelor's Degree", 2990,  10, "Japan"),
        ("1c503e22-b2c3-4989-9c76-8d1afa36693e", 42, "Male",   "High",   1.4, 7.8, 36.7, 0.61, "Company CEO", "PhD"               ,3403,  13, "United States"),
        ("1e4486e0-19f8-4856-a2e3-c91e98925b37", 38, "Female", "Never",  9.5, 5.2, 19.6, 0.87, "Soldier",     "Some College",      2899,  2,  "Canada"),
        ("20b22d7b-c3e7-4729-bc09-f2a5db64a3ff", 7,  "Male",   "Never",  10.1,7.1, 10.1, 0.01, "Engineer",    "PhD",			   1200,  0,  "United States")
    """)

    db.commit()

    print("Database initialized with seed data")

    cursor.close()