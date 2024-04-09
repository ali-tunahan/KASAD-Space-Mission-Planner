TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER AfterMissionBidAccepted\nAFTER INSERT ON Mission_Accepted_Bid\nFOR EACH ROW\nBEGIN\n    UPDATE Bid\n    SET status = \'Rejected\'\n    WHERE mission_id = NEW.mission_id AND bid_id != NEW.bid_id;\nEND'
sql_modes=1436549152
definers='root@localhost'
client_cs_names='latin1'
connection_cl_names='latin1_swedish_ci'
db_cl_names='latin1_swedish_ci'
created=171266208214
