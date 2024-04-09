TYPE=VIEW
query=select `A`.`id` AS `astronaut_id`,count(`MAB`.`mission_id`) AS `experience`,(sum(`M`.`duration`) / `A`.`years_of_experience`) AS `performance` from (((`dasak`.`astronaut` `A` join `dasak`.`bid_has_astronaut` `BHA` on((`A`.`id` = `BHA`.`id`))) join `dasak`.`mission_accepted_bid` `MAB` on((`BHA`.`bid_id` = `MAB`.`bid_id`))) join `dasak`.`mission` `M` on((`MAB`.`mission_id` = `M`.`mission_id`))) where ((`M`.`launch_date` + interval `M`.`duration` day) >= curdate()) group by `A`.`id`
md5=e24a8a86f5487409bdb2e58f32284eda
updatable=0
algorithm=0
definer_user=root
definer_host=localhost
suid=2
with_check_option=0
timestamp=2024-04-09 11:25:04
create-version=1
source=SELECT \n    A.id AS astronaut_id,\n    COUNT(MAB.mission_id) AS experience,\n    SUM(M.duration) / A.years_of_experience AS performance\nFROM \n    Astronaut A\nJOIN \n    Bid_Has_Astronaut BHA ON A.id = BHA.id\nJOIN \n    Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id\nJOIN \n    Mission M ON MAB.mission_id = M.mission_id\nWHERE \n    DATE_ADD(M.launch_date, INTERVAL M.duration DAY) >= CURDATE()\nGROUP BY \n    A.id
client_cs_name=latin1
connection_cl_name=latin1_swedish_ci
view_body_utf8=select `A`.`id` AS `astronaut_id`,count(`MAB`.`mission_id`) AS `experience`,(sum(`M`.`duration`) / `A`.`years_of_experience`) AS `performance` from (((`dasak`.`astronaut` `A` join `dasak`.`bid_has_astronaut` `BHA` on((`A`.`id` = `BHA`.`id`))) join `dasak`.`mission_accepted_bid` `MAB` on((`BHA`.`bid_id` = `MAB`.`bid_id`))) join `dasak`.`mission` `M` on((`MAB`.`mission_id` = `M`.`mission_id`))) where ((`M`.`launch_date` + interval `M`.`duration` day) >= curdate()) group by `A`.`id`
