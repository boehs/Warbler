usrinput = input("is this your first time?")
createtable1 = """
-- warbler.punish definition

CREATE TABLE IF NOT EXISTS `punish` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `userId` bigint(20) unsigned NOT NULL COMMENT 'The snowflake id of a punished user',
  `guildId` bigint(20) unsigned NOT NULL,
  `punishTier` tinyint(2) unsigned NOT NULL COMMENT 'The tier a given user is on (does not necessarily represent if the user is currently serving a punishment, as it may decrease (every two weeks!) before a users punishment is over), serves as a baseline for future punishments)',
  `punishTime` bigint(20) unsigned DEFAULT NULL COMMENT 'The time a user received the punishment they are currently serving, may be empty if user has points but their punishment has ended',
  `punishLength` int(10) unsigned DEFAULT NULL COMMENT 'The length of a punishment a user is serving, may be empty if user has points but their punishment has ended',
  `punishType` tinytext DEFAULT NULL COMMENT 'm, or b = mute or ban so that when it comes time to revoke a punishment the bot knows what to remove, may be empty if user has points but their punishment has ended',
  `updateTime` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
"""
createtable2 = """
-- warbler.guild definition

CREATE TABLE IF NOT EXISTS `guild` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `guildId` bigint(20) unsigned NOT NULL,
  `modRoleId` bigint(20) unsigned,
  `memberRoleId` bigint(20) unsigned,
  `mutedRoleId` bigint(20) unsigned,
  `punishTiers` bigint(20) unsigned,
  `membersCanViewTier` bool,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4;
"""

def execute(query):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()

if usrinput.lower() == "yes" or usrinput.lower() == "y":
  import os
  os.system("pip install -r requirements.txt")
  input("Install MySQL. start a server, and create a database named 'warbler' with no password and a username of 'root'. hit enter when done: ")
  import pymysql.cursors
  connection = pymysql.connect(host='localhost',user='root',password='',database='warbler',cursorclass=pymysql.cursors.DictCursor)
  execute(createtable1)
  execute(createtable1)
  input("Epic. now add your token to you ENV variables and party")

else:
    print("run main.py normally")