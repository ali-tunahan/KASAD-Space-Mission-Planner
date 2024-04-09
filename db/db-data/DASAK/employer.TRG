TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER AfterEmployerDeleted\nAFTER DELETE ON Employer\nFOR EACH ROW\nBEGIN\n    DELETE FROM Mission WHERE employer_id = OLD.id;\nEND'
sql_modes=1436549152
definers='root@localhost'
client_cs_names='latin1'
connection_cl_names='latin1_swedish_ci'
db_cl_names='latin1_swedish_ci'
created=171266204815
