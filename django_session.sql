/*
Navicat MySQL Data Transfer

Source Server         : 合肥测试172.16.154.62
Source Server Version : 50148
Source Host           : 172.16.154.62:8077
Source Database       : ifly_cp_msp_name_server

Target Server Type    : MYSQL
Target Server Version : 50148
File Encoding         : 65001

Date: 2017-08-09 09:51:37
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8_bin NOT NULL,
  `session_data` longtext COLLATE utf8_bin NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
