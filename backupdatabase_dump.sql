BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('4806a403dd1f');
CREATE TABLE backup_date (
	id INTEGER NOT NULL, 
	last_date DATE, 
	PRIMARY KEY (id)
);
INSERT INTO "backup_date" VALUES(1,'2022-03-15');
INSERT INTO "backup_date" VALUES(2,'2022-01-01');
CREATE TABLE banners (
	bid INTEGER NOT NULL, 
	name VARCHAR, 
	b_url VARCHAR, 
	PRIMARY KEY (bid), 
	UNIQUE (name)
);
CREATE TABLE genre (
	gid INTEGER NOT NULL, 
	mid INTEGER, 
	name VARCHAR, 
	image_url VARCHAR, 
	PRIMARY KEY (gid), 
	FOREIGN KEY(mid) REFERENCES user_table (uid)
);
CREATE TABLE movie (
	mid INTEGER NOT NULL, 
	uid INTEGER, 
	name VARCHAR, 
	short_description VARCHAR, 
	image_url VARCHAR, 
	date DATE, 
	description VARCHAR, 
	q480p VARCHAR, 
	q720p VARCHAR, 
	q1080p VARCHAR, 
	genre VARCHAR, 
	"Language" VARCHAR, 
	"Director" VARCHAR, 
	"Type" VARCHAR, 
	orignal INTEGER, 
	trending BOOLEAN, 
	sid INTEGER, 
	PRIMARY KEY (mid), 
	FOREIGN KEY(uid) REFERENCES user_table (uid), 
	FOREIGN KEY(sid) REFERENCES season (sid)
);
CREATE TABLE "order" (
	oid INTEGER NOT NULL, 
	uid INTEGER, 
	date DATE NOT NULL, 
	valid_till DATE NOT NULL, 
	total_price INTEGER NOT NULL, 
	payment_id VARCHAR, 
	membership VARCHAR, 
	amount VARCHAR, 
	payment_status VARCHAR, 
	PRIMARY KEY (oid), 
	FOREIGN KEY(uid) REFERENCES user_table (uid)
);
CREATE TABLE season (
	sid INTEGER NOT NULL, 
	name VARCHAR, 
	date DATE, 
	wsid INTEGER, 
	orignal INTEGER, 
	PRIMARY KEY (sid), 
	FOREIGN KEY(wsid) REFERENCES web_series (wsid)
);
CREATE TABLE temp_tabel (
	mid INTEGER NOT NULL, 
	gid INTEGER NOT NULL, 
	PRIMARY KEY (mid, gid), 
	FOREIGN KEY(mid) REFERENCES movie (mid), 
	FOREIGN KEY(gid) REFERENCES genre (gid)
);
CREATE TABLE user_table (
	uid INTEGER NOT NULL, 
	"Ph_number" VARCHAR, 
	email VARCHAR, 
	full_name VARCHAR, 
	password VARCHAR NOT NULL, 
	"DOB" VARCHAR NOT NULL, 
	"Gender" VARCHAR NOT NULL, 
	profile_pic VARCHAR, 
	membership VARCHAR NOT NULL, 
	razorpay_id VARCHAR NOT NULL, 
	PRIMARY KEY (uid)
);
CREATE TABLE web_series (
	wsid INTEGER NOT NULL, 
	uid INTEGER, 
	name VARCHAR, 
	short_description VARCHAR, 
	image_url VARCHAR, 
	genre VARCHAR, 
	description VARCHAR, 
	date DATE, 
	orignal INTEGER, 
	"Language" VARCHAR, 
	"Director" VARCHAR, 
	trending BOOLEAN, 
	PRIMARY KEY (wsid), 
	FOREIGN KEY(uid) REFERENCES user_table (uid)
);
COMMIT;
