usrinput = input("is this your first time?")
createtable1 = """
CREATE TABLE IF NOT EXISTS `punish` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `userId` bigint(20) unsigned NOT NULL COMMENT 'The snowflake id of a punished user',
  `guildId` bigint(20) unsigned NOT NULL COMMENT 'The id of the guild given user was punished in',
  `punishTier` tinyint(2) unsigned NOT NULL COMMENT 'The tier a given user is on (does not necessarily represent if the user is currently serving a punishment, as it may decrease (every two weeks!) before a users punishment is over), serves as a baseline for future punishments)',
  `punishTime` bigint(20) unsigned DEFAULT NULL COMMENT 'The time a user received the punishment they are currently serving, may be empty if user has points but their punishment has ended',
  `punishLength` int(10) unsigned DEFAULT NULL COMMENT 'The length of a punishment a user is serving, may be empty if user has points but their punishment has ended',
  `punishType` tinytext DEFAULT NULL COMMENT 'm, or b = mute or ban so that when it comes time to revoke a punishment the bot knows what to remove, may be empty if user has points but their punishment has ended',
  `updateTime` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'represents the last time that a row was updated (by any means)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;
"""
createtable2 = """
CREATE TABLE IF NOT EXISTS `guilds` (
  `guildId` bigint(20) unsigned NOT NULL COMMENT 'id of guild',
  `modRole` bigint(20) unsigned DEFAULT NULL COMMENT 'mod role id',
  `muteRole` bigint(20) unsigned DEFAULT NULL COMMENT 'muted role id',
  `memberRole` bigint(20) unsigned DEFAULT NULL COMMENT 'member role id',
  `punishTiers` varchar(100) DEFAULT NULL COMMENT 'punish tiers',
  `membersCanViewUserTiers` bit(1) NOT NULL DEFAULT b'1' COMMENT 'bool, if members can view punish tiers',
  `logging` bit(1) NOT NULL DEFAULT b'1' COMMENT 'if logging is enabled',
  `modmail` bit(1) NOT NULL DEFAULT b'1' COMMENT 'if modmail is enabled',
  `loggingChannel` bigint(20) unsigned DEFAULT NULL COMMENT 'logging channel id',
  `modmailChannel` bigint(20) unsigned DEFAULT NULL COMMENT 'modmail channel id',
  `wordGraylist` varchar(100) DEFAULT NULL COMMENT 'words to delete',
  `wordBlacklist` varchar(100) DEFAULT NULL COMMENT 'delete + point',
  `autoRemoveTime` bigint(20) NOT NULL DEFAULT 1209600 COMMENT 'auto punish purge time. 0 = never',
  `BlacklistPoints` bit(1) NOT NULL DEFAULT b'1' COMMENT 'points to add if blacklisted word is said',
  `guildIsPremium` bit(1) NOT NULL DEFAULT b'0' COMMENT 'if a guild is premium',
  `guildPremiumMonths` bit(1) NOT NULL DEFAULT b'0' COMMENT 'how many months of premium a guild has',
  `lastPremiumPurge` datetime DEFAULT NULL COMMENT 'last time a month was removed from premium standing',
  `isSuper` bit(1) NOT NULL DEFAULT b'0' COMMENT 'if guild is admin (global point addition/removal)',
  `maxPointGrant` MEDIUMINT NULL COMMENT 'Max points that can be granted in one go',
  PRIMARY KEY (`guildId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='server guilds';
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
  connection = pymysql.connect(host='localhost',user='root',password='root',database='warbler',cursorclass=pymysql.cursors.DictCursor)
  execute(createtable1)
  execute(createtable2)
  input("Epic. now add your token to you ENV variables and party")

else:
    print("run main.py normally")
