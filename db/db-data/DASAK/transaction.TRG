TYPE=TRIGGERS
triggers='CREATE DEFINER=`root`@`localhost` TRIGGER AfterTransactionInserted\nAFTER INSERT ON Transaction\nFOR EACH ROW\nBEGIN\n    UPDATE Company SET balance = balance + NEW.amount WHERE id = NEW.bidder_id;\n    UPDATE Company SET balance = balance - NEW.amount WHERE id = NEW.employer_id;\n    UPDATE Transaction SET status = \'FINISHED\' WHERE transaction_id = NEW.transaction_id;\nEND'
sql_modes=1436549152
definers='root@localhost'
client_cs_names='latin1'
connection_cl_names='latin1_swedish_ci'
db_cl_names='latin1_swedish_ci'
created=171266206256
