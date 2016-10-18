readme.txt

-My project is a graphical user interface to build networks (a variation of
mathematical graphs) and to get particular metrics off those networks.

Installation Process:
1. The user first needs to install BeautifulSoup4 and numpy. To download numpy,
one should download the universal binary package (available here: 
http://sourceforge.net/projects/numpy/files/OldFiles/1.4.0rc2/ , labeled as
numpy-1.4.0rc2.zip) and run setup.py in the immediate folder to set up the
package. To install BeautifulSoup4, you can access the tar file (available
here: http://www.crummy.com/software/BeautifulSoup/bs4/download/4.3/ , labeled
as  beautifulsoup4-4.3.2.tar.gz), unzip the tar file, and then run setup.py
in the immediate folder that was unzipped. Alternatively, if you have the pip
install format, you can install both of these packages using the commands in
terminal

sudo pip install numpy

sudo pip install beautifulsoup4

. Note that to use the pip install format, you must download get-pip.py 
(available here: https://bootstrap.pypa.io/get-pip.py) and then in the directory
where get-pip.py is saved, run the terminal command 

python get-pip.py 

(which may require administrative access).

2. Go to the directory "Source_And_Supports".

3. In the folder "For_Running_Term_Project", move all python scripts in this
folder into the immediate directory "Source_And_Supports"

4. In this directory, run the terminal command 

python termProject-GUI.py 

.