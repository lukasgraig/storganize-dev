DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS storage_box;

CREATE TABLE user (
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL, 
  PRIMARY KEY (username)
);

CREATE TABLE storage_box (
  uuid TEXT NOT NULL,
  username TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  box_type TEXT NOT NULL,
  box_title TEXT NOT NULL,
  box_desc TEXT NOT NULL,
  PRIMARY KEY (uuid),
  FOREIGN KEY (username) REFERENCES user (username)
);

CREATE TABLE items (
    item TEXT NOT NULL,
    uuid TEXT NOT NULL,
    FOREIGN KEY (uuid) REFERENCES storage_box (uuid)
)