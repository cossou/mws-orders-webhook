CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `seller_id` varchar(45) NOT NULL,
  `seller_order_id` varchar(45) NOT NULL,
  `order_status` varchar(100) NOT NULL DEFAULT 'Pending',
  `failed` int(3) NOT NULL DEFAULT '0',
  `syncronized` tinyint(1) NOT NULL DEFAULT '0',
  `syncronized_at` timestamp NULL DEFAULT NULL,
  `payload` json NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE_KEY` (`seller_id`,`seller_order_id`,`order_status`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
