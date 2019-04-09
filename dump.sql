CREATE TABLE `deposits` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `currency` varchar(3) NOT NULL,
  `country` varchar(10) NOT NULL,
  `city` varchar(30) NOT NULL,
  `amount` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`currency`,`country`,`city`)
)
