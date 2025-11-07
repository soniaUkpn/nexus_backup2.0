Flow:

-setup logging
-remove logs older than 30 days
-delete the files from the tmp folder
- get parameters from file if there is a file, otherwise get them manually inserted
- have them on a .env file
- in directory on path /adms_backups/backups/ we want get into the newest directory
	- Copy all files to /storage/amp/scripts/tmp 
	- Verify hashes are the same in both folders
	- Zip the .dmp files to .gz and delete the .dmp
-if copy of files is unsuccessful alert dynatrace - 'Nexus backup copy failed.' and send details to the log file 'saying which stage failed and which files were involved'
-get file hashes into an array
-delete the present files in nexus at  {repo address} + {environment} + {DNO}
-upload files to nexus with {repo address} + {environment} + {DNO}
-check if the file hashes we have in the array also exist in nexus location
-if copy of files is unsuccessful alert dynatrace - 'Nexus backup copy failed.' and send details to the log file 'saying which stage failed and which files were involved'
-print to log file 'backups successfully executed'
-delete the files from the tmp folder<img width="880" height="565" alt="image" src="https://github.com/user-attachments/assets/99ccd57f-d90c-4181-b732-32a953199ee2" />
