USE warbler;

DROP TABLE IF EXISTS punish;
CREATE TABLE punish
(
  userId          int unsigned NOT NULL, # Unique ID for the record
  punishTier      tinyint NOT NULL,                # Full title of the book
  punishTime      varchar(255) NOT NULL,                # The author of the book
  price           decimal(10,2) NOT NULL,               # The price of the book

  PRIMARY KEY     (userId)
);