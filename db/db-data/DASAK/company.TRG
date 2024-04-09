TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER CheckCompanyPersonIdBeforeInsert\nBEFORE INSERT ON Company\nFOR EACH ROW\nBEGIN\n    IF EXISTS (SELECT 1 FROM Person WHERE id = NEW.id) THEN\n        SIGNAL SQLSTATE \'45000\' SET MESSAGE_TEXT = \'The same id exists in Person table.\';\n    END IF;\nEND'
sql_modes=1436549152
definers='root@localhost'
client_cs_names='latin1'
connection_cl_names='latin1_swedish_ci'
db_cl_names='latin1_swedish_ci'
created=171266199689
