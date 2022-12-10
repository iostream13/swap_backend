## TÍNH NĂNG
- Người dùng có thể tạo tài khoản, chỉnh sửa thông tin tài khoản như ngày sinh, giới tính, sđt, email, bio.
- Người dùng có thể nạp token hoặc rút token ra khỏi ví.
- Người dùng có thể chuyển đổi giữa các loại token với nhau.

## Mô hình cơ sở dữ liệu

![alt text](https://cdn.discordapp.com/attachments/703442047469617273/1051105343326928916/bakaswap_diagram.png)

## Cấu trúc code: 
### main
- main.py: file main xây dựng FastAPI service, định nghĩa cấu trúc các API
### sql_app
- crud.py : Định nghĩa các method (read,write) để kết nối đến MySQL
- database.py : Kết nối MySQL
- models.py: Định nghĩa class object models cho FastAPI
- schemas.py: Định nghĩa lược đồ để làm việc với yêu cầu/phản hồi API cụ thể
