import pickle
import argparse
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pathlib import Path
from os import chdir


def create_gauth(auth_pickle_file, save=True):
    # authenticate user
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    # store GoogleAuth object in a pickle file to reuse it in the future
    if save:
        with open(auth_pickle_file, 'wb') as f_out:
            pickle.dump(gauth, f_out)
    
    return gauth


def create_folder(path):
    Path('{}'.format(path)).mkdir(parents=True, exist_ok=True)


def recursive_download(drive, folder):
    # create subfolder
    create_folder(folder['title'])

    # cd in subfolder
    chdir(folder['title'])

    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder['id'])}).GetList()

    for item in file_list:
        if item['mimeType'] == 'application/vnd.google-apps.folder':

            recursive_download(drive, item)
        else:
            item.GetContentFile(item['title'])
    
    # return to parent directory
    chdir('..')


def download_folder(folder_id, auth_pickle_file):
    # check if gauth pickle file exists else create it
    if Path(auth_pickle_file).exists():
        with open(auth_pickle_file, 'rb') as f_in:
            gauth = pickle.load(f_in)
    else:
        # else create one
        gauth = create_gauth(auth_pickle_file, True)

    # init drive instance
    drive = GoogleDrive(gauth)

    # get folder name from id
    target_folder = drive.CreateFile({'id': folder_id})

    # create folder
    create_folder(target_folder['title'])
    chdir(target_folder['title'])

    # iterate through all items of the target folder
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()

    for i, item in enumerate(sorted(file_list, key = lambda x: x['title']), start=1):
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            print('Downloading folder {} from GDrive ({}/{})'.format(item['title'], i, len(file_list)))
            
            # if found sub folder download its content
            recursive_download(drive, item)
        else:
            print('Downloading file {} from GDrive ({}/{})'.format(item['title'], i, len(file_list)))
            item.GetContentFile(item['title'])
    
    chdir('..')


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description='GDrive folder downloader')

    parser.add_argument('--folder_id', help='ID of folder in Google Drive', type=str, required=True)
    parser.add_argument('--auth_pickle_file', help='User authentication using pickled authentication object', type=str, default='gauth.pickle')

    return parser.parse_args()

    
if __name__ == "__main__":
    args = parse_command_line_arguments()
    
    download_folder(args.folder_id, args.auth_pickle_file)
