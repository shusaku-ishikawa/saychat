set /P NAME="ファイル名に使用する氏名を入力してください："
set /P TODAY="ファイル名に使用する今日の日付をyyyymmddで入力してください："
set /P USER="検索対象外のキャッシュフォルダを特定するため、PCログイン時のユーザ名を入力してください："

cd c:\

dir *.doc? *.xls? *.ppt? *.pdf *.txt *.xsd? *.mdb? *.zip *.lzh *.csv /s /b > tmporary.txt

find /V "C:\Users\"%USER%"\AppData" tmporary.txt > tmporary2.txt
find /V "C:\Users\"%USER%"\OneDrive - Nihon Unisys, Ltd" tmporary2.txt > tmporary.txt
find /V "C:\Windows\ServiceProfiles\LocalService\AppData" tmporary.txt > %NAME%_%TODAY%.txt

del tmporary.txt

del tmporary2.txt

/
