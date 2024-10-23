
CREATE TABLE IF NOT EXISTS app_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    profile_image VARCHAR(255) NOT NULL,
    bio TEXT,
    gender VARCHAR(10) NOT NULL,
    gender_pref VARCHAR(10) NOT NULL,
    fame_rate DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW app_profile AS
SELECT id, username, last_name, first_name, age, profile_image, bio, gender, gender_pref, fame_rate
FROM app_user;

-- TAGS Many2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tag (
  id SERIAL PRIMARY KEY,
  name VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS user_tag (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    tag_id INTEGER,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_tag FOREIGN KEY(tag_id) REFERENCES tag(id) ON DELETE CASCADE
);

-- FRIENDSHIP One2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS friendship (
    id SERIAL PRIMARY KEY,
    state VARCHAR(255) NOT NULL,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender FOREIGN KEY(sender_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_receiver FOREIGN KEY(receiver_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT unique_friendship UNIQUE(sender_id, receiver_id)
);

-- BLOCK One2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS block (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender FOREIGN KEY(sender_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_receiver FOREIGN KEY(receiver_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT unique_block UNIQUE(sender_id, receiver_id)
);
-- VIEW One2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS visit (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender FOREIGN KEY(sender_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_receiver FOREIGN KEY(receiver_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT unique_visit UNIQUE(sender_id, receiver_id)
);

-- NOTIF One2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notif (
    id SERIAL PRIMARY KEY,
    state VARCHAR(255) NOT NULL,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender FOREIGN KEY(sender_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_receiver FOREIGN KEY(receiver_id) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT unique_notif UNIQUE(state, sender_id, receiver_id)
);

-- CHANNEL One2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS channel (
    id SERIAL PRIMARY KEY,
    user_a INTEGER NOT NULL,
    user_b INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sender FOREIGN KEY(user_a) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_receiver FOREIGN KEY(user_b) REFERENCES app_user(id) ON DELETE CASCADE,
    CONSTRAINT unique_channel UNIQUE(user_a, user_b)
);

-- MESSAGE One2many -----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_channel FOREIGN KEY(channel_id) REFERENCES channel(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY(sender_id) REFERENCES app_user(id) ON DELETE CASCADE
);
