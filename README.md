Flow:

1. setup logging - done
2. remove logs older than 30 days - done
3. delete the files from the tmp folder - done
4. get parameters from file if there is a file, otherwise get them manually inserted - done
5. have them on a .env file - done
6. 
7. in directory on path /adms_backups/backups/ we want to get into the newest directory
	- Copy all files to /storage/amp/scripts/tmp 
	- Verify hashes are the same in both folders
	- Zip the .dmp files to .gz and delete the .dmp
8. if copy of files is unsuccessful alert dynatrace - 'Nexus backup copy failed.' and send details to the log file 'saying which stage failed and which files were involved'
9. get file hashes into an array
10. delete the present files in nexus at  {repo address} + {environment} + {DNO}
11. upload files to nexus with {repo address} + {environment} + {DNO}
12. check if the file hashes we have in the array also exist in nexus location
13. if copy of files is unsuccessful alert dynatrace - 'Nexus backup copy failed.' and send details to the log file 'saying which stage failed and which files were involved'
14. print to log file 'backups successfully executed'
15. delete the files from the tmp folder<img width="880" height="565" alt="image" src="https://github.com/user-attachments/assets/99ccd57f-d90c-4181-b732-32a953199ee2" />
