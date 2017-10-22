CREATE TABLE `mysql_instances` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `mysql_host` varchar(16) DEFAULT NULL,
  `mysql_port` int(11) DEFAULT NULL,
  `mysql_comment` varchar(2000) DEFAULT NULL,
  `manage_user` varchar(32) DEFAULT NULL,
  `manage_password` varchar(32) DEFAULT NULL,
  `is_master` int(11) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `master_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `slow_log` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `instance_id` int(11) DEFAULT NULL,
  `query_time` varchar(16) DEFAULT NULL,
  `last_errno` varchar(8) DEFAULT NULL,
  `rows_examined` int(11) DEFAULT NULL,
  `rows_sent` int(11) DEFAULT NULL,
  `log_timestamp` int(11) DEFAULT '0',
  `fingerprint_md5` varchar(32) DEFAULT NULL,
  `bytes_sent` int(11) DEFAULT NULL,
  `lock_time` varchar(16) DEFAULT NULL,
  `killed` int(11) DEFAULT NULL,
  `cmd_user` varchar(32) DEFAULT NULL,
  `query_sql` text,
  `cmd_ip` varchar(16) DEFAULT NULL,
  `query_date` datetime DEFAULT NULL,
  `cmd_schema` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `slow_query_fingerprint` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `instance_id` int(11) DEFAULT '0',
  `md5code` varchar(64) DEFAULT NULL,
  `sql_fingerprint` text,
  `first_apper_time` datetime DEFAULT '0000-00-00 00:00:00',
  `last_apper_time` datetime DEFAULT '0000-00-00 00:00:00',
  `total_number` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_idx_ii_md5` (`instance_id`,`md5code`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

create table mysql_performance_quota(
  id int unsigned NOT NULL AUTO_INCREMENT,
  `instance_id` int(11) DEFAULT '0',
  create_time datetime,
  com_select INT ,
  com_delete int ,
  questions int ,
  com_insert int ,
  com_commit int ,
  com_rollback int ,
  com_update int ,
  qps int,
  tps int,
  PRIMARY KEY (`id`),
  key create_time(create_time)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;
