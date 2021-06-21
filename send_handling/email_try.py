import smtplib
server = smtplib.SMTP('smtp.outlook.com', port=587)
server.starttls()
server.login("surreyend@outlook.com", "H45yr!kg!^4@")
message = "Subject: Test Mail\n\n Hello world!"
server.sendmail("surreyend@outlook.com", "f.baird@surrey.ac.uk", message)
server.quit()