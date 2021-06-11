## GDrive folder downloader

A simple python script to download nested folders from Google Drive. It takes as an input the Google Drive ID of the folder to be downloaded.
It has an optional argument auth_pickle_file which by default searches for a gauth.pickle where authentication object is stored. If such and file doesn't exist it creates one if authentication process is succesful. If the argument is changed it searches/saves a file of the specified name.
