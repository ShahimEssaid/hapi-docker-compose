This folder represent a package of content that can be loaded with the "loaders" approach from previous work. The idea is that this folder gets updated, as needed, with new loaders and content and then the directory (the "loders" folder) gets zipped as file to be used by end user on an instance of tims-ts to load the content.

Few key points:
1. The "loaders" directory has subdirectories, one per loader.
2. Each loader loads some specific content (up to us to decided how granular we want to be with this).
3. A loader directory can be turned off if the end user does not want that content loaded.
3. When a new set of loaders is ready for a "release", the "loaders" directory is zipped and the zip file is given a name or version that is descriptive.
4. The zip files are in Google Drive and we manage access to these zip files with Google access control.
5. A user that would like to use our tims-ts HAPI set up AND load some TIMS content, will setup an instance of tims-ts, obtain the zip file for the content they have access to, and unzip to the tims-ts instance directory.
6. A user can then further refine which loaders they want to use (default is use) by suffixing the loader directory with -off to diable that loader.
7. A reset of the tims-ts will load all available and not disabled loaders.


Thi is Base dependnet until a Python command is written to do this same task in a more OS independent way.
