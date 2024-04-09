TYPE=VIEW
query=select `A`.`id` AS `astronaut_id`,`M`.`mission_id` AS `mission_id`,`M`.`employer_id` AS `employer_id`,`M`.`title` AS `title`,`M`.`description` AS `description`,`M`.`objectives` AS `objectives`,`M`.`launch_date` AS `launch_date`,`M`.`duration` AS `duration`,`M`.`num_of_astronauts` AS `num_of_astronauts`,`M`.`payload_volume` AS `payload_volume`,`M`.`payload_weight` AS `payload_weight` from (((`dasak`.`astronaut` `A` join `dasak`.`bid_has_astronaut` `BHA` on((`A`.`id` = `BHA`.`id`))) join `dasak`.`mission_accepted_bid` `MAB` on((`BHA`.`bid_id` = `MAB`.`bid_id`))) join `dasak`.`mission` `M` on((`MAB`.`mission_id` = `M`.`mission_id`)))
md5=d2b46046c168ba95901f6d718a8aba8d
updatable=1
algorithm=0
definer_user=root
definer_host=localhost
suid=2
with_check_option=0
timestamp=2024-04-09 11:24:17
create-version=1
source=SELECT \n    A.id AS astronaut_id,\n    M.mission_id,\n    M.employer_id,\n    M.title,\n    M.description,\n    M.objectives,\n    M.launch_date,\n    M.duration,\n    M.num_of_astronauts,\n    M.payload_volume,\n    M.payload_weight\nFROM \n    Astronaut A\nJOIN \n    Bid_Has_Astronaut BHA ON A.id = BHA.id\nJOIN \n    Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id\nJOIN \n    Mission M ON MAB.mission_id = M.mission_id
client_cs_name=latin1
connection_cl_name=latin1_swedish_ci
view_body_utf8=select `A`.`id` AS `astronaut_id`,`M`.`mission_id` AS `mission_id`,`M`.`employer_id` AS `employer_id`,`M`.`title` AS `title`,`M`.`description` AS `description`,`M`.`objectives` AS `objectives`,`M`.`launch_date` AS `launch_date`,`M`.`duration` AS `duration`,`M`.`num_of_astronauts` AS `num_of_astronauts`,`M`.`payload_volume` AS `payload_volume`,`M`.`payload_weight` AS `payload_weight` from (((`dasak`.`astronaut` `A` join `dasak`.`bid_has_astronaut` `BHA` on((`A`.`id` = `BHA`.`id`))) join `dasak`.`mission_accepted_bid` `MAB` on((`BHA`.`bid_id` = `MAB`.`bid_id`))) join `dasak`.`mission` `M` on((`MAB`.`mission_id` = `M`.`mission_id`)))
