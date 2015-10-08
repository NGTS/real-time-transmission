DROP TABLE IF EXISTS `job_args`;
DROP TABLE IF EXISTS `job_queue`;
CREATE TABLE `job_queue` (
  `job_id` int(11) NOT NULL AUTO_INCREMENT,
  `job_type` char(20) DEFAULT NULL,
  `submitted` datetime DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=172399 DEFAULT CHARSET=latin1;

INSERT INTO `job_queue` VALUES (28,'transparency','2015-09-20 23:40:04','2015-09-21 23:40:04'),(29,'transparency','2015-09-20 23:40:04','2015-09-21 23:40:04'),(30,'transparency','2015-09-20 23:40:04','2015-09-21 23:40:04'),(31,'transparency','2015-09-20 23:40:04','2015-09-21 23:40:04'),(32,'transparency','2015-09-20 23:40:17','2015-09-21 23:40:17');

CREATE TABLE `job_args` (
  `job_id` int(11) NOT NULL DEFAULT '0',
  `arg_key` char(50) NOT NULL DEFAULT '',
  `arg_value` text,
  PRIMARY KEY (`job_id`,`arg_key`),
  CONSTRAINT `job_args_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `job_queue` (`job_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `job_args` VALUES (28,'file','/ngts/das05/action106249_observeField/IMAGE80120150920233952.fits'),(29,'file','/ngts/das03/action106267_observeField/IMAGE80520150920233952.fits'),(30,'file','/ngts/das06/action106258_observeField/IMAGE80220150920233952.fits'),(31,'file','/ngts/das02/action106276_observeField/IMAGE80620150920233952.fits'),(32,'file','/ngts/das03/action106267_observeField/IMAGE80520150920234004.fits');
