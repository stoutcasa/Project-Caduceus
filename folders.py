import os

#base_path = 'Project_Caduceus' for new root folder
subfolder_names = ['infrastructure', 'ansible', 'scripts', 'data', 'docs']

for name in subfolder_names:
    #os.makedirs(os.path.join(base_path, name), exist_ok=True)
    os.makedirs(os.path.join(name), exist_ok=True)