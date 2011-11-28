echo "rsync -avP -e ssh build/html/ srossross,clyther@web.sourceforge.net:htdocs/"

rsync -avP -e ssh build/html/ srossross,clyther@web.sourceforge.net:htdocs/ > rsync.log

echo "done. check ./rsync.log for details"
