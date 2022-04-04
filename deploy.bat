python -m pip install --upgrade pip;
pip install pywin32;
pip install PyQt5;
pip install DBUtils;
IF [NOT] EXIST cert.pem set var=1
IF [NOT] EXIST key.pem set var=1
IF DEFINED var (
openssl req -newkey rsa:1024 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
)