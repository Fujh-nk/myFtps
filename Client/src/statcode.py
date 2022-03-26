# USER_OP
USER_REG_REQ = 110          # 用户注册请求
USER_LOGIN_REQ = 111        # 用户登陆请求
USER_LOGOUT_REQ = 112       # 用户登出请求
USER_DEL_REQ = 113          # 用户账号销毁请求


# FILE_OP
FILE_META = 120             # 文件元数据
FILE_CONT = 121             # 文件内容
FILE_DOWNLOAD_REQ = 122     # 文件下载请求
FILE_UPLOAD_REQ = 123       # 文件上传请求
FILE_DEL_REQ = 124          # 文件删除请求


# DIR_OP
DIR_LIST = 130              # 目录内容
DIR_REQ = 131               # 目录请求
DIR_CREATE_REQ = 132        # 目录创建请求
DIR_DEL_REQ = 133           # 目录删除请求


# SERVER_OP
SERVER_REJ = 404            # 服务器拒绝服务（权限不够等情况）
SERVER_ERR = 400            # 服务器因其他原因未完成请求
SERVER_OK = 200             # 服务器完成请求并响应
