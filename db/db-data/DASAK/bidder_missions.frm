TYPE=VIEW
query=select `M`.`mission_id` AS `mission_id`,`M`.`employer_id` AS `employer_id`,`M`.`title` AS `title`,`M`.`description` AS `description`,`M`.`objectives` AS `objectives`,`M`.`launch_date` AS `launch_date`,`M`.`duration` AS `duration`,`M`.`num_of_astronauts` AS `num_of_astronauts`,`M`.`payload_volume` AS `payload_volume`,`M`.`payload_weight` AS `payload_weight` from (((`dasak`.`mission` `M` join `dasak`.`mission_accepted_bid` `MAB` on((`M`.`mission_id` = `MAB`.`mission_id`))) join `dasak`.`bid` `BD` on((`MAB`.`bid_id` = `BD`.`bid_id`))) join `dasak`.`bidder` `B` on((`BD`.`bidder_id` = `B`.`id`)))
md5=b5b88d623c411b1cd4d9724dcfc04bce
updatable=1
algorithm=0
definer_user=root
definer_host=localhost
suid=2
with_check_option=0
timestamp=2024-04-09 11:24:11
create-version=1
source=SELECT \n    M.mission_id,\n    M.employer_id,\n    M.title,\n    M.description,\n    M.objectives,\n    M.launch_date,\n    M.duration,\n    M.num_of_astronauts,\n    M.payload_volume,\n    M.payload_weight\nFROM \n    Mission M\nJOIN \n    Mission_Accepted_Bid MAB ON M.mission_id = MAB.mission_id\nJOIN \n    Bid BD ON MAB.bid_id = BD.bid_id\nJOIN \n    Bidder B ON BD.bidder_id = B.id
client_cs_name=latin1
connection_cl_name=latin1_swedish_ci
view_body_utf8=select `M`.`mission_id` AS `mission_id`,`M`.`employer_id` AS `employer_id`,`M`.`title` AS `title`,`M`.`description` AS `description`,`M`.`objectives` AS `objectives`,`M`.`launch_date` AS `launch_date`,`M`.`duration` AS `duration`,`M`.`num_of_astronauts` AS `num_of_astronauts`,`M`.`payload_volume` AS `payload_volume`,`M`.`payload_weight` AS `payload_weight` from (((`dasak`.`mission` `M` join `dasak`.`mission_accepted_bid` `MAB` on((`M`.`mission_id` = `MAB`.`mission_id`))) join `dasak`.`bid` `BD` on((`MAB`.`bid_id` = `BD`.`bid_id`))) join `dasak`.`bidder` `B` on((`BD`.`bidder_id` = `B`.`id`)))
