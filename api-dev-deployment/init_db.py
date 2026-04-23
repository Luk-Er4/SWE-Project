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

        ("1e4486e0-19f8-4856-a2e3-c91e98925b37","Mario","Villegas","mvillegas114","h7bS48aaTxLn","2026-02-16 23:05:00"),
        ("1c503e22-b2c3-4989-9c76-8d1afa36693e","Latoya","Conrad","lconrad701","c6ZJ5eE40sVg","2026-02-14 23:05:00"),
        ("9d97e207-f4ad-4942-bbc5-a332b18c0f42","Rosario","Frederick","rfrederick1220","EdJ8xrM3K66F","2026-02-10 23:05:00"),
        ("c8a18a8f-5518-4848-b3d9-7bafe0be328b","Reba","Gardner","rgard911","i/R66F{96s\\jGU","2026-01-16 23:05:00"),
        ("3b74cf2b-370b-4a46-9fe7-8bcaebbd2c38","Kathryn","Rice","krice123456","80944Cfyb","2026-01-17 23:05:00"),
        ("9198d2a0-ec23-42c2-9105-51fe8e53bb04","Alta","Cuevas","alcuev314","93GkPMnGb6{","2025-02-16 23:05:00"),
        ("3ebbac24-6eae-44f2-ade4-66fb83843c0c","Sam","Hodges","shodges111","6oq1UX1J4QzU","2025-02-16 23:05:00"),
        ("4b80f087-abab-4e53-9a83-74581c0fe8cc","Morgan","Freeman","freemanm724","z5c52n2Ze","2024-10-15 23:05:00"),
        ("6c52a8ac-641d-4502-8fe6-1e31f147776e","Glen","Harrington","gharring1030","w]X71N11UY[9nJ","2023-09-03 23:05:00"),
        ("f18670a4-23a6-43f9-8a9f-5243a0133852","Trevor","Stokes","tstokes000","8m88M3uEot","2022-01-01 23:05:00"),
        ("686d708e-b8ed-4aee-94e6-420ba268952d","Edmond","Turner","edmondurner333","4fvF\\FZ52t1","2026-02-16 22:05:00"),
        ("0a82c07a-cc6b-471d-bf30-564193b1020b","Zachery","Dougherty","cherydought8","\\Er8oX6u9t","2026-02-14 11:05:00"),
        ("c24bae0a-3b7b-4502-8c35-6e6cb08adeae","Quentin","Freeman","qfree7777","i98Fz3AHKRsp","2019-02-10 23:05:00"),
        ("b743185a-5d39-4ee1-8c6e-0f5e87fcaec3","Alexandra","Adams","aadam1234","we7tH3C9k","2017-01-16 23:05:00"),
        ("19fac969-d5a2-4ad0-a971-7c6f7a5a674f","Brigitte","Patton","brigitton1","GP93jz1NBbiw","2015-01-17 23:05:00"),
        ("29b3ecb8-ca76-413b-b4f6-3bb862545294","Lea","Liu","leau8754","tB5L8v9HD","2010-02-16 23:05:00"),
        ("6737d247-1c82-4d5f-8644-bb3f7a9ae2b3","Hank","Allen","hallen10","uFv7948Rrv10","1999-02-13 23:05:00"),
        ("4123f076-0001-4717-b2ee-88370f805ba7","Todd","Huynh","tohuyn9","zCP9{7467a","1998-01-05 23:05:00"),
        ("20b22d7b-c3e7-4729-bc09-f2a5db64a3ff","Eliza","Chang","echang235","4n7CLZYe2F4Qh2q/","2030-12-31 23:05:00"),
        ("3b35e6c6-f20d-4e2b-b92b-e47ddaea069e","Eugenia","Mahoney","emahoney452","Me1HOf937","1975-01-01 23:05:00")

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