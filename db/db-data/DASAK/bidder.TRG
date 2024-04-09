TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER AfterBidderDeleted\nAFTER DELETE ON Bidder\nFOR EACH ROW\nBEGIN\n    DELETE FROM Bid WHERE bidder_id = OLD.id;\nEND'
sql_modes=1436549152
definers='root@localhost'
client_cs_names='latin1'
connection_cl_names='latin1_swedish_ci'
db_cl_names='latin1_swedish_ci'
created=171266202844
